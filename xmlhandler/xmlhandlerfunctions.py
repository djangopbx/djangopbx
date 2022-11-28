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

from django.core.cache import cache
from lxml import etree
from django.db.models import Q
from dialplans.models import Dialplan
from accounts.models import Extension, ExtensionUser, FollowMeDestination
from voicemail.models import Voicemail



class XmlHandlerFunctions():

    def NotFoundXml(self):
        return '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<document type="freeswitch/xml">
  <section name="result">
    <result status="not found" />
  </section>
</document>
'''

    def NotFoundPublic(self, xml_list):
        xml_list.append('''<extension name="not-found" continue="false" uuid="9913df49-0757-414b-8cf9-bcae2fd81ae7">
  <condition field="" expression="">
    <action application="set" data="call_direction=inbound" inline="true"/>
    <action application="log" data="WARNING [inbound routes] 404 not found ${sip_network_ip}" inline="true"/>
  </condition>
</extension>
''')
        return xml_list


    def XmlHeader(self, name, context):
        xml = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<document type="freeswitch/xml">
    <section name="{}" description="">
        <context name="{}">
'''
        return xml.format(name, context)


    def XmlFooter(self):
        return '''    </context>
  </section>
</document>
'''

    def DirectoryAddDomain(self, domain, x_section, params = True, variables = True):
        x_domain = etree.SubElement(x_section, "domain", name=domain)
        if params:
            x_params = etree.SubElement(x_domain, "params")
            etree.SubElement(x_params, "param", name='jsonrpc-allowed-methods', value='verto')
            etree.SubElement(x_params, "param", name='jsonrpc-allowed-event-channels', value='demo,conference,presence')
        if variables:
            x_variables = etree.SubElement(x_domain, "variables")
            etree.SubElement(x_variables, "variable", name='default_language', value='$${default_language}')
            etree.SubElement(x_variables, "variable", name='default_dialect', value='$${default_dialect}')
        x_groups = etree.SubElement(x_domain, "groups")
        x_group = etree.SubElement(x_groups, "group", name='default')
        x_users = etree.SubElement(x_group, "users")
        return x_users


    def DirectoryAddUserAcl(self, domain, x_users, e):
        x_user =  etree.SubElement(x_users, "user", id=e.extension)
        if e.cidr:
            x_user.set("cidr", e.cidr)
        return

    def DirectoryAddUser(self, domain, user, number_as_presence_id, x_users, e, eu, v, cacheable):
        flag_vm_enabled = True
        vm_enabled = 'true'
        if v == None:
            flag_vm_enabled = False
            vm_enabled = 'false'

        presence_id = '%s@%s' % (e.extension, domain)
        if number_as_presence_id:
            presence_id = '%s@%s' % (e.number_alias, domain)

        destination = '%s@%s' % (e.extension, domain)

        if e.dial_string:
            dial_string = e.dial_string
        else:
            dial_string = '{sip_invite_domain=%s,presence_id=%s}${sofia_contact(%s)}' % (domain, presence_id, destination)

        x_user =  etree.SubElement(x_users, "user", id=user)
        if cacheable:
            x_user.set("cacheable", '60000')

        if e.cidr:
            x_user.set("cidr", e.cidr)

        sip_from_number = e.extension
        if e.number_alias:
            x_user.set("number-alias", e.number_alias)
            sip_from_number = e.number_alias

        x_params = etree.SubElement(x_user, "params")
        etree.SubElement(x_params, "param", name='password', value=e.password)
        etree.SubElement(x_params, "param", name='vm-enabled', value=vm_enabled)
        if flag_vm_enabled:
            etree.SubElement(x_params, "param", name='vm-password', value=v.password)
            if v.mail_to:
                etree.SubElement(x_params, "param", name='vm-email-all-messages', value=vm_enabled)
                etree.SubElement(x_params, "param", name='vm-attach-file', value=v.attach_file)
                etree.SubElement(x_params, "param", name='vm-keep-local-after-email', value=v.local_after_email)
                etree.SubElement(x_params, "param", name='vm-mailto', value=v.mail_to)
        if e.mwi_account:
            etree.SubElement(x_params, "param", name='MWI-Account', value=e.mwi_account)
        if e.auth_acl:
            etree.SubElement(x_params, "param", name='auth-acl', value=e.auth_acl)
        etree.SubElement(x_params, "param", name='dial-string', value=dial_string)
        etree.SubElement(x_params, "param", name='verto-context', value=domain)
        etree.SubElement(x_params, "param", name='verto-dialplan', value='XML')
        #etree.SubElement(x_params, "param", name='jsonrpc-allowed-methods', value='verto')
        #etree.SubElement(x_params, "param", name='jsonrpc-allowed-event-channels', value='demo,conference,presence')
        x_variables = etree.SubElement(x_user, "variables")


        etree.SubElement(x_variables, "variable", name='domain_uuid', value=str(e.domain_id.id))
        etree.SubElement(x_variables, "variable", name='domain_name', value=domain)
        etree.SubElement(x_variables, "variable", name='extension_uuid', value=str(e.id))
        if eu:
            etree.SubElement(x_variables, "variable", name='user_uuid', value=str(eu.user_uuid.user_uuid))
            etree.SubElement(x_variables, "variable", name='user_name', value=str(eu.user_uuid))

        etree.SubElement(x_variables, "variable", name='call_timeout', value=str(e.call_timeout))
        etree.SubElement(x_variables, "variable", name='caller_id_name', value=e.extension)
        etree.SubElement(x_variables, "variable", name='caller_id_number', value=sip_from_number)

        etree.SubElement(x_variables, "variable", name='presence_id', value=presence_id)

        if e.call_group:
            etree.SubElement(x_variables, "variable", name='call_group', value=e.call_group)
        etree.SubElement(x_variables, "variable", name='call_screen_enabled', value=e.call_screen_enabled)
        if e.user_record:
            etree.SubElement(x_variables, "variable", name='user_record', value=e.user_record)
        if e.hold_music:
            etree.SubElement(x_variables, "variable", name='hold_music', value=e.hold_music)
        if e.toll_allow:
            etree.SubElement(x_variables, "variable", name='toll_allow', value=e.toll_allow)
        if e.accountcode:
            etree.SubElement(x_variables, "variable", name='accountcode', value=e.accountcode)
        if e.user_context:
            etree.SubElement(x_variables, "variable", name='user_context', value=e.user_context)
        if e.effective_caller_id_name:
            etree.SubElement(x_variables, "variable", name='effective_caller_id_name', value=e.effective_caller_id_name)
        if e.effective_caller_id_number:
            etree.SubElement(x_variables, "variable", name='effective_caller_id_number', value=e.effective_caller_id_number)
        if e.outbound_caller_id_name:
            etree.SubElement(x_variables, "variable", name='outbound_caller_id_name', value=e.outbound_caller_id_name)
        if e.outbound_caller_id_number:
            etree.SubElement(x_variables, "variable", name='outbound_caller_id_number', value=e.outbound_caller_id_number)
        if e.emergency_caller_id_name:
            etree.SubElement(x_variables, "variable", name='emergency_caller_id_name', value=e.emergency_caller_id_name)
        if e.emergency_caller_id_number:
            etree.SubElement(x_variables, "variable", name='emergency_caller_id_number', value=e.emergency_caller_id_number)
        if e.missed_call_app:
            etree.SubElement(x_variables, "variable", name='missed_call_app', value=e.missed_call_app)
        if e.missed_call_data:
            etree.SubElement(x_variables, "variable", name='missed_call_data', value=e.missed_call_data)

        directory_full_name = 'None'
        if e.directory_first_name:
            directory_full_name = e.directory_first_name
            if e.directory_last_name:
                directory_full_name += ' %s' % e.directory_last_name
        etree.SubElement(x_variables, "variable", name='directory_full_name', value=directory_full_name)

        etree.SubElement(x_variables, "variable", name='directory-visible', value=e.directory_visible)
        etree.SubElement(x_variables, "variable", name='directory-exten-visible', value=e.directory_exten_visible)
        if e.limit_max > 0:
            etree.SubElement(x_variables, "variable", name='limit_max', value=str(e.limit_max))
        else:
            etree.SubElement(x_variables, "variable", name='limit_max', value='5')

        if e.limit_destination:
            etree.SubElement(x_variables, "variable", name='limit_destination', value=e.limit_destination)
        if e.sip_force_contact:
            etree.SubElement(x_variables, "variable", name='sip-force-contact', value=e.sip_force_contact)
        if e.sip_force_expires:
            etree.SubElement(x_variables, "variable", name='sip-force-expires', value=e.sip_force_expires)
        if e.nibble_account:
            etree.SubElement(x_variables, "variable", name='nibble_accouint', value=nibble_account)
        if e.absolute_codec_string:
            etree.SubElement(x_variables, "variable", name='absolute_codec_string', value=e.absolute_codec_string)
        etree.SubElement(x_variables, "variable", name='force_ping', value=e.force_ping)
        if e.sip_bypass_media:
            if e.sip_bypass_media == 'bypass-media':
                etree.SubElement(x_variables, "variable", name='bypass_media', value='true')
            if e.sip_bypass_media == 'bypass-media-after-bridge':
                etree.SubElement(x_variables, "variable", name='bypass_media_after_bridge', value='true')
            if e.sip_bypass_media == 'proxy-media':
                etree.SubElement(x_variables, "variable", name='proxy_media', value='true')
        etree.SubElement(x_variables, "variable", name='forward_all_enabled', value=e.forward_all_enabled)
        if e.forward_all_destination:
            etree.SubElement(x_variables, "variable", name='forward_all_destination', value=e.forward_all_destination)
        etree.SubElement(x_variables, "variable", name='forward_busy_enabled', value=e.forward_busy_enabled)
        if e.forward_busy_destination:
            etree.SubElement(x_variables, "variable", name='forward_busy_destination', value=e.forward_busy_destination)
        etree.SubElement(x_variables, "variable", name='forward_no_answer_enabled', value=e.forward_no_answer_enabled)
        if e.forward_no_answer_destination:
            etree.SubElement(x_variables, "variable", name='forward_no_answer_destination', value=e.forward_no_answer_destination)
        etree.SubElement(x_variables, "variable", name='forward_user_not_registered_enabled', value=e.forward_user_not_registered_enabled)
        if e.forward_user_not_registered_destination:
            etree.SubElement(x_variables, "variable", name='forward_user_not_registered_destination', value=e.forward_user_not_registered_destination)
        etree.SubElement(x_variables, "variable", name='follow_me_enabled', value=e.follow_me_enabled)
        if e.follow_me_destinations:
            etree.SubElement(x_variables, "variable", name='follow_me_destinations', value=e.follow_me_destinations)
        etree.SubElement(x_variables, "variable", name='do_not_disturb', value=e.do_not_disturb)
        etree.SubElement(x_variables, "variable", name='record_stereo', value='true')
        etree.SubElement(x_variables, "variable", name='transfer_fallback_extension', value='operator')
        etree.SubElement(x_variables, "variable", name='export_vars', value='domain_name')
        return


    def GetDirectory(self, domain, user, number_as_presence_id, cacheable = True):
        directory_cache_key = 'directory:%s@%s' % (user, domain)
        xml = cache.get(directory_cache_key)
        if xml:
            return xml

        e = Extension.objects.filter((Q(extension = user) | Q(number_alias = user)), domain_id__name = domain, enabled = 'true').first()
        if e == None:
            xml = self.NotFoundXml()
            cache.set(directory_cache_key, xml)
            return xml

        v = Voicemail.objects.filter(extension_id__extension = user, enabled = 'true').first()
        eu = ExtensionUser.objects.filter(extension_id = e.id, default_user = 'true').first()

        x_root = etree.XML(b'<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n<document type=\"freeswitch/xml\"></document>')
        x_section = etree.SubElement(x_root, "section", name='directory')

        x_users = self.DirectoryAddDomain(domain, x_section)
        self.DirectoryAddUser(domain, user, number_as_presence_id, x_users, e, eu, v, cacheable)

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        cache.set(directory_cache_key, xml)
        return xml


    def GetAcl(self, domain):
        es = Extension.objects.select_related('domain_id').filter(domain_id__name = domain, enabled = 'true').exclude(cidr__isnull = True).exclude(cidr__exact = '').order_by('domain_id')

        x_root = etree.XML(b'<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n<document type=\"freeswitch/xml\"></document>')
        x_section = etree.SubElement(x_root, "section", name='directory')

        last_domain = 'None'
        for e in es:
            if not last_domain == e.domain_id.name:
                last_domain = e.domain_id.name
                x_users = self.DirectoryAddDomain(e.domain_id.name, x_section, False, False)
            self.DirectoryAddUserAcl(domain, x_users, e)

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml


    def GetDomain(self, domain):
        ds = Domain.objects.filter(enabled = 'true').order_by('name')

        x_root = etree.XML(b'<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n<document type=\"freeswitch/xml\"></document>')
        x_section = etree.SubElement(x_root, "section", name='directory')

        last_domain = 'None'
        for d in ds:
            self.DirectoryAddDomain(e.domain_id.name, x_section, False, False)

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml


    def GetDirectoryStatic(self, number_as_presence_id, cacheable = False):
        x_root = etree.XML(b'<?xml version=\"1.0\" encoding=\"UTF-8\"?><include></include>\n')
        es = Extension.objects.select_related('domain_id').prefetch_related('extensionuser', 'voicemail').filter(enabled = 'true').order_by('domain_id')
        last_domain = 'None'
        for e in es:
            if not last_domain == e.domain_id.name:
                last_domain = e.domain_id.name
                x_users = self.DirectoryAddDomain(e.domain_id.name, x_root)
            v = e.voicemail.filter(enabled = 'true').first()
            eu = e.extensionuser.filter(default_user = 'true').first()
            self.DirectoryAddUser(e.domain_id.name, e.extension, number_as_presence_id, x_users, e, eu, v, cacheable)

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml


    def GetDialplan(self, caller_context, context_type, hostname, destination_number):
        xml_list = list()
        call_context = caller_context
        if caller_context == '':
            call_context = 'public'
        context_name = call_context
        if call_context == 'public' or call_context[:7] == 'public@' or call_context[-7:] == '.public':
            context_name = 'public'

        dialplan_cache_key = 'dialplan:%s' % call_context
        if context_name == 'public' and context_type == "single":
            dialplan_cache_key = 'dialplan:%s:%s' % (context_name, destination_number)

        xml = cache.get(dialplan_cache_key)
        if xml:
            return xml

        xml_list.append(self.XmlHeader('dialplan', call_context))

        if context_name == 'public' and context_type == 'single':
            xml_list.extend(Dialplan.objects.filter((Q(category = 'Inbound route',  number = destination_number) | Q(context__contains='public', domain_id__isnull=True)), (Q(hostname = hostname) | Q(hostname__isnull=True)), enabled = 'true').values_list('xml', flat=True).order_by('sequence'))
            if len(xml_list) == 1:
                xml_list = self.NotFoundPublic(xml_list)
        else:
            if context_name == "public" or ('@' in context_name):
                xml_list.extend(Dialplan.objects.filter((Q(hostname = hostname) | Q(hostname__isnull=True)), context = call_context, enabled = 'true').values_list('xml', flat=True).order_by('sequence'))
            else:
                xml_list.extend(Dialplan.objects.filter((Q(context = call_context) | Q(context = '${domain_name}')), (Q(hostname = hostname) | Q(hostname__isnull=True)), enabled = 'true').values_list('xml', flat=True).order_by('sequence'))

        if len(xml_list) == 0:
            return self.NotFoundXml()

        xml_list.append(self.XmlFooter())

        xml = '\n'
        xml = xml.join(xml_list)
        cache.set(dialplan_cache_key, xml)
        return xml


    def GetDialplanStatic(self, hostname):
        xml_list = list()
        xml_list.append('<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<include>\n')
        dps = Dialplan.objects.filter((Q(hostname = hostname) | Q(hostname__isnull=True)), enabled = 'true').order_by('context', 'sequence')
        start = True
        dp_count = 0
        for d in dps:
            dp_count += 1
            if start == True:
                start = False
                last_context = d.context
                xml_list.append('<context name=\"{}\">\n'.format(d.context))
            if not last_context == d.context:
                last_context = d.context
                xml_list.append('</context>\n<context name=\"{}\">\n'.format(d.context))
            xml_list.append(d.xml)

        xml_list.append('</context>\n</include>\n')

        if dp_count > 0:
            xml = '\n'
            xml = xml.join(xml_list)
            return xml

        return self.NotFoundXml()
