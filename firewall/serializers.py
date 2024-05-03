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

from django.utils.translation import gettext_lazy as _
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers

ip_type_choices = [
    'ipv4_addr',
    'ipv6_addr'
]

fw_list_choices = [
    'ipv4_white_list',
    'ipv6_white_list',
    'ipv4_sip_gateway_list',
    'ipv6_sip_gateway_list',
    'ipv4_sip_customer_list',
    'ipv6_sip_customer_list',
    'ipv4_web_block_list',
    'ipv6_web_block_list'
]


class FwGenericSerializer(serializers.Serializer):

    url        = serializers.SerializerMethodField()                                            # noqa: E501, E221
    id         = serializers.CharField(source='ip_address', initial='0.0.0.0', read_only=True)  # noqa: E501, E221
    fw_list    = serializers.ChoiceField(label=_('Firewall List Name'), choices=fw_list_choices)# noqa: E501, E221
    ip_type    = serializers.ChoiceField(label=_('IP Address Type'), choices=ip_type_choices)   # noqa: E501, E221
    ip_address = serializers.IPAddressField(label=_('IP Address'), protocol='both')             # noqa: E501, E221
    suffix     = serializers.IntegerField(label=_('Subnet Mask'), required=False, min_value=0, max_value=128, help_text=_('Not required, but could be 24 or 64 etc.')) # noqa: E501, E221

    def get_url(self, obj):
        ip_address = ''
        ipobj = obj.get('ip_address')
        if type(ipobj) is str:
            ip_address = ipobj
        if type(ipobj) is dict:
            try:
                ip_address = '%s/%s' % (ipobj['prefix']['addr'], ipobj['prefix']['len'])
            except:
                ip_address = 'Invalid'
        r = '%s&%s&%s' % (obj.get('ip_type'), obj.get('fw_list'), ip_address)
        return self.context['request'].build_absolute_uri('%s/' % urlsafe_base64_encode(r.encode()))

    def create(self, validated_data):
        return validated_data


class FwCountersSerializer(serializers.Serializer):

    url     = serializers.SerializerMethodField()       # noqa: E501, E221
    id      = serializers.CharField(source='counter')   # noqa: E501, E221
    counter = serializers.CharField(label=_('Counter')) # noqa: E501, E221
    packets = serializers.CharField(label=_('Packets')) # noqa: E501, E221
    bytes   = serializers.CharField(label=_('Bytes'))   # noqa: E501, E221

    def get_url(self, obj):
        r = '%s&%s&%s' % (obj.get('counter'), obj.get('packets'), obj.get('bytes'))
        return self.context['request'].build_absolute_uri('%s/' % urlsafe_base64_encode(r.encode()))
