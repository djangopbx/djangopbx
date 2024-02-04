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

from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers
from .models import (
    SipProfileDomain, SipProfileSetting, SipProfile, SwitchVariable, AccessControl,
    AccessControlNode, EmailTemplate, Modules
)


class SipProfileDomainSerializer(serializers.ModelSerializer):

    class Meta:
        model = SipProfileDomain
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'url', 'id', 'sip_profile_id', 'name', 'alias', 'parse',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class SipProfileSettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = SipProfileSetting
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'url', 'sip_profile_id', 'name', 'value', 'enabled', 'description', 'id',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class SipProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = SipProfile
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'url', 'id', 'name', 'hostname', 'enabled', 'description',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class SwitchVariableSerializer(serializers.ModelSerializer):

    class Meta:
        model = SwitchVariable
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'url', 'id', 'category', 'name', 'value', 'command', 'hostname',
                    'enabled', 'sequence', 'description',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class AccessControlSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccessControl
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'url', 'id', 'name', 'default', 'description',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class AccessControlNodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccessControlNode
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'url', 'id', 'access_control_id', 'type', 'cidr', 'domain', 'description',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class EmailTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailTemplate
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'url', 'id', 'domain_id', 'language', 'category', 'subcategory',
                    'subject', 'type', 'body', 'enabled', 'description',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class ModulesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Modules
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'url', 'id', 'label', 'name', 'category', 'name',
                    'sequence', 'enabled', 'default_enabled', 'description',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class FsRegistrationsSerializer(serializers.Serializer):

    url               = serializers.SerializerMethodField()               # noqa: E501, E221
    id                = serializers.UUIDField(source='registration_uuid') # noqa: E501, E221
    reg_user          = serializers.CharField()                           # noqa: E501, E221
    realm             = serializers.CharField()                           # noqa: E501, E221
    token             = serializers.CharField()                           # noqa: E501, E221
    reg_url           = serializers.CharField(source='url')               # noqa: E501, E221
    expires           = serializers.DateTimeField()                       # noqa: E501, E221
    network_ip        = serializers.IPAddressField(protocol='both')       # noqa: E501, E221
    network_port      = serializers.IntegerField()                        # noqa: E501, E221
    network_proto     = serializers.CharField()                           # noqa: E501, E221
    hostname          = serializers.CharField()                           # noqa: E501, E221
    metadata          = serializers.CharField()                           # noqa: E501, E221
    registration_uuid = serializers.UUIDField()                           # noqa: E501, E221

    def get_url(self, obj):
        try:
            sip_profile = obj.get('url').split('/')[1]
        except:
            sip_profile = 'internal'

        r = '%s@%s::%s::%s' % (obj.get('reg_user'), obj.get('realm'), obj.get('hostname'), sip_profile)
        return self.context['request'].build_absolute_uri('%s/' % urlsafe_base64_encode(r.encode()))
