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

from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _


class XmlCdr(models.Model):
    id                        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Call Detail Record'))
    domain_id                 = models.ForeignKey('tenants.Domain', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))
    extension_id              = models.ForeignKey('accounts.Extension', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Extension'))
    domain_name               = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Domain Name'))
    accountcode               = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Account Code'))
    direction                 = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Direction'))
    context                   = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Context'))
    caller_id_name            = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Caller ID Name'))
    caller_id_number          = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Caller ID Number'))
    caller_destination        = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Destination'))
    source_number             = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Source Number'))
    destination_number        = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('destination Number'))
    start_epoch               = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('Start Epoch'))
    start_stamp               = models.DateTimeField(blank=True, null=True, verbose_name=_('Start Date'))
    answer_epoch              = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('Answer Epoch'))
    answer_stamp              = models.DateTimeField(blank=True, null=True, verbose_name=_('Answer Date'))
    end_epoch                 = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('End Epoch'))
    end_stamp                 = models.DateTimeField(blank=True, null=True, verbose_name=_('End Date'))
    duration                  = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('Duration'))
    mduration                 = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('mSec Duration'))
    billsec                   = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('Bill Seconds'))
    billmsec                  = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('Bill mSeconds'))
    bridge_uuid               = models.UUIDField(blank=True, null=True, verbose_name=_('Bridge UUID'))
    read_codec                = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Read Codec'))
    read_rate                 = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Read Rate'))
    write_codec               = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Write Codec'))
    write_rate                = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Write Rate'))
    remote_media_ip           = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Remote Media IP'))
    network_addr              = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Network Address'))
    record_path               = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Record Path'))
    record_name               = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Record Name'))
    leg                       = models.CharField(max_length=8, blank=True, null=True, verbose_name=_('Leg'))
    pdd_ms                    = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('PDD'))
    rtp_audio_in_mos          = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name=_('MOS'))
    last_app                  = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Last App.'))
    last_arg                  = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Last Arg.'))
    missed_call               = models.BooleanField(blank=True, null=True, verbose_name=_('Missed Call'))
    cc_side                   = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('CC Side'))
    cc_member_uuid            = models.UUIDField(blank=True, null=True, verbose_name=_('CC Member UUID'))
    cc_queue_joined_epoch     = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('CC Joined Epoch'))
    cc_queue                  = models.UUIDField(blank=True, null=True, verbose_name=_('CC Queue UUID'))
    cc_member_session_uuid    = models.UUIDField(blank=True, null=True, verbose_name=_('CC Member Session UUID'))
    cc_agent_uuid             = models.UUIDField(blank=True, null=True, verbose_name=_('CC Agent UUID'))
    cc_agent                  = models.UUIDField(blank=True, null=True, verbose_name=_('CC Agent'))
    cc_agent_type             = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('CC Agent Type'))
    cc_agent_bridged          = models.CharField(max_length=8, blank=True, null=True, verbose_name=_('CC Agent Bridged'))
    cc_queue_answered_epoch   = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('CC Queue Answered Epoch'))
    cc_queue_terminated_epoch = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('CC Queue Terminated Epoch'))
    cc_queue_canceled_epoch   = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('CC Queue Cancelled Epoch'))
    cc_cancel_reason          = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('CC Cancel Reason'))
    cc_cause                  = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('CC Cause'))
    waitsec                   = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('Wait Seconds'))
    conference_name           = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Conference Name'))
    conference_uuid           = models.UUIDField(blank=True, null=True, verbose_name=_('Conference UUID'))
    conference_member_id      = models.CharField(max_length=8, blank=True, null=True, verbose_name=_('Conference Member ID'))
    digits_dialed             = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Digits Dialled'))
    pin_number                = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('PIN Number'))
    hangup_cause              = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Hangup Cause'))
    hangup_cause_q850         = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True, verbose_name=_('Hangup Cause Q.850'))
    sip_hangup_disposition    = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('SIP Hangup Disposition'))
    xml                       = models.TextField(blank=True, null=True, verbose_name=_('XML'))
    json                      = models.JSONField(blank=True, null=True, verbose_name=_('json'))
    created                   = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated                   = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised              = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by                = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        db_table = 'pbx_xml_cdr'

    def __str__(self):
        return str(id)
