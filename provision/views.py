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

import base64
import re
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


def chk_prov_auth(request, host, pbxs):
    realm = host
    if ':' in host:
        realm = host.split(':')[0]

    domain = pbxs.get_domain(realm)
    if not domain:
        return (False, HttpResponseNotFound())

    http_auth_enabled = pbxs.dd_settings(str(domain.id), 'provision', 'http_auth_enabled', 'boolean', 'false', True)[0]
    if http_auth_enabled == 'false':
        return (False, HttpResponseNotFound())

    if not http_auth_enabled == 'true':
        return (False, HttpResponseNotFound())

    http_usr = pbxs.dd_settings(str(domain.id), 'provision', 'http_auth_username')
    if http_usr:
        http_usr = http_usr[0]
    else:
        return (False, HttpResponseNotFound())

    http_pwd = pbxs.dd_settings(str(domain.id), 'provision', 'http_auth_password')
    if http_pwd:
        http_pwd = http_pwd[0]
    else:
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
                    ip = IpFunctions().get_client_ip(meta)
                    if ip:
                        IpFunctions().update_web_fail_ip(ip, uname)

    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
    return (False, response)

def device_config(request, *args, **kwargs):
    mac = None
    host = request.META['HTTP_HOST']
    if ':' in host:
        host = host.split(':')[0]

    pbxs = PbxSettings()
    pf = ProvisionFunctions()

    pauth = chk_prov_auth(request, host, pbxs)
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

    # Get default settings, domain settings, then user settings, then device settings, lines and keys
    prov_lines = DeviceLines.objects.filter(enabled='true', device_id=device).order_by('line_number')

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
            request, 'provision/%s/%s' % (device.template, cfgfile),
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
            'expansion_6_keys': expansion_6_keys
            }, 'application/octet-stream',
            200, 'uft-8', 'django', h_dict
            )
    else:
        # Add if statements here if you need a specific CONTENT-TYPE header for a device vendor.
        if device.vendor == 'something special':
            contype = 'text/plain'


    return render(
            request, 'provision/%s/%s' % (device.template, cfgfile),
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
            'expansion_6_keys': expansion_6_keys
            }, contype
            )

