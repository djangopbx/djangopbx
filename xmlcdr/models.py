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
from pbx.commonchoices import (
    EnabledTrueFalseChoice,
)
# for timeline link
from django.urls import reverse
from django.utils.html import mark_safe


class XmlCdr(models.Model):
    id                        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Call Detail Record'))              # noqa: E501, E221
    domain_id                 = models.ForeignKey('tenants.Domain', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))            # noqa: E501, E221
    extension_id              = models.ForeignKey('accounts.Extension', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Extension'))     # noqa: E501, E221
    core_uuid                 = models.UUIDField(blank=True, null=True, verbose_name=_('Core UUID'))                                                      # noqa: E501, E221
    call_uuid                 = models.UUIDField(blank=True, null=True, verbose_name=_('Call UUID'))                                                      # noqa: E501, E221
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
    last_arg                  = models.TextField(blank=True, null=True, verbose_name=_('Last Arg.'))                                                      # noqa: E501, E221
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
        verbose_name_plural = 'CDRs'
        db_table = 'pbx_xml_cdr'

    def __str__(self):
        return str(self.extension_id)

    def timeline(self):
        return mark_safe('<a class="grp-button" href="%s">%s</a>' % (
                    reverse('cdrtimeline', args=[self.call_uuid]), _('Timeline')
                    ))

    timeline.short_description = _('Timeline')


class CallTimeline(models.Model):
    id                            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Timeline Record'))             # noqa: E501, E221
    domain_id                     = models.ForeignKey('tenants.Domain', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))        # noqa: E501, E221
    core_uuid                     = models.UUIDField(db_index=True, verbose_name=_('Core UUID'))                                                          # noqa: E501, E221
    hostname                      = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Host Name'))                                  # noqa: E501, E221
    switchame                     = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Switch Name'))                                # noqa: E501, E221
    switch_ipv4                   = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Switch IPv6 Address'))                         # noqa: E501, E221
    switch_ipv6                   = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Switch IPv6 Address'))                         # noqa: E501, E221
    call_uuid                     = models.UUIDField(db_index=True, blank=True, null=True, verbose_name=_('Call UUID'))                                   # noqa: E501, E221
    event_name                    = models.CharField(max_length=64, verbose_name=_('Event Name'))                                                         # noqa: E501, E221
    event_subclass                = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Event Subclass'))                              # noqa: E501, E221
    event_date_local              = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Event Date Local'))                            # noqa: E501, E221
    event_epoch                   = models.DecimalField(db_index=True, max_digits=32, decimal_places=0, default=0, verbose_name=_('Event Epoch'))         # noqa: E501, E221
    event_sequence                = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Event Sequence'))                     # noqa: E501, E221
    event_calling_file            = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Event Calling File'))                          # noqa: E501, E221
    event_calling_function        = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Event Calling Function'))                      # noqa: E501, E221
    direction                     = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Direction'))                                   # noqa: E501, E221
    other_leg_direction           = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Other Leg Direction'))                         # noqa: E501, E221
    context                       = models.CharField(db_index=True, max_length=128, blank=True, null=True, verbose_name=_('Context'))                     # noqa: E501, E221
    other_leg_context             = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Other Leg Context'))                          # noqa: E501, E221
    hit_dialplan                  = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Hit Dialplan')) # noqa: E501, E221
    caller_user_name              = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Caller User Name'))                            # noqa: E501, E221
    caller_ani                    = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Caller ANI'))                                  # noqa: E501, E221
    other_leg_user_name           = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Other Leg User Name'))                         # noqa: E501, E221
    caller_uuid                   = models.UUIDField(blank=True, null=True, verbose_name=_('Caller UUID'))                                                # noqa: E501, E221
    other_leg_caller_uuid         = models.UUIDField(blank=True, null=True, verbose_name=_('Other Leg Caller UUID'))                                      # noqa: E501, E221
    channel_name                  = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Channel Name'))                               # noqa: E501, E221
    channel_state                 = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Channel State'))                               # noqa: E501, E221
    channel_call_state            = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Channel Call State'))                          # noqa: E501, E221
    answer_state                  = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Answer State'))                                # noqa: E501, E221
    bridge_channel                = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Bridge Channel'))                             # noqa: E501, E221
    unique_id                     = models.UUIDField(db_index=True, blank=True, null=True, verbose_name=_('Unique ID'))                                   # noqa: E501, E221
    other_leg_unique_id           = models.UUIDField(db_index=True, blank=True, null=True, verbose_name=_('Other Leg Unique ID'))                         # noqa: E501, E221
    caller_id_name                = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Caller ID Name'))                              # noqa: E501, E221
    other_leg_caller_id_name      = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Other Leg Caller ID Name'))                    # noqa: E501, E221
    caller_id_number              = models.CharField(db_index=True, max_length=32, blank=True, null=True, verbose_name=_('Caller ID Number'))             # noqa: E501, E221
    other_leg_caller_id_number    = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Other Leg Caller ID Number'))                  # noqa: E501, E221
    caller_destination            = models.CharField(db_index=True, max_length=32, blank=True, null=True, verbose_name=_('Destination'))                  # noqa: E501, E221
    other_leg_caller_destination  = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Other Leg Destination'))                       # noqa: E501, E221
    network_addr                  = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Network Address'))                             # noqa: E501, E221
    other_leg_network_addr        = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Other Leg Network Address'))                   # noqa: E501, E221
    created_time                  = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Created Time'))                       # noqa: E501, E221
    other_leg_created_time        = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Other Leg Created Time'))             # noqa: E501, E221
    answered_time                 = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Answered Time'))                      # noqa: E501, E221
    other_leg_answered_time       = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Other Leg Answered Time'))            # noqa: E501, E221
    progress_time                 = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Progress Time'))                      # noqa: E501, E221
    other_leg_progress_time       = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Other Leg Progress Time'))            # noqa: E501, E221
    progress_media_time           = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Progress Media Time'))                # noqa: E501, E221
    other_leg_progress_media_time = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Other Leg Progress Media Time'))      # noqa: E501, E221
    hangup_time                   = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Hangup Time'))                        # noqa: E501, E221
    other_leg_hangup_time         = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Other Leg Hangup Time'))              # noqa: E501, E221
    transfer_time                 = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Transfer Time'))                      # noqa: E501, E221
    other_leg_transfer_time       = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Other Leg Transfer Time'))            # noqa: E501, E221
    resurrect_time                = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Resurrect Time'))                     # noqa: E501, E221
    other_leg_resurrect_time      = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Other Leg Resurrect Time'))           # noqa: E501, E221
    bridged_time                  = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Bridged Time'))                       # noqa: E501, E221
    other_leg_bridged_time        = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Other Leg Bridged Time'))             # noqa: E501, E221
    last_hold_time                = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Last Hold Time'))                     # noqa: E501, E221
    other_leg_last_hold_time      = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Other Leg Last Hold Time'))           # noqa: E501, E221
    hold_accu_time                = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Hold Accu. Time'))                    # noqa: E501, E221
    other_leg_hold_accu_time      = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Other Leg Hold Accu. Time'))          # noqa: E501, E221
    application                   = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Application'))                                 # noqa: E501, E221
    application_name              = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Application Name'))                            # noqa: E501, E221
    application_action            = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Application Action'))                          # noqa: E501, E221
    application_uuid              = models.UUIDField(blank=True, null=True, verbose_name=_('Application UUID'))                                           # noqa: E501, E221
    application_data              = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Application Data'))                           # noqa: E501, E221
    application_status            = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Application Status'))                          # noqa: E501, E221
    application_file_path         = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Application File Path'))                      # noqa: E501, E221
    application_seconds           = models.DecimalField(max_digits=32, decimal_places=0, blank=True, null=True, verbose_name=_('Application Seconds'))    # noqa: E501, E221
    transfer_source               = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Transfer Source'))                            # noqa: E501, E221
    cc_side                       = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('CC Side'))                                     # noqa: E501, E221
    cc_queue                      = models.UUIDField(blank=True, null=True, verbose_name=_('CC Queue UUID'))                                              # noqa: E501, E221
    cc_action                     = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('CC Action'))                                   # noqa: E501, E221
    cc_count                      = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('CC Count'))                           # noqa: E501, E221
    cc_member_joining_time        = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('CC Member Joining Time'))             # noqa: E501, E221
    cc_member_leaving_time        = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('CC Member Leaving Time'))             # noqa: E501, E221
    cc_cause                      = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('CC Cause'))                                    # noqa: E501, E221
    cc_hangup_cause               = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('CC Hangup Cause'))                             # noqa: E501, E221
    cc_cancel_reason              = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('CC Cancel Reason'))                            # noqa: E501, E221
    cc_member_uuid                = models.UUIDField(blank=True, null=True, verbose_name=_('CC Member UUID'))                                             # noqa: E501, E221
    cc_member_session_uuid        = models.UUIDField(blank=True, null=True, verbose_name=_('CC Member Session UUID'))                                     # noqa: E501, E221
    cc_member_caller_id_name      = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('CC Member Caller ID Name'))                    # noqa: E501, E221
    cc_member_caller_id_number    = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('CC Member Caller ID Number'))                  # noqa: E501, E221
    cc_agent                      = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('CC Agent'))                                   # noqa: E501, E221
    cc_agent_uuid                 = models.UUIDField(blank=True, null=True, verbose_name=_('CC Agent UUID'))                                              # noqa: E501, E221
    cc_agent_system               = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('CC Agent System'))                             # noqa: E501, E221
    cc_agent_type                 = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('CC Agent Type'))                               # noqa: E501, E221
    cc_agent_state                = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('CC Agent State'))                              # noqa: E501, E221
    cc_agent_called_time          = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('CC Agent Called Time'))               # noqa: E501, E221
    cc_agent_answered_time        = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('CC Agent Answered Time'))             # noqa: E501, E221
    dtmf_digit                    = models.CharField(max_length=8, blank=True, null=True, verbose_name=_('DTMF Digit'))                                   # noqa: E501, E221
    dtmf_duration                 = models.DecimalField(max_digits=5, decimal_places=0, default=0, verbose_name=_('DTMF Duration'))                       # noqa: E501, E221
    dtmf_source                   = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('DTMF Source'))                                 # noqa: E501, E221
    cf_name                       = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Conference Name'))                            # noqa: E501, E221
    cf_action                     = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Conference Action'))                           # noqa: E501, E221
    cf_uuid                       = models.UUIDField(blank=True, null=True, verbose_name=_('Conference UUID'))                                            # noqa: E501, E221
    cf_domain                     = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Conference Domain'))                          # noqa: E501, E221
    cf_size                       = models.DecimalField(max_digits=5, decimal_places=0, default=0, verbose_name=_('Conference Size'))                     # noqa: E501, E221
    cf_ghosts                     = models.DecimalField(max_digits=5, decimal_places=0, default=0, verbose_name=_('Conference Ghosts'))                   # noqa: E501, E221
    cf_profile_name               = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Conference Profile Name'))                     # noqa: E501, E221
    cf_member_type                = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Conference Member Type'))                      # noqa: E501, E221
    cf_member_id                  = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Conference Member ID'))                        # noqa: E501, E221
    general_error                 = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('General Error'))                               # noqa: E501, E221
    created                       = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                             # noqa: E501, E221
    updated                       = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                 # noqa: E501, E221
    synchronised                  = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                           # noqa: E501, E221
    updated_by                    = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                         # noqa: E501, E221


    class Meta:
        verbose_name_plural = 'Call Timeline'
        db_table = 'pbx_call_timeline'

    def __str__(self):
        return f"{self.context}->{self.caller_id_number}: {self.event_name}"
