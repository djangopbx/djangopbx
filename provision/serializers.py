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

from rest_framework import serializers
from .models import (
    DeviceVendors, DeviceVendorFunctions, DeviceVendorFunctionGroups, DeviceProfiles,
    DeviceProfileSettings, DeviceProfileKeys, Devices, DeviceLines, DeviceKeys, DeviceSettings
)


class DeviceVendorsSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceVendors
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                'url', 'id',
                'name', 'description', 'enabled',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class DeviceVendorFunctionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceVendorFunctions
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                'url', 'id',
                'vendor_id', 'name', 'value', 'description', 'enabled',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class DeviceVendorFunctionGroupsSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceVendorFunctionGroups
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                'url', 'id',
                'function_id', 'group_id',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class DeviceProfilesSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceProfiles
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                'url', 'id',
                'name', 'vendor', 'domain_id', 'enabled', 'description',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class DeviceProfileSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceProfileSettings
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                'url', 'id',
                'profile_id', 'name', 'value', 'description', 'enabled',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class DeviceProfileKeysSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceProfileKeys
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                'url', 'id',
                'profile_id', 'category', 'key_id', 'key_type', 'line', 'value',
                'extension', 'protected', 'label', 'icon'
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class DevicesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Devices
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                'url', 'id',
                'mac_address', 'label', 'model',
                'template', 'profile_id', 'user_id', 'username', 'password',
                'alternate_id', 'vendor', 'domain_id', 'enabled', 'description',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class DeviceLinesSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceLines
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                'url', 'id',
                'device_id', 'line_number', 'server_address',
                'server_address_primary', 'server_address_secondary',
                'outbound_proxy_primary', 'outbound_proxy_secondary',
                'display_name', 'user_id', 'auth_id', 'password',
                'sip_port', 'sip_transport', 'register_expires', 'shared_line',
                'enabled',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class DeviceKeysSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceKeys
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                'url', 'id',
                'device_id', 'category', 'key_id', 'key_type', 'line', 'value',
                'extension', 'protected', 'label', 'icon',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class DeviceSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceSettings
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                'url', 'id',
                'device_id', 'name', 'value', 'description', 'enabled',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]
