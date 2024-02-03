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
    XmlCdr,
)


class XmlCdrSerializer(serializers.ModelSerializer):

    class Meta:
        model = XmlCdr
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                'url', 'id',
                'domain_id',
                'extension_id',
                'domain_name',
                'accountcode',
                'direction',
                'context',
                'caller_id_name',
                'caller_id_number',
                'caller_destination',
                'source_number',
                'destination_number',
                'start_epoch',
                'start_stamp',
                'answer_epoch',
                'answer_stamp',
                'end_epoch',
                'end_stamp',
                'duration',
                'mduration',
                'billsec',
                'billmsec',
                'bridge_uuid',
                'read_codec',
                'read_rate',
                'write_codec',
                'write_rate',
                'remote_media_ip',
                'network_addr',
                'record_path',
                'record_name',
                'leg',
                'pdd_ms',
                'rtp_audio_in_mos',
                'last_app',
                'last_arg',
                'missed_call',
                'cc_side',
                'cc_member_uuid',
                'cc_queue_joined_epoch',
                'cc_queue',
                'cc_member_session_uuid',
                'cc_agent_uuid',
                'cc_agent',
                'cc_agent_type',
                'cc_agent_bridged',
                'cc_queue_answered_epoch',
                'cc_queue_terminated_epoch',
                'cc_queue_canceled_epoch',
                'cc_cancel_reason',
                'cc_cause',
                'waitsec',
                'conference_name',
                'conference_uuid',
                'conference_member_id',
                'digits_dialed',
                'pin_number',
                'hangup_cause',
                'hangup_cause_q850',
                'sip_hangup_disposition',
                'xml',
                'json',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]
