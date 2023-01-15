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
    id                        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Call Detail Record'))              # noqa: E501, E221
    domain_id                 = models.ForeignKey('tenants.Domain', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))            # noqa: E501, E221
    extension_id              = models.ForeignKey('accounts.Extension', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Extension'))     # noqa: E501, E221
    domain_name               = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Domain Name'))                                    # noqa: E501, E221
    accountcode               = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Account Code'))                                    # noqa: E501, E221
    direction                 = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Direction'))                                       # noqa: E501, E221
    context                   = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Context'))                                        # noqa: E501, E221
    caller_id_name            = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Caller ID Name'))                                  # noqa: E501, E221
    caller_id_number          = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Caller ID Number'))                                # noqa: E501, E221
    caller_destination        = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Destination'))                                     # noqa: E501, E221
    source_number             = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Source Number'))                                   # noqa: E501, E221
    destination_number        = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('destination Number'))                              # noqa: E501, E221
    start_epoch               = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('Start Epoch'))                # noqa: E501, E221
    start_stamp               = models.DateTimeField(blank=True, null=True, verbose_name=_('Start Date'))                                                 # noqa: E501, E221
    answer_epoch              = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('Answer Epoch'))               # noqa: E501, E221
    answer_stamp              = models.DateTimeField(blank=True, null=True, verbose_name=_('Answer Date'))                                                # noqa: E501, E221
    end_epoch                 = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('End Epoch'))                  # noqa: E501, E221
    end_stamp                 = models.DateTimeField(blank=True, null=True, verbose_name=_('End Date'))                                                   # noqa: E501, E221
    duration                  = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('Duration'))                   # noqa: E501, E221
    mduration                 = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('mSec Duration'))              # noqa: E501, E221
    billsec                   = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('Bill Seconds'))               # noqa: E501, E221
    billmsec                  = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('Bill mSeconds'))              # noqa: E501, E221
    bridge_uuid               = models.UUIDField(blank=True, null=True, verbose_name=_('Bridge UUID'))                                                    # noqa: E501, E221
    read_codec                = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Read Codec'))                                      # noqa: E501, E221
    read_rate                 = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Read Rate'))                                       # noqa: E501, E221
    write_codec               = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Write Codec'))                                     # noqa: E501, E221
    write_rate                = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Write Rate'))                                      # noqa: E501, E221
    remote_media_ip           = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Remote Media IP'))                                # noqa: E501, E221
    network_addr              = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Network Address'))                                # noqa: E501, E221
    record_path               = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Record Path'))                                    # noqa: E501, E221
    record_name               = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Record Name'))                                     # noqa: E501, E221
    leg                       = models.CharField(max_length=8, blank=True, null=True, verbose_name=_('Leg'))                                              # noqa: E501, E221
    pdd_ms                    = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('PDD'))                        # noqa: E501, E221
    rtp_audio_in_mos          = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, verbose_name=_('MOS'))                         # noqa: E501, E221
    last_app                  = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Last App.'))                                       # noqa: E501, E221
    last_arg                  = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Last Arg.'))                                      # noqa: E501, E221
    missed_call               = models.BooleanField(blank=True, null=True, verbose_name=_('Missed Call'))                                                 # noqa: E501, E221
    cc_side                   = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('CC Side'))                                         # noqa: E501, E221
    cc_member_uuid            = models.UUIDField(blank=True, null=True, verbose_name=_('CC Member UUID'))                                                 # noqa: E501, E221
    cc_queue_joined_epoch     = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('CC Joined Epoch'))            # noqa: E501, E221
    cc_queue                  = models.UUIDField(blank=True, null=True, verbose_name=_('CC Queue UUID'))                                                  # noqa: E501, E221
    cc_member_session_uuid    = models.UUIDField(blank=True, null=True, verbose_name=_('CC Member Session UUID'))                                         # noqa: E501, E221
    cc_agent_uuid             = models.UUIDField(blank=True, null=True, verbose_name=_('CC Agent UUID'))                                                  # noqa: E501, E221
    cc_agent                  = models.UUIDField(blank=True, null=True, verbose_name=_('CC Agent'))                                                       # noqa: E501, E221
    cc_agent_type             = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('CC Agent Type'))                                   # noqa: E501, E221
    cc_agent_bridged          = models.CharField(max_length=8, blank=True, null=True, verbose_name=_('CC Agent Bridged'))                                 # noqa: E501, E221
    cc_queue_answered_epoch   = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('CC Queue Answered Epoch'))    # noqa: E501, E221
    cc_queue_terminated_epoch = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('CC Queue Terminated Epoch'))  # noqa: E501, E221
    cc_queue_canceled_epoch   = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('CC Queue Cancelled Epoch'))   # noqa: E501, E221
    cc_cancel_reason          = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('CC Cancel Reason'))                                # noqa: E501, E221
    cc_cause                  = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('CC Cause'))                                        # noqa: E501, E221
    waitsec                   = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('Wait Seconds'))               # noqa: E501, E221
    conference_name           = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Conference Name'))                                # noqa: E501, E221
    conference_uuid           = models.UUIDField(blank=True, null=True, verbose_name=_('Conference UUID'))                                                # noqa: E501, E221
    conference_member_id      = models.CharField(max_length=8, blank=True, null=True, verbose_name=_('Conference Member ID'))                             # noqa: E501, E221
    digits_dialed             = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Digits Dialled'))                                  # noqa: E501, E221
    pin_number                = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('PIN Number'))                                      # noqa: E501, E221
    hangup_cause              = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Hangup Cause'))                                    # noqa: E501, E221
    hangup_cause_q850         = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True, verbose_name=_('Hangup Cause Q.850'))          # noqa: E501, E221
    sip_hangup_disposition    = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('SIP Hangup Disposition'))                          # noqa: E501, E221
    xml                       = models.TextField(blank=True, null=True, verbose_name=_('XML'))                                                            # noqa: E501, E221
    json                      = models.JSONField(blank=True, null=True, verbose_name=_('json'))                                                           # noqa: E501, E221
    created                   = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                 # noqa: E501, E221
    updated                   = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                     # noqa: E501, E221
    synchronised              = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                               # noqa: E501, E221
    updated_by                = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                             # noqa: E501, E221

    class Meta:
        db_table = 'pbx_xml_cdr'

    def __str__(self):
        return str(self.extension_id)
