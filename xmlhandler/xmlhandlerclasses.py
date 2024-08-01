#
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

from django.core.cache import cache
from lxml import etree
from pbx.commonvalidators import valid_uuid4
from django.db.models import Q
from .xmlhandler import XmlHandler
from dialplans.models import Dialplan, DialplanExcludes
from tenants.models import Domain
from tenants.pbxsettings import PbxSettings
from accounts.models import Extension, ExtensionUser, Gateway
from voicemail.models import Voicemail
from switch.models import (
    AccessControl, AccessControlNode, SipProfile, SwitchVariable
    )
from phrases.models import PhraseDetails
from musiconhold.models import MusicOnHold
from numbertranslations.models import NumberTranslations
from ivrmenus.models import IvrMenus
from conferencesettings.models import ConferenceControls, ConferenceProfiles
from callcentres.models import CallCentreQueues, CallCentreAgents, CallCentreTiers, get_agent_contact


class DirectoryHandler(XmlHandler):

    def DirectoryAddDomain(self, domain, x_section, params=True, variables=True, groups=True):
        x_domain = etree.SubElement(x_section, "domain", name=domain, alias='true')
        if params:
            x_params = etree.SubElement(x_domain, "params")
            etree.SubElement(x_params, "param", name='jsonrpc-allowed-methods', value='verto')
            etree.SubElement(
                x_params, "param", name='jsonrpc-allowed-event-channels',
                value='demo,conference,presence'
                )
        if variables:
            x_variables = etree.SubElement(x_domain, "variables")
            etree.SubElement(x_variables, "variable", name='default_language', value='$${default_language}')
            etree.SubElement(x_variables, "variable", name='default_dialect', value='$${default_dialect}')
            etree.SubElement(x_variables, "variable", name='default_voice', value='$${default_voice}')
            etree.SubElement(x_variables, "variable", name='sounds_dir', value='$${sounds_dir}')
        if groups:
            x_groups = etree.SubElement(x_domain, "groups")
            x_group = etree.SubElement(x_groups, "group", name='default')
            x_users = etree.SubElement(x_group, "users")
            return x_users
        return x_domain

    def DirectoryAddUserAcl(self, domain, x_users, e):
        x_user = etree.SubElement(x_users, "user", id=e.extension)
        if e.cidr:
            x_user.set("cidr", e.cidr)
        return

    def DirectoryAddUser(self, domain, user, number_as_presence_id, x_users, e, eu, v, cacheable):
        flag_vm_enabled = True
        vm_enabled = 'true'
        if v is None:
            flag_vm_enabled = False
            vm_enabled = 'false'

        presence_id = '%s@%s' % (e.extension, domain)
        if number_as_presence_id:
            presence_id = '%s@%s' % (e.number_alias, domain)

        destination = '%s@%s' % (e.extension, domain)

        if e.dial_string:
            dial_string = e.dial_string
        else:
            dial_string = '{sip_invite_domain=%s,presence_id=%s}${sofia_contact(%s)}' % (
                domain, presence_id, destination
                )

        x_user = etree.SubElement(x_users, "user", id=user)
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
            etree.SubElement(x_params, "param", name='vm-password', value=(v.password if v.password else ''))

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
        # etree.SubElement(x_params, "param", name='jsonrpc-allowed-methods', value='verto')
        # etree.SubElement(x_params, "param", name='jsonrpc-allowed-event-channels', value='demo,conference,presence')
        x_variables = etree.SubElement(x_user, "variables")

        etree.SubElement(x_variables, "variable", name='domain_uuid', value=str(e.domain_id.id))
        etree.SubElement(x_variables, "variable", name='domain_name', value=domain)
        etree.SubElement(x_variables, "variable", name='extension_uuid', value=str(e.id))
        if eu:
            if eu.user_uuid:
                etree.SubElement(x_variables, "variable", name='user_uuid', value=str(eu.user_uuid.user_uuid))
                etree.SubElement(x_variables, "variable", name='user_name', value=str(eu.user_uuid))

        etree.SubElement(x_variables, "variable", name='call_timeout', value=str(e.call_timeout))
        etree.SubElement(x_variables, "variable", name='caller_id_name', value=e.extension)
        etree.SubElement(x_variables, "variable", name='caller_id_number', value=sip_from_number)

        etree.SubElement(x_variables, "variable", name='presence_id', value=presence_id)
        if flag_vm_enabled:
            if v.greeting_id:
                etree.SubElement(x_variables, "variable", name='voicemail_greeting_number', value=str(v.greeting_id))
            if v.alternate_greeting_id:
                etree.SubElement(
                    x_variables, "variable", name='voicemail_alternate_greet_id',
                    value=str(v.alternate_greeting_id)
                    )

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
            etree.SubElement(
                x_variables, "variable", name='effective_caller_id_name',
                value=e.effective_caller_id_name
                )
        if e.effective_caller_id_number:
            etree.SubElement(
                x_variables, "variable", name='effective_caller_id_number',
                value=e.effective_caller_id_number
                )
        if e.outbound_caller_id_name:
            etree.SubElement(
                x_variables, "variable", name='outbound_caller_id_name',
                value=e.outbound_caller_id_name
                )
        if e.outbound_caller_id_number:
            etree.SubElement(
                x_variables, "variable", name='outbound_caller_id_number',
                value=e.outbound_caller_id_number
                )
        if e.emergency_caller_id_name:
            etree.SubElement(
                x_variables, "variable", name='emergency_caller_id_name',
                value=e.emergency_caller_id_name
                )
        if e.emergency_caller_id_number:
            etree.SubElement(
                x_variables, "variable", name='emergency_caller_id_number',
                value=e.emergency_caller_id_number
                )
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
            etree.SubElement(x_variables, "variable", name='nibble_accouint', value=e.nibble_account)
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
            etree.SubElement(
                x_variables, "variable", name='forward_busy_destination',
                value=e.forward_busy_destination
                )
        etree.SubElement(x_variables, "variable", name='forward_no_answer_enabled', value=e.forward_no_answer_enabled)
        if e.forward_no_answer_destination:
            etree.SubElement(
                x_variables, "variable", name='forward_no_answer_destination',
                value=e.forward_no_answer_destination
                )
        etree.SubElement(
                x_variables, "variable", name='forward_user_not_registered_enabled',
                value=e.forward_user_not_registered_enabled
                )
        if e.forward_user_not_registered_destination:
            etree.SubElement(
                x_variables, "variable", name='forward_user_not_registered_destination',
                value=e.forward_user_not_registered_destination
                )
        etree.SubElement(x_variables, "variable", name='follow_me_enabled', value=e.follow_me_enabled)
        if e.follow_me_destinations:
            etree.SubElement(x_variables, "variable", name='follow_me_destinations', value=e.follow_me_destinations)
        etree.SubElement(x_variables, "variable", name='do_not_disturb', value=e.do_not_disturb)
        etree.SubElement(x_variables, "variable", name='record_stereo', value='true')
        etree.SubElement(x_variables, "variable", name='transfer_fallback_extension', value='operator')
        etree.SubElement(x_variables, "variable", name='export_vars', value='domain_name')
        return

    def DirectoryPopulate(self, domain, x_users, e):
        x_user = etree.SubElement(x_users, "user", id=e.extension)
        # sip_from_number = e.extension
        if e.number_alias:
            x_user.set("number-alias", e.number_alias)
            # sip_from_number = e.number_alias

        x_params = etree.SubElement(x_user, "params")
        etree.SubElement(x_params, "param", name='directory-visible', value=e.directory_visible)
        etree.SubElement(x_params, "param", name='directory-exten-visible', value=e.directory_exten_visible)
        x_variables = etree.SubElement(x_user, "variables")
        etree.SubElement(x_variables, "variable", name='directory-visible', value=e.directory_visible)
        etree.SubElement(x_variables, "variable", name='directory-exten-visible', value=e.directory_exten_visible)
        return

    def DirectoryReverseAuth(self, domain, user, x_users, password):
        x_user = etree.SubElement(x_users, "user", id=user)
        x_params = etree.SubElement(x_user, "params")
        etree.SubElement(x_params, "param", name='reverse-auth-user', value=user)
        etree.SubElement(x_params, "param", name='reverse-auth-pass', value=password)
        return

    def GetDirectory(self, domain, user, cacheable=True):
        if not domain:
            xml = self.NotFoundXml()
            return xml
        if not user:
            xml = self.NotFoundXml()
            return xml

        cache_key = 'xmlhandler:number_as_presence_id'
        number_as_presence_id = cache.get(cache_key)
        if not number_as_presence_id:
            number_as_presence_id = PbxSettings().default_settings(
                    'xmlhandler', 'number_as_presence_id', 'boolean'
                    )
            cache.set(cache_key, number_as_presence_id)

        directory_cache_key = 'directory:%s@%s' % (user, domain)
        xml = cache.get(directory_cache_key)
        if xml:
            return xml

        e = Extension.objects.filter(
                (Q(extension=user) | Q(number_alias=user)), domain_id__name=domain, enabled='true'
                ).first()
        if e is None:
            xml = self.NotFoundXml()
            cache.set(directory_cache_key, xml)
            return xml

        v = Voicemail.objects.filter(extension_id__extension=user, enabled='true').first()
        eu = ExtensionUser.objects.filter(extension_id=e.id, default_user='true').first()

        x_root = self.XrootDynamic()
        x_section = etree.SubElement(x_root, "section", name='directory')

        x_users = self.DirectoryAddDomain(domain, x_section)
        self.DirectoryAddUser(domain, user, number_as_presence_id, x_users, e, eu, v, cacheable)

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        cache.set(directory_cache_key, xml)
        if self.debug:
            print(xml)
        return xml

    def GetAcl(self, domain=None):
        if domain:
            es = Extension.objects.select_related('domain_id').filter(
                domain_id__name=domain, enabled='true'
                ).exclude(cidr__isnull=True).exclude(cidr__exact='').order_by('domain_id')
        else:
            es = Extension.objects.select_related('domain_id').filter(
                enabled='true'
                ).exclude(cidr__isnull=True).exclude(cidr__exact='').order_by('domain_id')

        x_root = self.XrootDynamic()
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

    def GetDomain(self):
        ds = Domain.objects.filter(enabled='true').order_by('name')
        x_root = self.XrootDynamic()
        x_section = etree.SubElement(x_root, "section", name='directory')

        for d in ds:
            self.DirectoryAddDomain(d.name, x_section, False, False, False)

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml

    def GetGroupCall(self, domain):
        if not domain:
            xml = self.NotFoundXml()
            return xml

        directory_cache_key = 'directory:groups:%s' % domain
        xml = cache.get(directory_cache_key)
        if xml:
            return xml

        es = Extension.objects.select_related('domain_id').filter(
                domain_id__name=domain, enabled='true'
                ).exclude(call_group__isnull=True).exclude(call_group='').order_by('call_group')
        cg_dict = {}
        for e in es:
            if ',' in e.call_group:
                call_groups = e.call_group.lower().replace(' ', '').split(',')
            else:
                call_groups = [e.call_group.lower().replace(' ', '')]
            for cg in call_groups:
                if cg in cg_dict:
                    cg_dict[cg].append(e.extension)
                else:
                    cg_dict[cg] = [e.extension]

        x_root = self.XrootDynamic()
        x_section = etree.SubElement(x_root, "section", name='directory')
        x_domain = self.DirectoryAddDomain(domain, x_section, False, False, False)
        x_groups = etree.SubElement(x_domain, "groups")
        for key, value in cg_dict.items():
            x_group = etree.SubElement(x_groups, "group", name=key)
            for extn in value:
                etree.SubElement(x_group, "user", id=extn, type='pointer')

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        cache.set(directory_cache_key, xml)
        if self.debug:
            print(xml)
        return xml

    def GetReverseAuthLookup(self, domain, user):
        if not domain:
            xml = self.NotFoundXml()
            return xml
        if not user:
            xml = self.NotFoundXml()
            return xml
        directory_cache_key = 'directory:reverseauth:%s@%s' % (user, domain)
        xml = cache.get(directory_cache_key)
        if xml:
            return xml

        e = Extension.objects.filter(
                (Q(extension=user) | Q(number_alias=user)), domain_id__name=domain, enabled='true'
                ).first()
        if e is None:
            xml = self.NotFoundXml()
            cache.set(directory_cache_key, xml)
            return xml

        x_root = self.XrootDynamic()
        x_section = etree.SubElement(x_root, "section", name='directory')

        x_users = self.DirectoryAddDomain(domain, x_section)
        self.DirectoryReverseAuth(domain, user, x_users, e.password)

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        cache.set(directory_cache_key, xml)
        if self.debug:
            print(xml)
        return xml

    def GetPopulateDirectory(self, domain=None):
        if domain:
            es = Extension.objects.select_related('domain_id').filter(
                (Q(directory_visible='true') | Q(directory_exten_visible='true')),
                domain_id__name=domain, enabled='true'
                ).order_by('domain_id')
        else:
            es = Extension.objects.select_related('domain_id').filter(
                (Q(directory_visible='true') | Q(directory_exten_visible='true')),
                enabled='true'
                ).order_by('domain_id')

        x_root = self.XrootDynamic()
        x_section = etree.SubElement(x_root, "section", name='directory')

        last_domain = 'None'
        for e in es:
            if not last_domain == e.domain_id.name:
                last_domain = e.domain_id.name
                x_users = self.DirectoryAddDomain(e.domain_id.name, x_section, False, False)
            self.DirectoryPopulate(domain, x_users, e)

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml

    def GetDirectoryStatic(self, number_as_presence_id, cacheable=False):
        number_as_presence_id = PbxSettings().default_settings('xmlhandler', 'number_as_presence_id', 'boolean')

        x_root = self.XrootStatic()
        es = Extension.objects.select_related('domain_id').prefetch_related('extensionuser', 'voicemail').filter(
                enabled='true'
                ).order_by('domain_id')
        last_domain = 'None'
        for e in es:
            if not last_domain == e.domain_id.name:
                last_domain = e.domain_id.name
                x_users = self.DirectoryAddDomain(e.domain_id.name, x_root)
            v = e.voicemail.filter(enabled='true').first()
            eu = e.extensionuser.filter(default_user='true').first()
            self.DirectoryAddUser(e.domain_id.name, e.extension, number_as_presence_id, x_users, e, eu, v, cacheable)

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml


class DialplanHandler(XmlHandler):

    def GetDialplan(self, caller_context, hostname, destination_number):
        xml_list = list()
        call_context = caller_context
        if caller_context == '':
            call_context = 'public'
        context_name = call_context
        if call_context == 'public' or call_context[:7] == 'public@' or call_context[-7:] == '.public':
            context_name = 'public'

        cache_key = 'xmlhandler:context_type'
        context_type = cache.get(cache_key)
        if not context_type:
            context_type = PbxSettings().default_settings('xmlhandler', 'context_type', 'text')
            cache.set(cache_key, context_type)

        dialplan_cache_key = 'dialplan:%s' % call_context
        if context_name == 'public' and context_type == "single":
            dialplan_cache_key = 'dialplan:%s:%s' % (context_name, destination_number)

        xml = cache.get(dialplan_cache_key)
        if xml:
            return xml

        xml_list.append(self.XmlHeader('dialplan', call_context))

        if context_name == 'public' and context_type == 'single':
            xml_list.extend(Dialplan.objects.filter(
                (Q( category='Inbound route',  xml__isnull=False,
                    number=destination_number
                    ) | Q(context__contains='public', domain_id__isnull=True)),
                (Q(hostname=hostname) | Q(hostname__isnull=True)), enabled='true'
                ).values_list('xml', flat=True).order_by('sequence'))
            if len(xml_list) == 2:
                xml_list = self.NotFoundPublic(xml_list)
        else:
            if context_name == "public" or ('@' in context_name):
                xml_list.extend(Dialplan.objects.filter(
                    (Q(hostname=hostname) | Q(hostname__isnull=True)),  xml__isnull=False,
                    context=call_context, enabled='true'
                    ).values_list('xml', flat=True).order_by('sequence'))
            else:
                dialplan_excludes_cache_key = 'dialplanexclude:%s' % call_context
                excludeList = cache.get(dialplan_excludes_cache_key)
                if excludeList is None:
                    excludeList = list(DialplanExcludes.objects.values_list('app_id', flat=True).filter(domain_name=call_context))
                    cache.set(dialplan_excludes_cache_key, excludeList)
                if excludeList:
                    xml_list.extend(Dialplan.objects.filter(
                        (Q(context=call_context) | Q(context='${domain_name}')),
                        (Q(hostname=hostname) | Q(hostname__isnull=True)),  xml__isnull=False, enabled='true'
                        ).exclude(app_id__in=excludeList).values_list('xml', flat=True).order_by('sequence'))
                else:
                    xml_list.extend(Dialplan.objects.filter(
                        (Q(context=call_context) | Q(context='${domain_name}')),
                        (Q(hostname=hostname) | Q(hostname__isnull=True)),  xml__isnull=False, enabled='true'
                        ).values_list('xml', flat=True).order_by('sequence'))

        if len(xml_list) == 0:
            return self.NotFoundXml()

        xml_list.append(self.XmlFooter())

        xml = '\n'
        xml = xml.join(xml_list)
        cache.set(dialplan_cache_key, xml)
        if self.debug:
            print(xml)
        return xml

    def GetDialplanStatic(self, hostname):
        xml_list = list()
        xml_list.append('<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<include>\n')
        dps = Dialplan.objects.filter(
                (Q(hostname=hostname) | Q(hostname__isnull=True)), enabled='true'
                ).order_by('context', 'sequence')
        start = True
        dp_count = 0
        for d in dps:
            dp_count += 1
            if start:
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


class LanguagesHandler(XmlHandler):

    def GetLanguage(self, lang, macro_name):
        if not valid_uuid4(macro_name):
            return self.NotFoundXml()

        languages_cache_key = 'languages:%s:%s' % (lang, macro_name)
        xml = cache.get(languages_cache_key)
        if xml:
            return xml

        cache_key = 'xmlhandler:lang:sounds_dir'
        sounds_dir = cache.get(cache_key)
        if not sounds_dir:
            sounds_dir = PbxSettings().default_settings('switch', 'sounds', 'dir', '/usr/share/freeswitch/sounds', True)
            cache.set(cache_key, sounds_dir)

        default_language = self.get_default_language()
        default_dialect = self.get_default_dialect()
        default_voice = self.get_default_voice()

        xml_list = list()
        x_root = self.XrootDynamic()
        x_section = etree.SubElement(x_root, "section", name='languages')
        x_language = etree.SubElement(x_section, "language", name=lang)
        x_language.attrib['say-module'] = lang
        x_language.attrib['sound-prefix'] = '{}/{}/{}/{}'.format(sounds_dir, default_language, default_dialect, default_voice)
        x_language.attrib['tts-engine'] = 'cepstral'
        x_language.attrib['tts-voice'] = default_voice
        x_phrases = etree.SubElement(x_language, "phrases")
        x_macros = etree.SubElement(x_phrases, "macros")
        pds = PhraseDetails.objects.filter(phrase_id=macro_name).order_by('sequence')
        # using len() here because we are going to itterate the queryset anyway (otherwise count is better but two hits on the RDBMS).
        if len(pds) > 0:
            x_macro = etree.SubElement(x_macros, "macro", name=macro_name)
            x_input = etree.SubElement(x_macro, "input", pattern="(.*)")
            x_match = etree.SubElement(x_input, "match")
        for pd in pds:
            etree.SubElement(x_match, "action", function=pd.pfunction, data=pd.data)

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        cache.set(languages_cache_key, xml)
        if self.debug:
            print(xml)
        return xml


class ConfigHandler(XmlHandler):

    def __init__(self):
        self.debug = False
        try:
            cs_dsn_r = SwitchVariable.objects.get(enabled='true', category='DSN', name='dsn_callcentre')
            self.cs_dsn = cs_dsn_r.value
        except:
            self.cs_dsn = None

    def GetACL(self):
        configuration_cache_key = 'configuration:acl.conf'
        xml = cache.get(configuration_cache_key)
        if xml:
            return xml

        x_root = self.XrootDynamic()
        x_section = etree.SubElement(x_root, "section", name='configuration')
        x_conf_name = etree.SubElement(x_section, 'configuration', name='acl.conf', description='Network Lists')
        x_networklists = etree.SubElement(x_conf_name, 'network-lists')
        alist = AccessControl.objects.all().order_by('name')
        for a in alist:
            x_netlist = etree.SubElement(x_networklists, 'list', name=a.name, default=a.default)
            nlist = AccessControlNode.objects.filter(access_control_id=a.id).order_by('-type')
            for n in nlist:
                if n.domain is not None:
                    etree.SubElement(x_netlist, 'node', type=n.type, domain=n.domain)
                if n.cidr is not None:
                    etree.SubElement(x_netlist, 'node', type=n.type, cidr=n.cidr)

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        cache.set(configuration_cache_key, xml)
        if self.debug:
            print(xml)
        return xml

    def GetSofia(self, hostname=''):
        configuration_cache_key = 'configuration:sofia.conf'
        xml = cache.get(configuration_cache_key)
        if xml:
            return xml
        x_root = self.XrootDynamic()
        x_section = etree.SubElement(x_root, "section", name='configuration')
        x_conf_name = etree.SubElement(x_section, 'configuration', name='sofia.conf', description='sofia Endpoint')
        x_global_settings = etree.SubElement(x_conf_name, 'global_settings')
        etree.SubElement(x_global_settings, 'param', name='log-level', value='0')
        #etree.SubElement(x_global_settings, 'param', name='auto-restart', value='false')
        etree.SubElement(x_global_settings, 'param', name='debug-presense', value='0')
        #etree.SubElement(x_global_settings, 'param', name='capture-serverlog-level', value='udp:homer.mydomain.com:5060')
        x_profiles = etree.SubElement(x_conf_name, 'profiles')
        ps = SipProfile.objects.filter(enabled='true').order_by('name')
        for p in ps:
            ds = p.sipprofiledomain_set.all().order_by('name')
            ss = p.sipprofilesetting_set.filter(enabled='true').order_by('name')
            gws = Gateway.objects.filter((Q(hostname=hostname) | Q(hostname__isnull=True)), enabled='true', profile=p.name)
            x_profile = etree.SubElement(x_profiles, 'profile', name=p.name)
            etree.SubElement(x_profile, 'aliases')
            x_gateways = etree.SubElement(x_profile, 'gateways')
            etree.SubElement(x_gateways, 'X-PRE-PROCESS', cmd='include', data='sip_profiles/%s/*.xml' % p.name)
            for gw in gws:
                x_gateway = etree.SubElement(x_gateways, 'gateway', name=str(gw.id))
                if gw.username:
                    etree.SubElement(x_gateway, 'param', name='username', value=gw.username)
                if gw.distinct_to:
                    etree.SubElement(x_gateway, 'param', name='distinct-to', value=gw.distinct_to)
                if gw.auth_username:
                    etree.SubElement(x_gateway, 'param', name='auth-username', value=gw.auth_username)
                if gw.password:
                    etree.SubElement(x_gateway, 'param', name='password', value=gw.password)
                if gw.realm:
                    etree.SubElement(x_gateway, 'param', name='realm', value=gw.realm)
                if gw.from_user:
                    etree.SubElement(x_gateway, 'param', name='from-user', value=gw.from_user)
                if gw.from_domain:
                    etree.SubElement(x_gateway, 'param', name='from-domain', value=gw.from_domain)
                if gw.proxy:
                    etree.SubElement(x_gateway, 'param', name='proxy', value=gw.proxy)
                if gw.register_proxy:
                    etree.SubElement(x_gateway, 'param', name='register-proxy', value=gw.register_proxy)
                if gw.outbound_proxy:
                    etree.SubElement(x_gateway, 'param', name='outbound-proxy', value=gw.outbound_proxy)
                if gw.expire_seconds:
                    etree.SubElement(x_gateway, 'param', name='expire-seconds', value=str(gw.expire_seconds))
                if gw.register:
                    etree.SubElement(x_gateway, 'param', name='register', value=gw.register)
                if gw.register_transport:
                    if gw.register_transport == 'udp':
                        etree.SubElement(x_gateway, 'param', name='register-transport', value=gw.register_transport)
                    elif gw.register_transport == 'tcp':
                        etree.SubElement(x_gateway, 'param', name='register-transport', value=gw.register_transport)
                    elif gw.register_transport == 'tls':
                        etree.SubElement(x_gateway, 'param', name='register-transport', value=gw.register_transport)
                        etree.SubElement(x_gateway, 'param', name='contact-params', value='transport=tls')
                    else:
                        etree.SubElement(x_gateway, 'param', name='register-transport', value='udp')

                if gw.retry_seconds:
                    etree.SubElement(x_gateway, 'param', name='retry-seconds', value=str(gw.retry_seconds))
                if gw.extension:
                    etree.SubElement(x_gateway, 'param', name='extension', value=gw.extension)
                if gw.ping:
                    etree.SubElement(x_gateway, 'param', name='ping', value=gw.ping)
                if gw.context:
                    etree.SubElement(x_gateway, 'param', name='context', value=gw.context)
                if gw.caller_id_in_from:
                    etree.SubElement(x_gateway, 'param', name='caller-id-in-from', value=gw.caller_id_in_from)
                if gw.supress_cng:
                    etree.SubElement(x_gateway, 'param', name='supress-cng', value=gw.supress_cng)
                if gw.extension_in_contact:
                    etree.SubElement(x_gateway, 'param', name='extension-in-contact', value=gw.extension_in_contact)
                x_variables = etree.SubElement(x_gateway, 'variables')
                if gw.sip_cid_type:
                    etree.SubElement(x_variables, 'variable', name='sip-cid-type', value=gw.sip_cid_type)

            x_domains = etree.SubElement(x_profile, 'domains')
            for d in ds:
                etree.SubElement(x_domains, 'domain', name=d.name, alias=d.alias, parse=d.parse)

            x_settings = etree.SubElement(x_profile, 'settings')
            for s in ss:
                if s.value is None:
                    s_value = ''
                else:
                    s_value = s.value
                etree.SubElement(x_settings, 'param', name=s.name, value=s_value)


        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        cache.set(configuration_cache_key, xml)
        if self.debug:
            print(xml)
        return xml

    def GetLocalStream(self):
        configuration_cache_key = 'configuration:local_stream.conf'
        xml = cache.get(configuration_cache_key)
        if xml:
            return xml
        x_root = self.XrootDynamic()
        x_section = etree.SubElement(x_root, "section", name='configuration')
        x_conf_name = etree.SubElement(x_section, 'configuration', name='local_stream.conf', description='Stream files from local directories')
        mlist = MusicOnHold.objects.all().order_by('name', 'rate')
        for m in mlist:
            x_mdir = etree.SubElement(x_conf_name, 'directory', name=m.name, path=m.path)
            etree.SubElement(x_mdir, 'param', name='rate', value=str(m.rate))
            etree.SubElement(x_mdir, 'param', name='shuffle', value=m.shuffle)
            etree.SubElement(x_mdir, 'param', name='channels', value=str(m.channels))
            etree.SubElement(x_mdir, 'param', name='interval', value=str(m.interval))
            etree.SubElement(x_mdir, 'param', name='timer-name', value=m.timer_name)
            if m.chime_list:
                etree.SubElement(x_mdir, 'param', name='chime-list', value=m.chime_list)
                if m.chime_freq:
                    etree.SubElement(x_mdir, 'param', name='chime-freq', value=m.chime_freq)
                if m.chime_max:
                    etree.SubElement(x_mdir, 'param', name='chime-max', value=m.chime_max)

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        cache.set(configuration_cache_key, xml)
        if self.debug:
            print(xml)
        return xml

    def GetTranslate(self):
        configuration_cache_key = 'configuration:translate.conf'
        xml = cache.get(languages_cache_key)
        if xml:
            return xml
        x_root = self.XrootDynamic()
        x_section = etree.SubElement(x_root, "section", name='configuration')
        x_conf_name = etree.SubElement(x_section, 'configuration', name='translate.conf', description='Number Translation Rules', autogenerated='true')
        x_profiles = etree.SubElement(x_conf_name, "profiles")
        ns = NumberTranslations.objects.filter(enabled='true').order_by('name')
        for n in ns:
            nds = n.numbertranslationdetails_set.all().order_by('td_order')
            x_profile = etree.SubElement(x_profiles, 'profile', name=n.name, description=n.description)
            for nd in nds:
                etree.SubElement(x_profile, 'rule', regex=nd.regex, replace=nd.replace)

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        cache.set(configuration_cache_key, xml)
        if self.debug:
            print(xml)
        return xml

    def GetIvr(self, ivr_id):
        configuration_cache_key = 'configuration:ivr.conf:%s' % ivr_id
        xml = cache.get(configuration_cache_key)
        if xml:
            return xml
        x_root = self.XrootDynamic()
        x_section = etree.SubElement(x_root, "section", name='configuration')
        x_conf_name = etree.SubElement(x_section, 'configuration', name='ivr.conf', description='IVR Menus')
        x_menus = etree.SubElement(x_conf_name, "menus")
        try:
            ivr = IvrMenus.objects.get(pk=ivr_id)
        except:
            return self.NotFoundXml()

        x_menu = etree.SubElement(x_menus, "menu", name=str(ivr.id), description=ivr.name)
        x_menu.attrib['greet-long'] = (ivr.greet_long if ivr.greet_long else '')
        x_menu.attrib['greet-short'] = (ivr.greet_short if ivr.greet_short else '')
        x_menu.attrib['invalid-sound'] = (ivr.invalid_sound if ivr.invalid_sound else '')
        x_menu.attrib['exit-sound'] = (ivr.exit_sound if ivr.exit_sound else '')
        x_menu.attrib['confirm-macro'] = (ivr.confirm_macro if ivr.confirm_macro else '')
        x_menu.attrib['confirm-key'] = (ivr.confirm_key if ivr.confirm_key else '')
        x_menu.attrib['tts-engine'] = (ivr.tts_engine if ivr.tts_engine else '')
        x_menu.attrib['tts-voice'] = (ivr.tts_voice if ivr.tts_voice else '')
        x_menu.attrib['confirm-attempts'] = str(ivr.confirm_attempts)
        x_menu.attrib['timeout'] = str(ivr.timeout)
        x_menu.attrib['inter-digit-timeout'] = str(ivr.inter_digit_timeout)
        x_menu.attrib['max-failures'] = str(ivr.max_failiures)
        x_menu.attrib['max-timeouts'] = str(ivr.max_timeouts)
        x_menu.attrib['digit-len'] = str(ivr.digit_len)

        ivropts = ivr.ivrmenuoptions_set.all().order_by('sequence')
        for op in ivropts:
            etree.SubElement(x_menu, "entry", action=(
                op.option_action if op.option_action else ''),
                digits=(op.option_digits if op.option_digits else '1'),
                param=(op.option_param if op.option_param else ''),
                description=(op.description if op.description else ''))

        if ivr.direct_dial == 'true':
            etree.SubElement(x_menu, "entry", action='menu-exec-app', digits='/^(\d{2,11})$/',
                param='set ${cond(${user_exists id $1 %s} == true ? user_exists=true : user_exists=false)}' % ivr.context, description='direct dial')
            etree.SubElement(x_menu, "entry", action='menu-exec-app', digits='/^(\d{2,11})$/',
                param='playback ${cond(${user_exists} == true ? ivr/ivr-call_being_transferred.wav : ivr/ivr-that_was_an_invalid_entry.wav)}',
                description='direct dial')
            etree.SubElement(x_menu, "entry", action='menu-exec-app', digits='/^(\d{2,11})$/',
                param='transfer ${cond(${user_exists} == true ? $1 XML %s)}' % ivr.context, description='direct dial')


        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        cache.set(configuration_cache_key, xml)
        if self.debug:
            print(xml)
        return xml

    def GetConference(self):
        configuration_cache_key = 'configuration:conference.conf'
        xml = cache.get(configuration_cache_key)
        if xml:
            return xml

        x_root = self.XrootDynamic()
        x_section = etree.SubElement(x_root, "section", name='configuration')
        x_conf_name = etree.SubElement(x_section, 'configuration', name='conference.conf', description='Audio Conference')
        x_caller_controls = etree.SubElement(x_conf_name, 'caller-controls')
        ccl = ConferenceControls.objects.filter(enabled='true').order_by('name')
        for cc in ccl:
            x_group = etree.SubElement(x_caller_controls, 'group', name=cc.name)
            ccds = cc.conferencecontroldetails_set.filter(enabled='true').order_by('digits')
            for ccd in ccds:
                    etree.SubElement(x_group, 'control', digits=ccd.digits, action=ccd.action, data=(ccd.data if ccd.data else ''))

        x_profiles = etree.SubElement(x_conf_name, 'profiles')
        cpl = ConferenceProfiles.objects.filter(enabled='true').order_by('name')
        for cp in cpl:
            x_profile = etree.SubElement(x_profiles, 'profile', name=cp.name)
            cpps = cc.conferenceprofileparams_set.filter(enabled='true').order_by('name')
            for cpp in cpps:
                    etree.SubElement(x_group, 'control', param=cpp.name, value=(cpp.value if cpp.value else ''))

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        cache.set(configuration_cache_key, xml)
        if self.debug:
            print(xml)
        return xml

    def GetCallcentre(self):
        configuration_cache_key = 'configuration:callcentre.conf'
        xml = cache.get(configuration_cache_key)
        if xml:
            return xml

        x_root = self.XrootDynamic()
        x_section = etree.SubElement(x_root, "section", name='configuration')
        x_conf_name = etree.SubElement(x_section, 'configuration', name='callcenter.conf', description='Call Centre')
        x_settings = etree.SubElement(x_conf_name, 'settings')
        # dsn or dsn_callcenter can go in here if defined and/or required
        if self.cs_dsn:
            etree.SubElement(x_settings, 'param', name='odbc-dsn', value=self.cs_dsn)

        x_queues = etree.SubElement(x_conf_name, 'queues')
        ccqs = CallCentreQueues.objects.filter(enabled='true')
        for ccq in ccqs:
            x_queue = etree.SubElement(x_queues, 'queue', name=str(ccq.id), label='%s@%s' % (ccq.name.replace(' ', '-'), ccq.domain_id.name))
            etree.SubElement(x_queue, 'param', name='strategy', value=ccq.strategy)
            etree.SubElement(x_queue, 'param', name='moh-sound', value=ccq.moh_sound)
            if ccq.record_template:
                etree.SubElement(x_queue, 'param', name='record-template', value=ccq.record_template)
            etree.SubElement(x_queue, 'param', name='time-base-score', value=ccq.time_base_score)
            etree.SubElement(x_queue, 'param', name='max-wait-time', value=str(ccq.max_wait_time))
            etree.SubElement(x_queue, 'param', name='max-wait-time-with-no-agent', value=str(ccq.max_wait_time_na))
            etree.SubElement(x_queue, 'param', name='max-wait-time-with-no-agent-time-reached', value=str(ccq.max_wait_time_natr))
            etree.SubElement(x_queue, 'param', name='tier-rules-apply', value=ccq.tier_rules_apply)
            etree.SubElement(x_queue, 'param', name='tier-rule-wait-second', value=str(ccq.tier_rule_wait_sec))
            etree.SubElement(x_queue, 'param', name='tier-rule-wait-multiply-level', value=ccq.tier_rule_wm_level)
            etree.SubElement(x_queue, 'param', name='tier-rule-no-agent-no-wait', value=ccq.tier_rule_nanw)
            etree.SubElement(x_queue, 'param', name='discard-abandoned-after', value=str(ccq.discard_abndnd_after))
            etree.SubElement(x_queue, 'param', name='abandoned-resume-allowed', value=ccq.abndnd_resume_allowed)
            if ccq.announce_sound:
                etree.SubElement(x_queue, 'param', name='announce-sound', value=ccq.announce_sound)
            if ccq.announce_frequency:
                etree.SubElement(x_queue, 'param', name='announce-frequency', value=str(ccq.announce_frequency))

        x_agents = etree.SubElement(x_conf_name, 'agents')
        ccas = CallCentreAgents.objects.all()
        for cca in ccas:
            agent_contact = get_agent_contact(cca)
            x_agent = etree.SubElement(x_agents, 'agent', name=str(cca.id))
            x_agent.set('label', '%s@%s' % (cca.name.replace(' ', '-'), cca.domain_id.name))
            x_agent.set('type', cca.agent_type)
            x_agent.set('contact', agent_contact)
            if cca.status:
                x_agent.set('status', cca.status)
            x_agent.set('no-answer-delay-time', str(cca.no_answer_delay_time))
            x_agent.set('max-no-answer', str(cca.max_no_answer))
            x_agent.set('wrap-up-time', str(cca.wrap_up_time))
            x_agent.set('reject-delay-time', str(cca.reject_delay_time))
            x_agent.set('busy-delay-time', str(cca.busy_delay_time))

        x_tiers = etree.SubElement(x_conf_name, 'tiers')
        ccts = CallCentreTiers.objects.all()
        for cct in ccts:
            x_tier = etree.SubElement(x_tiers, 'tier', agent=str(cct.agent_id.id), queue=str(cct.queue_id.id))
            x_tier.set('domain_name', cct.queue_id.domain_id.name)
            x_tier.set('level', str(cct.tier_level))
            x_tier.set('position', str(cct.tier_position))

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        cache.set(configuration_cache_key, xml)
        if self.debug:
            print(xml)
        return xml

    def GetCallcentreQueue(self, queue_id):
        x_root = self.XrootDynamic()
        x_section = etree.SubElement(x_root, "section", name='configuration')
        x_conf_name = etree.SubElement(x_section, 'configuration', name='callcenter.conf', description='Call Centre')
        x_settings = etree.SubElement(x_conf_name, 'settings')
        # dsn or dsn_callcenter can go in here if defined and/or required
        if self.cs_dsn:
            etree.SubElement(x_settings, 'param', name='odbc-dsn', value=self.cs_dsn)
        x_queues = etree.SubElement(x_conf_name, 'queues')
        ccq = CallCentreQueues.objects.get(pk=queue_id)
        x_queue = etree.SubElement(x_queues, 'queue', name=str(ccq.id), label='%s@%s' % (ccq.name.replace(' ', '-'), ccq.domain_id.name))
        etree.SubElement(x_queue, 'param', name='strategy', value=ccq.strategy)
        etree.SubElement(x_queue, 'param', name='moh-sound', value=ccq.moh_sound)
        if ccq.record_template:
            etree.SubElement(x_queue, 'param', name='record-template', value=ccq.record_template)
        etree.SubElement(x_queue, 'param', name='time-base-score', value=ccq.time_base_score)
        etree.SubElement(x_queue, 'param', name='max-wait-time', value=str(ccq.max_wait_time))
        etree.SubElement(x_queue, 'param', name='max-wait-time-with-no-agent', value=str(ccq.max_wait_time_na))
        etree.SubElement(x_queue, 'param', name='max-wait-time-with-no-agent-time-reached', value=str(ccq.max_wait_time_natr))
        etree.SubElement(x_queue, 'param', name='tier-rules-apply', value=ccq.tier_rules_apply)
        etree.SubElement(x_queue, 'param', name='tier-rule-wait-second', value=str(ccq.tier_rule_wait_sec))
        etree.SubElement(x_queue, 'param', name='tier-rule-wait-multiply-level', value=ccq.tier_rule_wm_level)
        etree.SubElement(x_queue, 'param', name='tier-rule-no-agent-no-wait', value=ccq.tier_rule_nanw)
        etree.SubElement(x_queue, 'param', name='discard-abandoned-after', value=str(ccq.discard_abndnd_after))
        etree.SubElement(x_queue, 'param', name='abandoned-resume-allowed', value=ccq.abndnd_resume_allowed)
        if ccq.announce_sound:
            etree.SubElement(x_queue, 'param', name='announce-sound', value=ccq.announce_sound)
        if ccq.announce_frequency:
            etree.SubElement(x_queue, 'param', name='announce-frequency', value=str(ccq.announce_frequency))

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        if self.debug:
            print(xml)
        return xml
