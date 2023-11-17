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
from tenants.models import Domain
from .models import ConferenceCentres


class CnfFunctions():

    def __init__(self, domain_uuid, domain_name, cnf_uuid=None, user_name='system'):
        self.domain_uuid = domain_uuid
        self.domain_name = domain_name
        self.user_name = user_name
        self.cnf_uuid = cnf_uuid
        if cnf_uuid:
            try:
                self.cnf = ConferenceCentres.objects.get(pk=cnf_uuid)
            except:
                self.cnf = False
        else:
            self.cnf = False

    def add_dialplan(self):
        d = Domain.objects.get(pk=self.domain_uuid)

        dp = Dialplan.objects.create(
            domain_id=d,
            app_id='da23e762-de58-4c39-b6e5-f3b209a80a16',
            name=self.cnf.name,
            number=self.cnf.extension,
            destination='false',
            context=self.domain_name,
            category='Conference centre',
            dp_continue='false',
            sequence=333,
            enabled=self.cnf.enabled,
            description=self.cnf.description,
            updated_by=self.user_name
        )
        return dp

    def generate_xml(self):
        if not self.cnf:
            return None
        try:
            dp = Dialplan.objects.get(pk=self.cnf.dialplan_id)
        except:
            dp = self.add_dialplan()

        dp.enabled = self.cnf.enabled
        dp.name = self.cnf.name
        dp.number=self.cnf.extension

        x_root = etree.Element("extension", name=dp.name)
        x_root.set('continue', dp.dp_continue)
        x_root.set('uuid', str(dp.id))
        x_condition = etree.SubElement(x_root, "condition", field='destination_number', expression='^%s$' % self.cnf.extension)
        etree.SubElement(x_condition, "action", application='answer', data='')
        etree.SubElement(x_condition, "action", application='sleep', data='1000')
        if self.cnf.greeting:
            etree.SubElement(x_condition, "action", application='playback', data=self.cnf.greeting)
        etree.SubElement(x_condition, "action", application='set', data='conference_uuid=%s' % str(self.cnf.id))
        httapi_url = PbxSettings().default_settings('dialplan', 'httapi_url', 'text', 'http://127.0.0.1:8008', True)[0]
        etree.SubElement(x_condition, "action", application='httapi', data='{httapi_profile=dpbx,url=%s/httapihandler/conference/}' % httapi_url)

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8").replace('&lt;', '<').replace('&gt;', '>')
        dp.xml = xml
        dp.save()
        return dp.id
