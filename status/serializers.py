#
#    DjangoPBX
#
#    MIT License
#
#    Copyright (c) 2016 - 2024 Adrian Fretwell <adrian@djangopbx.com>
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

        r = '%s|%s|%s|%s' % (obj.get('reg_user'), obj.get('realm'), sip_profile, obj.get('hostname'))
        return self.context['request'].build_absolute_uri('%s/' % urlsafe_base64_encode(r.encode()))
