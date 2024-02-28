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
from django.core.cache import cache
from django.db.models import CharField, Value as V
from django.db.models.functions import Concat
from lxml import etree
from pbx.fscmdabslayer import FsCmdAbsLayer
from .models import Gateway, Bridge, ExtensionUser
from provision.models import Devices, DeviceLines
from django.contrib.auth.models import User, Group
from tenants.pbxsettings import PbxSettings


class AccountFunctions():

    def list_gateways(self, domain_id=None, gw_global=False):
        if gw_global:
            return Gateway.objects.filter(enabled='true', domain_id__isnull=True).values_list('id', 'gateway').order_by('gateway')
        if domain_id:
            return Gateway.objects.filter(
                domain_id=uuid.UUID(domain_id),
                enabled='true'
                ).values_list('id', 'gateway').order_by('gateway')
        else:
            return Gateway.objects.filter(enabled='true').values_list('id', 'gateway').order_by('gateway')

    def list_bridges(self, domain_id=None):
        if domain_id:
            return Bridge.objects.filter(
                domain_id=uuid.UUID(domain_id),
                enabled='true').annotate(
                full_dest=Concat(V('bridge:'), 'destination', output_field=CharField())
                ).values_list('full_dest', 'name').order_by('name')
        else:
            return Bridge.objects.filter(
                enabled='true').annotate(
                full_dest=Concat(V('bridge:'), 'destination', output_field=CharField())
                ).values_list('full_dest', 'name').order_by('name')

    def list_user_extensions(self, domain_id, user_uuid):
        return ExtensionUser.objects.filter(
            extension_id__domain_id=uuid.UUID(domain_id),
            user_uuid=uuid.UUID(user_uuid)
            ).values_list('extension_id__extension', flat=True)

    def list_superuser_extensions(self, domain_id):
        return ExtensionUser.objects.filter(
            extension_id__domain_id=uuid.UUID(domain_id)
            ).order_by('extension_id__extension').values_list('extension_id__extension', flat=True)

    def list_user_extensions_uuid(self, domain_id, user_uuid):
        return ExtensionUser.objects.filter(
            extension_id__domain_id=uuid.UUID(domain_id),
            user_uuid=uuid.UUID(user_uuid)
            ).values_list('extension_id', flat=True)

    def list_superuser_extensions_uuid(self, domain_id):
        return ExtensionUser.objects.filter(
            extension_id__domain_id=uuid.UUID(domain_id)
            ).order_by('extension_id__extension').values_list('extension_id', flat=True)

    def gateway_type(self, gateway):
        gateway_type = 'gateway'
        if gateway[:6] == 'bridge':
            gateway_type = 'bridge'
        if gateway[:4] == 'enum':
            gateway_type = 'enum'
        if gateway[:7] == 'freetdm':
            gateway_type = 'freetdm'
        if gateway[: 8] == 'transfer':
            gateway_type = 'transfer'
        if gateway[:4] == 'xmpp':
            gateway_type = 'xmpp'
        return gateway_type

    def gateway_bridge_data(self, gateway, gateway_type, prefix):
        if gateway_type == 'gateway':
            bridge_data = 'sofia/gateway/%s/%s$1' % (gateway, prefix)

        if gateway_type == 'freetdm':
            bridge_data = '%s/1/a/%s$1' % (gateway, prefix)

        if gateway_type == 'xmpp':
            bridge_data = 'dingaling/gtalk/+%s$1@voice.google.com' % prefix

        if gateway_type == 'bridge':
            parts = gateway.split(':')
            bridge_data = parts[1]

        if gateway_type == 'enum':
            bridge_data = '${enum_auto_route}'

        if gateway_type == 'transfer':
            parts = gateway.split(':')
            bridge_data = parts[1]

        return bridge_data

    def write_gateway_xml(self, gw):
        xml = ''

        conflist = PbxSettings().default_settings('switch', 'sip_profiles', 'dir')
        if conflist:
            confdir = conflist[0]

            root = etree.Element('include')
            gateway = etree.SubElement(root, 'gateway', name=str(gw.id))
            if gw.username:
                etree.SubElement(gateway, 'param', name='username', value=gw.username)
            if gw.distinct_to:
                etree.SubElement(gateway, 'param', name='distinct-to', value=gw.distinct_to)
            if gw.auth_username:
                etree.SubElement(gateway, 'param', name='auth-username', value=gw.auth_username)
            if gw.password:
                etree.SubElement(gateway, 'param', name='password', value=gw.password)
            if gw.realm:
                etree.SubElement(gateway, 'param', name='realm', value=gw.realm)
            if gw.from_user:
                etree.SubElement(gateway, 'param', name='from-user', value=gw.from_user)
            if gw.from_domain:
                etree.SubElement(gateway, 'param', name='from-domain', value=gw.from_domain)
            if gw.proxy:
                etree.SubElement(gateway, 'param', name='proxy', value=gw.proxy)
            if gw.register_proxy:
                etree.SubElement(gateway, 'param', name='register-proxy', value=gw.register_proxy)
            if gw.outbound_proxy:
                etree.SubElement(gateway, 'param', name='outbound-proxy', value=gw.outbound_proxy)
            if gw.expire_seconds:
                etree.SubElement(gateway, 'param', name='expire-seconds', value=str(gw.expire_seconds))
            if gw.register:
                etree.SubElement(gateway, 'param', name='register', value=gw.register)
            if gw.register_transport:
                if gw.register_transport == 'udp':
                    etree.SubElement(gateway, 'param', name='register-transport', value=gw.rgister_transport)
                elif gw.register_transport == 'tcp':
                    etree.SubElement(gateway, 'param', name='register-transport', value=gw.rgister_transport)
                elif gw.register_transport == 'tls':
                    etree.SubElement(gateway, 'param', name='register-transport', value=gw.rgister_transport)
                    etree.SubElement(gateway, 'param', name='contact-params', value='transport=tls')
                else:
                    etree.SubElement(gateway, 'param', name='register-transport', value='udp')

            if gw.retry_seconds:
                etree.SubElement(gateway, 'param', name='retry-seconds', value=str(gw.retry_seconds))
            if gw.extension:
                etree.SubElement(gateway, 'param', name='extension', value=gw.extension)
            if gw.ping:
                etree.SubElement(gateway, 'param', name='ping', value=gw.ping)
            if gw.context:
                etree.SubElement(gateway, 'param', name='context', value=gw.context)
            if gw.caller_id_in_from:
                etree.SubElement(gateway, 'param', name='caller-id-in-from', value=gw.caller_id_in_from)
            if gw.supress_cng:
                etree.SubElement(gateway, 'param', name='supress-cng', value=gw.supress_cng)
            if gw.extension_in_contact:
                etree.SubElement(gateway, 'param', name='extension-in-contact', value=gw.extension_in_contact)
            etree.SubElement(gateway, 'variables')

            if gw.sip_cid_type:
                etree.SubElement(gateway, 'param', name='sip-cid-type', value=gw.sip_cid_type)

            etree.indent(root)
            xml = str(etree.tostring(root), "utf-8")
            try:
                os.makedirs('%s/%s' % (confdir, gw.profile), mode=0o755, exist_ok=True)
            except OSError:
                return -2

            try:
                with open('%s/%s/%s.xml' % (confdir, gw.profile, str(gw.id)), 'w') as f:
                    f.write(xml)
            except OSError:
                return -3

            return 1
        else:
            return -1


class GatewayFunctions():
    esconnected = False
    configuration_cache_key = 'configuration:sofia.conf'

    def __init__(self):
        self.esconnected = False
        self.es = FsCmdAbsLayer()
        self.es_connect()

    def rescan_sofia_profile(self, profile):
        cache.delete(self.configuration_cache_key)
        cmd = 'api sofia profile %s rescan' % profile
        if self.esconnected:
            self.es.clear_responses()
            self.es.send(cmd)
            self.es.process_events()
            res = self.es.get_responses()
            if res:
                return 1
        return -1

    def sofia_stop_gateway(self, profile, gateway_id):
        cmd = 'api sofia profile %s killgw %s' % (profile, gateway_id)
        result = self.es.send(cmd)
        if self.esconnected:
            self.es.clear_responses()
            self.es.send(cmd)
            self.es.process_events()
            res = self.es.get_responses()
            if res:
                return 1
        return -1

    def es_disconnect(self):
        self.es.disconnect()
        self.esconnected = False

    def es_connect(self):
        if self.es.connect():
            self.esconnected = True


class ExtRelatedFunctions():

    def create_user(self, obj, request):
        ret = 0
        username = '%s@%s' % (obj.extension, obj.domain_id.name)
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username, username, obj.password)
            user.first_name = obj.effective_caller_id_name.replace (' ', '-')
            user.last_name = obj.effective_caller_id_number
            user.save()
            ret = 1
            user_group = Group.objects.get(name='user')
            if user_group:
                user_group.user_set.add(user)
            user.profile.domain_id = obj.domain_id
            user.profile.username = username
            user.profile.enabled = 'true'
            user.profile.updated_by = request.user.username
            user.profile.save()
            ExtensionUser.objects.create(
                extension_id = obj,
                user_uuid = user.profile,
                updated_by = request.user.username
            )
        return ret

    def create_device(self, obj, request):
        ret = 0
        user = None
        mac = ':'.join(str(uuid.uuid4())[24:].upper()[i:i+2] for i in range(0,12,2))
        if not Devices.objects.filter(domain_id=obj.domain_id_id, label=obj.extension).exists():
            extuser = obj.extensionuser.filter(default_user='true').first()
            ret = 1
            if extuser:
                user = extuser.user_uuid
            device = Devices.objects.create(
                domain_id=obj.domain_id,
                user_id=user,
                mac_address=mac,
                label=obj.extension,
                updated_by=request.user.username
            )
        DeviceLines.objects.create(
                device_id=device,
                line_number=1,
                server_address=obj.domain_id,
                display_name=obj.extension,
                user_id=obj.extension,
                auth_id=obj.extension,
                password=obj.password
        )
        return ret
