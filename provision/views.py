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

import logging
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend

from tenants.pbxsettings import PbxSettings

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


logger = logging.getLogger(__name__)

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



def device_config(request):
    pass