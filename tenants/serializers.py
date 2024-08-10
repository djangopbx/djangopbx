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

from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import (
    Domain, Profile, DefaultSetting, DomainSetting, ProfileSetting
)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'url', 'username', 'email', 'groups']
        depth = 1


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ['id', 'url', 'name']


class DomainSerializer(serializers.ModelSerializer):

    class Meta:
        model = Domain
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = ['id', 'url', 'name', 'portal_name', 'home_switch', 'menu_id', 'enabled',
                    'description', 'created', 'updated', 'synchronised', 'updated_by']


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'id', 'url', 'domain_id', 'username', 'email', 'status', 'api_key',
                    'enabled', 'created', 'updated', 'synchronised', 'updated_by'
                ]


class DefaultSettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = DefaultSetting
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'id', 'url', 'app_uuid', 'category', 'subcategory',
                    'value_type', 'value', 'sequence', 'enabled',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class DomainSettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = DomainSetting
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'id', 'url', 'domain_id', 'app_uuid', 'category', 'subcategory',
                    'value_type', 'value', 'sequence', 'enabled',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class ProfileSettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileSetting
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'id', 'url', 'user_id', 'category', 'subcategory',
                    'value_type', 'value', 'sequence', 'enabled',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class GenericItemValueSerializer(serializers.Serializer):

    url     = serializers.SerializerMethodField()          # noqa: E501, E221
    id      = serializers.CharField(source='item')         # noqa: E501, E221
    item    = serializers.CharField(label=_('Item'))       # noqa: E501, E221
    value   = serializers.CharField(label=_('Value'))      # noqa: E501, E221

    def get_url(self, obj):
        if self.context['request'].get_full_path().endswith('/%s/' % obj.get('item')):
            return self.context['request'].build_absolute_uri(None)
        return self.context['request'].build_absolute_uri('%s/' % obj.get('item'))
