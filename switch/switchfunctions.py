#
#    DjangoPBX
#
#    MIT License
#
#    Copyright (c) 2016 - 2022 Adrian Fretwell <adrian@djangopbx.com>
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

import os
import uuid
import socket
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from lxml import etree
from io import StringIO
import switch.models
from tenants.pbxsettings import PbxSettings

class SwitchFunctions():
    def import_sip_profiles(self, profile_remove = False):
        path_of_xml = settings.BASE_DIR / 'switch/resources/templates/conf/sip_profiles'
        ext = ('.xml.noload')
        for files in os.listdir(path_of_xml):
            if files.endswith(ext):
                with open(path_of_xml / files) as f:
                    xml = f.read()

                self.create_sip_profile_from_xml(xml, profile_remove)
            else:
                continue


    def create_sip_profile_from_xml(self, xml, profile_remove = False):
        parser = etree.XMLParser(remove_comments=True)
        tree   = etree.parse(StringIO(xml), parser)
        root = tree.getroot()

        if not etree.iselement(root):
            return False

        if len(root):  # check root has children

            sip_profile_name = root.get('name', 'noname')
            if sip_profile_name == 'noname':
                return False
            sip_profile_enabled = root.get('enabled', 'true')
            sip_profile_local_enabled = 'true'


            sip_profile_description = ''

            if sip_profile_name == 'internal':
                sip_profile_description = 'The Internal profile by default requires registration which is used by the endpoints. By default the Internal profile binds to port 5060.'

            if sip_profile_name == 'internal-ipv6':
                sip_profile_description = 'The Internal IPV6 profile binds to the IP version 6 address and is similar to the Internal profile.'
                sip_profile_local_enabled = 'false'

            if sip_profile_name == 'external':
                sip_profile_description = 'The External profile external provides anonymous calling in the public context. By default the External profile binds to port 5080. Calls can be sent using a SIP URL:voip.domain.com:5080'

            if sip_profile_name == 'external-ipv6':
                sip_profile_description = 'The External IPV6 profile binds to the IP version 6 address and is similar to the External profile.'
                sip_profile_local_enabled = 'false'

            if sip_profile_name == 'lan':
                sip_profile_description = 'The LAN profile is the same as the Internal profile except that it is bound to the LAN IP.'
                sip_profile_local_enabled = 'false'

            if not sip_profile_enabled == 'false':

                if profile_remove:
                    self.sip_profile_remove(sip_profile_name)
                else:
                    if self.sip_profile_exists(sip_profile_name):
                        return False

                sp = switch.models.SipProfile(
                    name = sip_profile_name,
                    enabled = sip_profile_local_enabled,
                    description = sip_profile_description
                )
                sp.save()

                for ele in root:
                    if ele.tag == 'domains':
                        if len(ele):  # check element has children
                            for domain in ele:
                                self.sip_profile_domain_add(sp, domain.get('name'), domain.get('alias'), domain.get('parse'))

                    if ele.tag == 'settings':
                        if len(ele):  # check element has children
                            for setting in ele:
                                self.sip_profile_setting_add(sp, setting.get('name'), setting.get('value'), setting.get('enabled', 'true'), setting.get('description', ''))



    def sip_profile_domain_add(self, sp, dname, dalias, dparse):
        switch.models.SipProfileDomain.objects.create(
            sip_profile_id = sp,
            name = dname,
            alias = dalias,
            parse = dparse
        )


    def sip_profile_setting_add(self, sp, sname, svalue, senabled, sdesc):
        switch.models.SipProfileSetting.objects.create(
            sip_profile_id = sp,
            name = sname,
            value = svalue,
            enabled = senabled,
            description = sdesc
        )

    def sip_profile_exists(self, sp_name):
        return switch.models.SipProfile.objects.filter(name = sp_name).exists()

    def sip_profile_remove(self, sp_name):
        switch.models.SipProfile.objects.filter(name = sp_name).delete()
        return True

    def import_vars(self, var_remove = False):
        path_of_xml = settings.BASE_DIR / 'switch/resources/templates/conf/vars.xml'
        with open(path_of_xml) as f:
            xml = f.read()
            self.create_var_from_xml(xml, var_remove)


    def create_var_from_xml(self, xml, profile_remove = False):
        parser = etree.XMLParser(remove_comments=True)
        tree   = etree.parse(StringIO(xml), parser)
        root = tree.getroot()

        if not etree.iselement(root):
            return False

        if len(root):  # check root has children

            vorder = 10
            for ele in root:
                if ele.tag == 'X-PRE-PROCESS':
                    data = ele.get('data').split('=', 1)
                    self.var_add(ele.get('category'), data[0], data[1], ele.get('cmd'), ele.get('enabled'), vorder)
                    vorder += 10


    def var_add(self, vcat, vname, vvalue, vcmd, venabled, vorder):
        switch.models.SwitchVariable.objects.create(
            category = vcat,
            name = vname,
            value = vvalue,
            command = vcmd,
            enabled = venabled,
            sequence = vorder
        )


    def save_var_xml(self):
        vlist = switch.models.SwitchVariable.objects.filter(enabled = 'true').order_by('category', 'sequence')
        xml = ''
        prev_var_cat = ''
        hostname = socket.gethostname()

        switchconflist = PbxSettings().default_settings('switch', 'conf', 'dir')
        if switchconflist:
            switchconfdir = switchconflist[0]
            for v in vlist:
                if not v.category == 'Provision':
                    if not prev_var_cat == v.category:
                        xml += "\n<!-- " + v.category + " -->\n"
                        if not v.description == None:
                            if len(v.description) > 0:
                                xml += "\n<!-- " + v.category + " -->\n"

                    cmd = v.command
                    if len(cmd) == 0:
                        cmd = 'set'
                    if cmd == 'Exec-Set':
                        cmd = 'exec-set'
                    if v.hostname:
                        if len(v.hostname) == 0:
                            xml += "<X-PRE-PROCESS cmd=\"" + v.command + "\" data=\"" + v.name + "=" + v.value + "\" />\n"
                        elif v.hostname == hostname:
                            xml += "<X-PRE-PROCESS cmd=\"" + v.command + "\" data=\"" + v.name + "=" + v.value + "\" />\n"
                    else:
                        xml += "<X-PRE-PROCESS cmd=\"" + v.command + "\" data=\"" + v.name + "=" + v.value + "\" />\n"

                    prev_var_cat = v.category

#                xml += "\n"

            if os.path.exists(switchconfdir):
                f = open(switchconfdir + '/vars.xml', 'w')
                f.write(xml)
                f.close()
                return 0
            else:
                return 2

        else:
            return 1
