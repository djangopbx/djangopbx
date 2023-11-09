#    DjangoPBX
#
#    MIT License
#
#    Copyright (c) 2016 - 2023 Adrian Fretwell <adrian@djangopbx.com>
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#    SOFTWARE.
#
#    Contributor(s):
#    Adrian Fretwell <adrian@djangopbx.com>
#

import uuid
from django.utils.translation import gettext_lazy as _
from lxml import etree
from dialplans.models import Dialplan
from tenants.models import Domain
from accounts.models import Extension, FollowMeDestination
from .models import IvrMenus, IvrMenuOptions
from switch.models import SwitchVariable


class IvrDestAction():

    def __init__(self, domain_name, domain_uuid):
        self.domain_uuid = domain_uuid
        self.domain_name = domain_name

    def decorate(self, text, decorate):
        if decorate:
            return '--- %s ----------' % _(text)
        else:
            return _(text)

    def get_ivr_action_choices(self, sep=':', decorate=False):
        ivr_actions = []
        e_list = []
        v_list = []
        es = Extension.objects.select_related('domain_id').prefetch_related('voicemail').filter(
                domain_id=uuid.UUID(self.domain_uuid),
                enabled='true'
                ).order_by('extension')
        for e in es:
            e_list.append(('transfer%s%s XML %s' % (sep, e.extension, e.domain_id), '%s %s' % (e.extension, e.description)))
            v = e.voicemail.filter(enabled='true').first()
            if v:
                v_list.append(
                    ('transfer%s99%s XML %s' % (sep, e.extension, e.domain_id), '%s(VM) %s' % (e.extension, e.description))
                    )

        if len(e_list) > 0:
            ivr_actions.append((self.decorate('Extensions', decorate), e_list))
        if len(v_list) > 0:
            ivr_actions.append((self.decorate('Voicemails', decorate), v_list))

        rg_list = []
        rgs = Dialplan.objects.filter(domain_id=uuid.UUID(self.domain_uuid),
                category='Ring group',
                enabled='true'
                ).order_by('name')
        for rg in rgs:
            rg_list.append(('transfer%s%s XML %s' % (sep, rg.number, self.domain_name), '%s-%s' % (rg.name, rg.number)))

        if len(rg_list) > 0:
            ivr_actions.append((self.decorate('Ring groups', decorate), rg_list))

        ivr_list = []
        ivrs = Dialplan.objects.filter(domain_id=uuid.UUID(self.domain_uuid),
                category='IVR menu',
                enabled='true'
                ).order_by('name')
        for ivr in ivrs:
            ivr_list.append(('transfer%s%s XML %s' % (sep, ivr.number, self.domain_name), '%s-%s' % (ivr.name, ivr.number)))

        if len(ivr_list) > 0:
            ivr_actions.append((self.decorate('IVR menus', decorate), ivr_list))

        t_list = []
        sv = SwitchVariable.objects.filter(category='Tones', enabled='true').order_by('name')
        for t in sv:
            t_list.append(('playback%stone_stream://%s' % (sep, t.value), t.name))

        if len(t_list) > 0:
            ivr_actions.append((self.decorate('Tones', decorate), t_list))

        o_list = []
        o_list.append(('transfer%s98 XML %s' % (sep, self.domain_name), _('Check Voicemail')))
        o_list.append(('transfer%s411 XML %s' % (sep,  self.domain_name), _('Company Directory')))
        o_list.append(('transfer%s732 XML %s' % (sep, self.domain_name), _('Record')))
        o_list.append(('hangup', _('Hangup')))
        ivr_actions.append((self.decorate('Other', decorate), o_list))

        return ivr_actions

# may not need below
class IvrFunctions():

    def __init__(self, domain_uuid, domain_name, ivr_uuid=None, user_name='system'):
        self.domain_uuid = domain_uuid
        self.domain_name = domain_name
        self.user_name = user_name
        self.ivr_uuid = ivr_uuid
        if ivr_uuid:
            try:
                self.ivr = IvrMenus.objects.get(pk=ivr_uuid)
            except:
                self.ivr = False
        else:
            self.ivr = False

    def add_dialplan(self):
        d = Domain.objects.get(pk=self.domain_uuid)

        dp = Dialplan.objects.create(
            domain_id=d,
            app_id='6bf14c5d-c76c-4e6f-8782-c62bf7902ea3',
            name=self.ivr.name,
            number=self.ivr.extension,
            destination='true',
            context=self.domain_name,
            category='IVR menu',
            dp_continue='false',
            sequence=101,
            enabled=self.ivr.enabled,
            description=self.ivr.description,
            updated_by=self.user_name
        )
        return dp

    def generate_xml(self):
        if not self.ivr:
            return None
        try:
            dp = Dialplan.objects.get(pk=self.ivr.dialplan_id)
        except:
            dp = self.add_dialplan()

        dp.enabled = self.ivr.enabled
        dp.name = self.ivr.name
        dp.number=self.ivr.extension

        x_root = etree.Element("extension", name=dp.name)
        x_root.set('continue', dp.dp_continue)
        x_root.set('uuid', str(dp.id))
        x_condition = etree.SubElement(x_root, "condition", field='destination_number', expression='^%s$' % self.ivr.extension)
        etree.SubElement(x_condition, "action", application='ring_ready', data='')
        etree.SubElement(x_condition, "action", application='answer', data='')
        etree.SubElement(x_condition, "action", application='sleep', data='1000')
        etree.SubElement(x_condition, "action", application='set', data='hangup_after_bridge=true')
        etree.SubElement(x_condition, "action", application='set', data='ring_back=%s' % self.ivr.ringback)
        etree.SubElement(x_condition, "action", application='set', data='presence_id=%s@%s' % (self.ivr.extension, self.domain_name))
        lang = self.ivr.language.split('/')
        etree.SubElement(x_condition, "action", application='set', data='default_language=%s' % lang[0])
        etree.SubElement(x_condition, "action", application='set', data='default_dialect=%s' % lang[1])
        etree.SubElement(x_condition, "action", application='set', data='default_voice=%s' % lang[2])
        etree.SubElement(x_condition, "action", application='set', data='transfer_ring_back=%s' % self.ivr.ringback)
        etree.SubElement(x_condition, "action", application='set', data='ivr_menu_uuid=%s' % str(self.ivr.id))
        etree.SubElement(x_condition, "action", application='ivr', data=str(self.ivr.id))
        etree.SubElement(x_condition, "action", application='hangup', data='')

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8").replace('&lt;', '<').replace('&gt;', '>')
        dp.xml = xml
        dp.save()
        return dp.id
