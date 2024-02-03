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
from .models import IvrMenus, IvrMenuOptions


class IvrFunctions():

    def __init__(self, ivr=None, user_name='system'):
        self.ivr = ivr
        self.user_name = user_name

    def add_dialplan(self):
        dp = Dialplan.objects.create(
            domain_id=self.ivr.domain_id,
            app_id='6bf14c5d-c76c-4e6f-8782-c62bf7902ea3',
            name=self.ivr.name,
            number=self.ivr.extension,
            destination='false',
            context=self.ivr.domain_id.name,
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
        etree.SubElement(x_condition, "action", application='set', data='presence_id=%s@%s' % (self.ivr.extension, self.ivr.domain_id.name))
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
