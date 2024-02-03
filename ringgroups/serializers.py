#
#    DjangoPBX
#
#    MIT License
#
#    Copyright (c) 2016 - 2023 Adrian Fretwell <adrian@djangopbx.com>
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
    RingGroup, RingGroupDestination, RingGroupUser,
)


class RingGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = RingGroup
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                'url', 'id',
                'domain_id',
                'name',
                'extension',
                'greeting',
                'strategy',
                'timeout_app',
                'timeout_data',
                'call_timeout',
                'caller_id_name',
                'caller_id_number',
                'cid_name_prefix',
                'cid_number_prefix',
                'distinctive_ring',
                'ring_group_ringback',
                'follow_me_enabled',
                'missed_call_app',
                'missed_call_data',
                'forward_enabled',
                'forward_destination',
                'forward_toll_allow',
                'context',
                'enabled',
                'description',
                'dialplan_id',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class RingGroupDestinationSerializer(serializers.ModelSerializer):

    class Meta:
        model = RingGroupDestination
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                'url', 'id',
                'ring_group_id',
                'number',
                'delay',
                'timeout',
                'destination_prompt',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class RingGroupUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = RingGroupUser
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                'url', 'id',
                'ring_group_id',
                'user_uuid',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]
