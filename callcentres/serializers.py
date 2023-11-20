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
    CallCentreQueues, CallCentreAgents, CallCentreTiers
)


class CallCentreQueuesSerializer(serializers.ModelSerializer):

    class Meta:
        model = CallCentreQueues
        fields = [
                    'url', 'id', 'domain_id',
                    'name',
                    'extension',
                    'greeting',
                    'strategy',
                    'moh_sound',
                    'record_template',
                    'time_base_score',
                    'max_wait_time',
                    'max_wait_time_na',
                    'max_wait_time_natr',
                    'timeout_action',
                    'tier_rules_apply',
                    'tier_rule_wait_sec',
                    'tier_rule_wm_level',
                    'tier_rule_nanw',
                    'discard_abndnd_after',
                    'abndnd_resume_allowed',
                    'cid_name_prefix',
                    'announce_sound',
                    'announce_frequency',
                    'cc_exit_keys',
                    'enabled',
                    'description',
                    'dialplan_id',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class CallCentreAgentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CallCentreAgents
        fields = [
                    'url', 'id', 'domain_id',
                    'name', 'user_uuid', 'agent_type', 'call_timeout', 'agent_id',
                    'agent_pin', 'contact', 'status', 'no_answer_delay_time', 'max_no_answer',
                    'wrap_up_time', 'reject_delay_time', 'busy_delay_time',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class CallCentreTiersSerializer(serializers.ModelSerializer):

    class Meta:
        model = CallCentreTiers
        fields = [
                    'url', 'id', 'queue_id', 'agent_id', 'tier_level', 'tier_position',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]
