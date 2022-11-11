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

from  rest_framework  import serializers
from .models import (
    Extension,  Gateway,
)


class ExtensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extension
        fields =['url', 'id', 'domain_id', 
                'extension',
                'number_alias',
                'password',
                'accountcode',
                'effective_caller_id_name',
                'effective_caller_id_number',
                'outbound_caller_id_name',
                'outbound_caller_id_number',
                'emergency_caller_id_name',
                'emergency_caller_id_number',
                'directory_first_name',
                'directory_last_name',
                'directory_visible',
                'directory_exten_visible',
                'limit_max',
                'limit_destination',
                'missed_call_app',
                #'missed_call_data',
                'toll_allow',
                'call_timeout',
                'call_group',
                'call_screen_enabled',
                'user_record',
                'hold_music',
                'user_context',
                'enabled',
                'description',
                'auth_acl',
                'cidr',
                'sip_force_contact',
                #'nibble_account',
                'sip_force_expires',
                'mwi_account',
                'sip_bypass_media',
                #'unique_id',
                'absolute_codec_string',
                'force_ping',
                'dial_string',
                'forward_all_enabled',
                'forward_all_destination',
                'forward_busy_enabled',
                'forward_busy_destination',
                'forward_no_answer_enabled',
                'forward_no_answer_destination',
                'forward_user_not_registered_destination',
                'forward_user_not_registered_enabled',
                #'dial_user',
                #'dial_domain',
                'forward_caller_id',
                #'follow_me_uuid',
                'follow_me_enabled',
                #'follow_me_destinations',
                'do_not_disturb',
                'created', 'updated', 'synchronised', 'updated_by']


class GatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gateway
        fields =['url', 'id', 'domain_id', 
                'gateway',
                'username',
                'password',
                'distinct_to',
                'auth_username',
                'realm',
                'from_user',
                'from_domain',
                'proxy',
                'register_proxy',
                'outbound_proxy',
                'expire_seconds',
                'register',
                'register_transport',
                'retry_seconds',
                'extension',
                'ping',
                'caller_id_in_from',
                'supress_cng',
                'sip_cid_type',
                'codec_prefs',
                'channels',
                'extension_in_contact',
                'context',
                'profile',
                'hostname',
                'enabled',
                'description',
                'created', 'updated', 'synchronised', 'updated_by']

