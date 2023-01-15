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
from rest_framework import serializers
from .models import (
    Domain, Profile, DefaultSetting, DomainSetting, ProfileSetting
)


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Group
        fields = ['url', 'name']


class DomainSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Domain
        fields = ['url', 'name', 'enabled', 'description', 'created', 'updated', 'synchronised', 'updated_by']


class ProfileSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Profile
        fields = [
                    'url', 'domain_id', 'username', 'email', 'status', 'api_key',
                    'enabled', 'created', 'updated', 'synchronised', 'updated_by'
                ]


class DefaultSettingSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DefaultSetting
        fields = [
                    'url', 'id', 'app_uuid', 'category', 'subcategory',
                    'value_type', 'value', 'sequence', 'enabled',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class DomainSettingSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DomainSetting
        fields = [
                    'url', 'id', 'domain_id', 'app_uuid', 'category', 'subcategory',
                    'value_type', 'value', 'sequence', 'enabled',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class ProfileSettingSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ProfileSetting
        fields = [
                    'url', 'id', 'user_id', 'category', 'subcategory',
                    'value_type', 'value', 'sequence', 'enabled',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]
