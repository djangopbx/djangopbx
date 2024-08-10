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
import base64
import re
from django.db.models import Case, Value, When
from django.utils import timezone
from django.conf import settings
#import logging
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend

from .provisionfunctions import ProvisionFunctions
from tenants.pbxsettings import PbxSettings
from pbx.commonipfunctions import IpFunctions

from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    DeviceVendors, DeviceVendorFunctions, DeviceVendorFunctionGroups, DeviceProfiles,
    DeviceProfileSettings, DeviceProfileKeys, Devices, DeviceLines, DeviceKeys, DeviceSettings
)
from accounts.models import Extension
from contacts.models import Contact

from .serializers import (
    DeviceVendorsSerializer, DeviceVendorFunctionsSerializer, DeviceVendorFunctionGroupsSerializer,
    DeviceProfilesSerializer, DeviceProfileSettingsSerializer, DeviceProfileKeysSerializer,
    DevicesSerializer, DeviceLinesSerializer, DeviceKeysSerializer, DeviceSettingsSerializer
)


#logger = logging.getLogger(__name__)

class DeviceVendorsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows DeviceVendors to be viewed or edited.
    """
    queryset = DeviceVendors.objects.all().order_by('name')
    serializer_class = DeviceVendorsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'enabled']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)



class DeviceVendorFunctionsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows DeviceVendorFunctions to be viewed or edited.
    """
    queryset = DeviceVendorFunctions.objects.all().order_by('vendor_id', 'name')
    serializer_class = DeviceVendorFunctionsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['vendor_id', 'name', 'value', 'enabled']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class DeviceVendorFunctionGroupsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows DeviceVendorFunctionGroups to be viewed or edited.
    """
    queryset = DeviceVendorFunctionGroups.objects.all().order_by('function_id')
    serializer_class = DeviceVendorFunctionGroupsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['function_id', 'group_id']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class DeviceProfilesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows DeviceProfiles to be viewed or edited.
    """
    queryset = DeviceProfiles.objects.all().order_by('domain_id', 'vendor', 'name')
    serializer_class = DeviceProfilesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'vendor', 'name', 'enabled']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class DeviceProfileSettingsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows DeviceProfileSettings to be viewed or edited.
    """
    queryset = DeviceProfileSettings.objects.all().order_by('profile_id', 'name')
    serializer_class = DeviceProfileSettingsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['profile_id', 'name', 'value']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class DeviceProfileKeysViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows DeviceProfileKeys to be viewed or edited.
    """
    queryset = DeviceProfileKeys.objects.all().order_by('profile_id', 'key_id')
    serializer_class = DeviceProfileKeysSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['profile_id', 'category', 'value', 'extension', 'label']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class DevicesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Devices to be viewed or edited.
    """
    queryset = Devices.objects.all().order_by('domain_id', 'mac_address')
    serializer_class = DevicesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'mac_address', 'label', 'description', 'enabled']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class DeviceLinesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows DeviceLines to be viewed or edited.
    """
    queryset = DeviceLines.objects.all().order_by('device_id', 'line_number')
    serializer_class = DeviceLinesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['device_id', 'server_address', 'user_id', 'auth_id', 'enabled']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class DeviceKeysViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows DeviceKeys to be viewed or edited.
    """
    queryset = DeviceKeys.objects.all().order_by('device_id', 'key_id')
    serializer_class = DeviceKeysSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['device_id', 'key_type', 'value', 'extension', 'label']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class DeviceSettingsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows DeviceSettings to be viewed or edited.
    """
    queryset = DeviceSettings.objects.all().order_by('device_id', 'name')
    serializer_class = DeviceSettingsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['device_id', 'name', 'value', 'enabled']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


ipf = IpFunctions()

def chk_prov_auth(request, host, pbxs):
    realm = host
    domain = pbxs.get_domain(realm)
    if not domain:
        return (False, HttpResponseNotFound())
    http_auth_enabled = pbxs.dd_settings(str(domain.id), 'provision', 'http_auth_enabled', 'boolean', False, True)
    if not http_auth_enabled:
        return (False, HttpResponseNotFound())
    http_usr = pbxs.dd_settings(str(domain.id), 'provision', 'http_auth_username')
    if not http_usr:
        return (False, HttpResponseNotFound())
    http_pwd = pbxs.dd_settings(str(domain.id), 'provision', 'http_auth_password')
    if not http_pwd:
        return (False, HttpResponseNotFound())
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            # NOTE: We are only support basic authentication for now.
            #
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).decode('utf-8').split(':', 1)
                if uname == http_usr and passwd == http_pwd:
                    return (True, domain)
                else:
                    meta = request.META
                    ip = ipf.get_client_ip(meta)
                    if ip:
                        ipf.update_web_fail_ip(ip, uname)

    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
    return (False, response)

def device_config(request, *args, **kwargs):
    mac = None
    contacts = []
    host = request.META['HTTP_HOST']
    if ':' in host:
        host = host.split(':')[0]

    pbxs = PbxSettings()
    pf = ProvisionFunctions()

    pauth = chk_prov_auth(request, host, pbxs)
    print(pauth)
    if not pauth[0]:
        return pauth[1]

    if 'file' in kwargs:
        cfgfile = kwargs['file']
    else:
        cfgfile = 'mac.cfg'

    if 'mac' in kwargs:
        mac = kwargs['mac']

    if 'macboot' in kwargs:
        cfgfile = 'y000000000000.boot'

# Hard coded MAC for testing revove!!!!!!!!!!!!
#    mac = '001565a6699b'
    if not mac:
        p = re.compile(r'(?:[0-9a-fA-F]:?){12}')
        results = re.findall(p, request.META['HTTP_USER_AGENT'])
        if len(results) > 0:
            mac = results[0]

    if not mac:
        return HttpResponseNotFound()

    if not ':' in mac:
        mac = ':'.join(mac[i:i+2] for i in range(0,12,2))

    try:
        device = Devices.objects.get(domain_id_id=pauth[1].id, mac_address=mac.upper())
    except Devices.DoesNotExist:
        device = None

    if not device:
        return HttpResponseNotFound()
    if device.alternate_id:
        try:
            device = Devices.objects.get(pk=device.alternate_id)
        except Devices.DoesNotExist:
            device = None
    if not device:
        return HttpResponseNotFound()

    prov_template = os.path.join('provision/',device.template, cfgfile)
    if not os.path.isfile(os.path.join(settings.BASE_DIR, 'provision/templates', prov_template)):
        return HttpResponseNotFound()

    if 'contacts' in kwargs:
        contact_type = kwargs['contacts']
        if contact_type == 'users' or contact_type == 'groups':
            if not device.user_id:
                return HttpResponseNotFound()
            if  contact_type == 'users':
                qs = Contact.objects.filter(domain_id=device.domain_id, user_id=device.user_id, enabled='true')
            else:
                qs = Contact.objects.filter(domain_id=device.domain_id,
                    contactgroup__group_id__in=device.user_id.user.groups.all(), enabled='true')
            for q in qs:
                c_dict = {}
                c_dict['category'] = contact_type
                org = q.contactorg_set.first()
                if org:
                    c_dict['contact_organization'] = org.organisation_name
                c_dict['contact_name_given'] = q.given_name
                c_dict['contact_name_family'] = q.family_name
                c_dict['numbers'] = []
                ns = q.contacttel_set.all().order_by(
                        Case(
                         When(tel_type='pref', then=Value(1)),
                         When(tel_type='work', then=Value(2)),
                         When(tel_type='cell', then=Value(3)),
                         When(tel_type='home', then=Value(4)),
                         default=Value(100)
                        )
                    )
                for n in ns:
                    n_dict = {}
                    n_dict['phone_number'] = n.number
                    c_dict['numbers'].append(n_dict)
                contacts.append(c_dict)
        elif contact_type == 'extensions':
            qs = Extension.objects.filter(domain_id=device.domain_id, enabled='true')
            for q in qs:
                c_dict = {}
                c_dict['category'] = contact_type
                c_dict['effective_caller_id_name'] = q.effective_caller_id_name
                c_dict['phone_number'] = q.effective_caller_id_number
                c_dict['phone_extension'] = q.extension
                contacts.append(c_dict)
        else:
            return HttpResponseNotFound()


    # Get default settings, domain settings, then user settings, then device settings, lines and keys
    prov_lines = DeviceLines.objects.filter(enabled='true', device_id=device, auth_id__isnull=False).order_by('line_number')

    line_keys = pf.device_keys(device, 'line')
    memory_keys = pf.device_keys(device, 'memory')
    programmable_keys = pf.device_keys(device, 'programmable')
    expansion_1_keys = pf.device_keys(device, 'expansion-1')
    expansion_2_keys = pf.device_keys(device, 'expansion-2')
    expansion_3_keys = pf.device_keys(device, 'expansion-3')
    expansion_4_keys = pf.device_keys(device, 'expansion-4')
    expansion_5_keys = pf.device_keys(device, 'expansion-5')
    expansion_6_keys = pf.device_keys(device, 'expansion-6')

    prov_defs = {'domain_name': device.domain_id, 'mac': mac.replace(':', '')}
    prov_defs = pbxs.default_provision_settings(prov_defs)
    prov_defs = pbxs.domain_provision_settings(prov_defs, device.domain_id)
    if device.user_id:
        prov_defs = pbxs.user_provision_settings(prov_defs, device.user_id)

    if device.profile_id:
        prov_defs = pf.device_profile_settings(prov_defs, device.profile_id)

    prov_defs = pf.device_settings(prov_defs)

    device.provisioned_date = timezone.now()
    device.provisioned_method = request.scheme
    device.provisioned_ip = ipf.get_client_ip(request.META)
    device.save()

    # Set Content type
    contype = 'text/plain'
    if request.META['CONTENT_TYPE'] == 'application/octet-stream':
        h_dict = {
                    'Content-Description': 'File Transfer',
                    'Content-Disposition': 'attachment; filename="%s"' % cfgfile,
                    'Content-Transfer-Encoding': 'binary',
                    'Expires': 0,
                    'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
                    'Pragma': 'public'
                }
        return render(
            request, prov_template,
            {'prov_defs': prov_defs,
            'prov_lines': prov_lines,
            'line_keys': line_keys,
            'memory_keys': memory_keys,
            'programmable_keys': programmable_keys,
            'expansion_1_keys': expansion_1_keys,
            'expansion_2_keys': expansion_2_keys,
            'expansion_3_keys': expansion_3_keys,
            'expansion_4_keys': expansion_4_keys,
            'expansion_5_keys': expansion_5_keys,
            'expansion_6_keys': expansion_6_keys,
            'contacts': contacts
            }, 'application/octet-stream',
            200, 'uft-8', 'django', h_dict
            )
    else:
        # Add if statements here if you need a specific CONTENT-TYPE header for a device vendor.
        if device.vendor == 'something special':
            contype = 'text/plain'


    return render(
            request, prov_template,
            {'prov_defs': prov_defs,
            'prov_lines': prov_lines,
            'line_keys': line_keys,
            'memory_keys': memory_keys,
            'programmable_keys': programmable_keys,
            'expansion_1_keys': expansion_1_keys,
            'expansion_2_keys': expansion_2_keys,
            'expansion_3_keys': expansion_3_keys,
            'expansion_4_keys': expansion_4_keys,
            'expansion_5_keys': expansion_5_keys,
            'expansion_6_keys': expansion_6_keys,
            'contacts': contacts
            }, contype
            )

