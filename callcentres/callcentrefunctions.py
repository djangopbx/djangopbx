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
#from tenants.pbxsettings import PbxSettings
from dialplans.models import Dialplan


class CcFunctions():

    def __init__(self, cc=None, user_name='system'):
        self.cc = cc
        self.user_name = user_name

    def add_dialplan(self):
        dp = Dialplan.objects.create(
            domain_id=self.cc.domain_id,
            app_id='48b0bd79-021d-4151-b59e-06370fc686cd',
            name=self.cc.name,
            number=self.cc.extension,
            destination='false',
            context=self.cc.domain_id.name,
            category='Call centre',
            dp_continue='false',
            sequence=230,
            enabled='true',
            description=self.cc.description,
            updated_by=self.user_name
        )
        return dp

    def generate_xml(self):
        if not self.cc:
            return None
        try:
            dp = Dialplan.objects.get(pk=self.cc.dialplan_id)
        except:
            dp = self.add_dialplan()

        dp.name = self.cc.name
        dp.number=self.cc.extension

        x_root = etree.Element("extension", name=dp.name)
        x_root.set('continue', dp.dp_continue)
        x_root.set('uuid', str(dp.id))

        # Group 1
        x_condition = etree.SubElement(x_root, "condition", field='destination_number', expression='^([^#]+#)(.*)$')
        x_condition.set('break', 'never')
        etree.SubElement(x_condition, "action", application='set', data='caller_id_name=$2')

        # Group 2
        x_condition = etree.SubElement(x_root, "condition", field='destination_number', expression='^%s$' % self.cc.extension)
        etree.SubElement(x_condition, "action", application='answer', data='')
        etree.SubElement(x_condition, "action", application='set', data='hangup_after_bridge=true')
        if self.cc.greeting:
            etree.SubElement(x_condition, "action", application='playback', data=self.cc.greeting)
        etree.SubElement(x_condition, "action", application='callcenter', data=str(self.cc.id))
        toa = self.cc.timeout_action.split(':')
        if toa[0] == 'hangup':
            etree.SubElement(x_condition, "action", application=toa[0], data='')
        else:
            etree.SubElement(x_condition, "action", application=toa[0], data=toa[1])

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8").replace('&lt;', '<').replace('&gt;', '>')
        dp.xml = xml
        dp.save()
        return dp.id
