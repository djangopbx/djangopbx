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
    Dialplan, DialplanDetail,
)
from .inboundroute import InboundRoute
from .outboundroute import OutboundRoute

STATUS = (
    'true',
    'false',
)


class DialplanSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dialplan
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'url', 'id', 'domain_id', 'app_id', 'hostname', 'context',
                    'category', 'name', 'number', 'destination', 'dp_continue',
                    'xml', 'sequence', 'enabled', 'description',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class DialplanDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = DialplanDetail
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'url', 'id', 'dialplan_id', 'tag', 'type', 'data',
                    'dp_break', 'inline', 'group', 'sequence',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class InboundRouteSerializer(serializers.Serializer):

    url                   = serializers.SerializerMethodField()                                                   # noqa: E501, E221
    id                    = serializers.UUIDField(read_only=True)                                                 # noqa: E501, E221
    domain_id             = serializers.CharField(max_length=128, required=True, initial='djangopbx.com')         # noqa: E501, E221
    current_xml           = serializers.CharField(source='xml', read_only=True)                                   # noqa: E501, E221
    prefix                = serializers.CharField(max_length=16, required=False)                                  # noqa: E501, E221
    number                = serializers.CharField(max_length=128, required=True)                                  # noqa: E501, E221
    context               = serializers.CharField(max_length=128, initial='public', required=True)                # noqa: E501, E221
    application           = serializers.CharField(max_length=64, initial='transfer', required=True)               # noqa: E501, E221
    data                  = serializers.CharField(max_length=128, initial='201 XML djangopbx.com', required=True) # noqa: E501, E221
    caller_id_name_prefix = serializers.CharField(max_length=32, required=False)                                  # noqa: E501, E221
    record                = serializers.ChoiceField(choices=STATUS, initial='false', default='false')             # noqa: E501, E221
    account_code          = serializers.CharField(max_length=32, required=False)                                  # noqa: E501, E221
    enabled               = serializers.ChoiceField(choices=STATUS, default='true')                               # noqa: E501, E221
    description           = serializers.CharField(max_length=254, required=False)                                 # noqa: E501, E221

    def get_url(self, obj):
        if hasattr(obj, 'id'):
            if obj.id:
                return self.context['request'].build_absolute_uri('/api/dialplan_ib_route/%s/' % obj.id)
        return self.context['request'].build_absolute_uri('/api/dialplan_ib_route/')

    def create(self, validated_data):
        return InboundRoute(id=None, **validated_data)

    def update(self, instance, validated_data):
        return instance


class OutboundRouteSerializer(serializers.Serializer):

    url                   = serializers.SerializerMethodField()                                            # noqa: E501, E221
    id                    = serializers.UUIDField(read_only=True)                                          # noqa: E501, E221
    domain_id             = serializers.CharField(max_length=128, required=True, initial='djangopbx.com')  # noqa: E501, E221
    current_xml           = serializers.CharField(source='xml', read_only=True)                            # noqa: E501, E221
    name                  = serializers.CharField(max_length=64, required=True)                            # noqa: E501, E221
    gateway_1             = serializers.CharField(max_length=128, required=True)                           # noqa: E501, E221
    gateway_2             = serializers.CharField(max_length=128, required=False)                          # noqa: E501, E221
    gateway_3             = serializers.CharField(max_length=128, required=False)                          # noqa: E501, E221
    number                = serializers.CharField(max_length=128, required=True)                           # noqa: E501, E221
    prefix                = serializers.CharField(max_length=16, required=False)                           # noqa: E501, E221
    limit                 = serializers.IntegerField(min_value=0, default=0, initial=0)                    # noqa: E501, E221
    account_code          = serializers.CharField(max_length=32, required=False)                           # noqa: E501, E221
    toll_allow            = serializers.CharField(max_length=128, required=False)                          # noqa: E501, E221
    pin_numbers           = serializers.ChoiceField(choices=STATUS, initial='false', default='false')      # noqa: E501, E221
    sequence              = serializers.IntegerField(min_value=100, initial=101, default=101)              # noqa: E501, E221
    enabled               = serializers.ChoiceField(choices=STATUS, default='true')                        # noqa: E501, E221
    description           = serializers.CharField(max_length=254, required=False)                          # noqa: E501, E221

    def get_url(self, obj):
        if hasattr(obj, 'id'):
            if obj.id:
                return self.context['request'].build_absolute_uri('/api/dialplan_ob_route/%s/' % obj.id)
        return self.context['request'].build_absolute_uri('/api/dialplan_ob_route/')

    def create(self, validated_data):
        return OutboundRoute(id=None, **validated_data)

    def update(self, instance, validated_data):
        return instance

