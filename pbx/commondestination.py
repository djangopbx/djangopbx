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
from dialplans.models import Dialplan
from accounts.models import Extension, Bridge
from switch.models import SwitchVariable


class CommonDestAction():

    def __init__(self, domain_name, domain_uuid):
        self.domain_uuid = domain_uuid
        self.domain_name = domain_name
        self.sep = ':'

    def decorate(self, text, decorate):
        if decorate:
            return '--- %s ----------' % _(text)
        else:
            return _(text)

    def get_dp_list(self, cat, dest=False):
        d_list = []
        if dest:
            qs = Dialplan.objects.filter(domain_id=uuid.UUID(self.domain_uuid), destination='true',
                enabled='true').order_by('name')
        else:
            qs = Dialplan.objects.filter(domain_id=uuid.UUID(self.domain_uuid), category=cat,
                enabled='true').order_by('name')
        for q in qs:
            d_list.append(('transfer%s%s XML %s' % (self.sep, q.number, self.domain_name), '%s-%s' % (q.name, q.number)))
        return d_list

    def get_action_choices(self, sep=':', decorate=False, opt=65535):
        self.sep = sep
        cd_actions = []
        e_list = []
        v_list = []
        cg_list = []
        es = Extension.objects.select_related('domain_id').prefetch_related('voicemail').filter(
                domain_id=uuid.UUID(self.domain_uuid),
                enabled='true'
                ).order_by('extension')
        for e in es:
            e_list.append(('transfer%s%s XML %s' % (sep, e.extension, e.domain_id), '%s %s' % (
                    e.extension, (e.description if e.description else 'Extension %s' % e.extension))))
            if e.call_group:
                if ',' in e.call_group:
                    call_groups = e.call_group.split(',')
                    for call_group in call_groups:
                        cg_entry = ('bridge%sgroup/%s@%s' % (sep, call_group.strip(), e.domain_id), call_group.strip())
                        if cg_entry not in cg_list:
                            cg_list.append(cg_entry)
                else:
                    cg_entry = ('bridge%sgroup/%s@%s' % (sep, e.call_group, e.domain_id), e.call_group)
                    if cg_entry not in cg_list:
                        cg_list.append(cg_entry)
            v = e.voicemail.filter(enabled='true').first()
            if v:
                v_list.append(
                    ('transfer%s99%s XML %s' % (sep, e.extension, e.domain_id), '%s(VM) %s' % (
                        e.extension, (v.description if v.description else 'Voicemail %s' % e.extension))))
        if opt & 1 == 1:
            d_list = []
            qs = Bridge.objects.filter(domain_id=uuid.UUID(self.domain_uuid), enabled='true').order_by('name')
            for q in qs:
                d_list.append(('bridge%s%s' % (sep, q.destination), q.name))
            if e_list:
                cd_actions.append((self.decorate('Bridges', decorate), d_list))

        # Placeholder: Call Centers
        #if opt & 2 == 2:


        if opt & 4 == 4:
            d_list = self.get_dp_list('Call flows')
            if d_list:
                cd_actions.append((self.decorate('Call flows', decorate), d_list))

        if opt & 8 == 8:
            if cg_list:
                cd_actions.append((self.decorate('Call groups', decorate), cg_list))

        #if opt & 16 == 16:
        # Placeholder: Conferences

        if opt & 32 == 32:
            d_list = self.get_dp_list('N/A', True)
            if d_list:
                cd_actions.append((self.decorate('Dialplans', decorate), d_list))

        if opt & 64 == 64:
            if e_list:
                cd_actions.append((self.decorate('Extensions', decorate), e_list))

        if opt & 128 == 128:
            d_list = self.get_dp_list('IVR menu')
            if d_list:
                cd_actions.append((self.decorate('IVR menus', decorate), d_list))

        #if opt & 256 == 256:
        # Placeholder: Recordings - needs httapi handler

        if opt & 512 == 512:
            d_list = self.get_dp_list('Ring group')
            if d_list:
                cd_actions.append((self.decorate('Ring groups', decorate), d_list))

        if opt & 1024 == 1024:
            d_list = self.get_dp_list('Time condition')
            if d_list:
                cd_actions.append((self.decorate('Time Conditions', decorate), d_list))

        if opt & 2048 == 2048:
            if v_list:
                cd_actions.append((self.decorate('Voicemails', decorate), v_list))

        if opt & 4096 == 4096:
            t_list = []
            sv = SwitchVariable.objects.filter(category='Tones', enabled='true').order_by('name')
            for t in sv:
                t_list.append(('playback:tone_stream://%s' % t.value, t.name))

            if len(t_list) > 0:
                cd_actions.append((self.decorate('Tones', decorate), t_list))

        if opt & 8192 == 8192:
            o_list = []
            o_list.append(('transfer%s98 XML %s' % (sep, self.domain_name), _('Check Voicemail')))
            o_list.append(('transfer%s411 XML %s' % (sep, self.domain_name), _('Company Directory')))
            o_list.append(('transfer%s732 XML %s' % (sep, self.domain_name), _('Record')))
            if opt & 16384 == 16384:
                o_list.append(('hangup', _('Hangup')))
            cd_actions.append((self.decorate('Other', decorate), o_list))

        return cd_actions
