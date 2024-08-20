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
from tenants.pbxsettings import PbxSettings
from dialplans.models import Dialplan


class CfFunctions():

    def __init__(self, cf=None, user_name='system'):
        self.cf = cf
        self.user_name = user_name

    def add_dialplan(self):
        dp = Dialplan.objects.create(
            domain_id=self.cf.domain_id,
            app_id='ccf122fd-b0e0-460e-aa48-c7025a18c3e9',
            name=self.cf.name,
            number=self.cf.extension,
            destination='false',
            context=self.cf.domain_id.name,
            category='Call flow',
            dp_continue='false',
            sequence=101,
            enabled='true',
            description=self.cf.description,
            updated_by=self.user_name
        )
        return dp

    def generate_xml(self):
        if not self.cf:
            return None
        try:
            dp = Dialplan.objects.get(pk=self.cf.dialplan_id)
        except:
            dp = self.add_dialplan()

        dp.name = self.cf.name
        dp.number=self.cf.extension
        httapi_url = PbxSettings().default_settings('dialplan', 'httapi_url', 'text', 'http://127.0.0.1:8008', True)

        x_root = etree.Element("extension", name=dp.name)
        x_root.set('continue', dp.dp_continue)
        x_root.set('uuid', str(dp.id))
        x_condition = etree.SubElement(x_root, "condition", field='destination_number', expression='^(?:flow\\+)?%s$' % self.cf.feature_code.replace('*', '\\*'))
        x_condition.set('break', 'on-true')
        etree.SubElement(x_condition, "action", application='answer', data='')
        etree.SubElement(x_condition, "action", application='sleep', data='200')
        etree.SubElement(x_condition, "action", application='set', data='callflow_pin=%s' % self.cf.pin_number)
        etree.SubElement(x_condition, "action", application='set', data='callflow_uuid=%s' % str(self.cf.id))
        etree.SubElement(x_condition, "action", application='httapi', data='{httapi_profile=dpbx,url=%s/httapihandler/callflowtoggle/}' % httapi_url)
        x_condition = etree.SubElement(x_root, "condition", field='destination_number', expression='^%s$' % self.cf.extension)
        etree.SubElement(x_condition, "action", application='set', data='callflow_uuid=%s' % str(self.cf.id))
        if self.cf.status == 'true':
            toa = self.cf.data.split(':')
        else:
            toa = self.cf.alternate_data.split(':')
        if toa[0] == 'hangup':
            etree.SubElement(x_condition, "action", application=toa[0], data='')
        else:
            etree.SubElement(x_condition, "action", application=toa[0], data=toa[1])

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8").replace('&lt;', '<').replace('&gt;', '>')
        dp.xml = xml
        dp.save()
        return dp.id
