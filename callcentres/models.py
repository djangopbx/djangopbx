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

from django.db import models

import random
import uuid
from django.utils.translation import gettext_lazy as _
from pbx.commonchoices import EnabledTrueFalseChoice

def random_pin():
    return str(random.randint(10000, 99999))

def get_agent_contact(cca):
    confirm = 'group_confirm_file=ivr/ivr-accrpt_reject.wav,group_confirm_key=1,group_confirm_read_timeout=2000,leg_timeout=%s' % cca.call_timeout

    if '}' in cca.contact:
        parts = cca.contact.partition('}')
        if 'sofia/gateway' in cca.contact:
            agent_contact = '%s,%s,call_timeout=%s,sip_h_caller_destination=${caller_destination}}%s' % (parts[0], confirm, cca.call_timeout, parts[2])
        else:
            agent_contact = '%s,call_timeout=%s,domain_uuid=%s,Domain_name=%s,sip_h_caller_destination=${caller_destination}}%s' % (parts[0], cca.call_timeout, str(cca.domain_id), cca.domain_id.name, parts[2])
    else:
        if 'sofia/gateway' in cca.contact:
            agent_contact = '{%s,call_timeout=%s,sip_h_caller_destination=${caller_destination}}%s' % (confirm, cca.call_timeout, cca.contact)
        else:
            agent_contact = '{call_timeout=%s,domain_uuid=%s,Domain_name=%s,sip_h_caller_destination=${caller_destination}}%s' % (cca.call_timeout, str(cca.domain_id), cca.domain_id.name, cca.contact)
    return agent_contact


class CallCentreQueueTimeBScoreChoice(models.TextChoices):
    CSYSTEM = 'system', _('System') # noqa: E221
    CQUEUE  = 'queue',  _('Queue')  # noqa: E221


class CallCentreQueueStrategyChoice(models.TextChoices):
    CRA    = 'ring-all',                         _('Ring All')                         # noqa: E221
    CLIA   = 'longest-idle-agent',               _('Longest Idle Agent')               # noqa: E221
    CRR    = 'round-robin',                      _('Round Robin')                      # noqa: E221
    CTD    = 'top-down',                         _('Top Down')                         # noqa: E221
    CAWLTT = 'agent-with-least-talk-time',       _('Agent With Least Talk Time')       # noqa: E221
    CAWFC  = 'agent-with-fewest-calls',          _('Agent With Fewest Calls')          # noqa: E221
    CSBAO  = 'sequentially-by-agent-order',      _('Sequentially By Agent Order')      # noqa: E221
    CSBNAO = 'sequentially-by-next-agent-order', _('Sequentially By Next Agent Order') # noqa: E221
    CRAND  = 'random',                           _('Random')                           # noqa: E221


class CallCentreAgentStatusChoice(models.TextChoices):
    CNONE  = '', ''                                              # noqa: E221
    CLGDO  = 'Logged Out',            _('Logged Out')            # noqa: E221
    CAVAIL = 'Available',             _('Available')             # noqa: E221
    CAOD   = 'Available (On Demand)', _('Available (On Demand)') # noqa: E221
    COB    = 'On Break',              _('On Break')              # noqa: E221


class CallCentreAgentTypeChoice(models.TextChoices):
    CCALLBK = 'callback',      _('Call Back')    # noqa: E221
    CUUIDSB = 'uuid-standby',  _('UUID Standby') # noqa: E221


class CallCentreAgents(models.Model):
    id                   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Call Centre Agent'))                                                                                                      # noqa: E501, E221
    domain_id            = models.ForeignKey('tenants.Domain', db_column='domain_uuid', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))                                                                          # noqa: E501, E221
    user_uuid            = models.ForeignKey('tenants.Profile', models.SET_NULL, to_field='user_uuid', db_column='user_uuid', blank=True, null=True, verbose_name=_('User'))                                                                # noqa: E501, E221
    name                 = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Name'), help_text=_('Enter a name'))                                                                                                      # noqa: E501, E221
    agent_type           = models.CharField(max_length=16, blank=True, null=True, choices=CallCentreAgentTypeChoice.choices, default=CallCentreAgentTypeChoice.CCALLBK, verbose_name=_('Type'))                                             # noqa: E501, E221
    call_timeout         = models.DecimalField(max_digits=3, decimal_places=0, default=20, verbose_name=_('Call Timeout'))                                                                                                                  # noqa: E501, E221
    agent_id             = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Agent Id'))                                                                                                                               # noqa: E501, E221
    agent_pin            = models.CharField(max_length=16, default=random_pin, verbose_name=_('Agent PIN'))                                                                                                                                 # noqa: E501, E221
    contact              = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Contact'), help_text=_('Select the contact destination (eg. extension)'))                                                                # noqa: E501, E221
    status               = models.CharField(max_length=32, blank=True, null=True, choices=CallCentreAgentStatusChoice.choices, default=CallCentreAgentStatusChoice.CNONE, verbose_name=_('Status'), help_text=_('Sets the default status')) # noqa: E501, E221
    data                 = models.CharField(max_length=64, default='false', verbose_name=_('Agent Data'))                                                                                                                                   # noqa: E501, E221
    no_answer_delay_time = models.DecimalField(max_digits=3, decimal_places=0, default=30, verbose_name=_('No Answer Delay Time'))                                                                                                          # noqa: E501, E221
    max_no_answer        = models.DecimalField(max_digits=3, decimal_places=0, default=0, verbose_name=_('Max No Answer'))                                                                                                                  # noqa: E501, E221
    wrap_up_time         = models.DecimalField(max_digits=3, decimal_places=0, default=10, verbose_name=_('Wrap Up Time'))                                                                                                                  # noqa: E501, E221
    reject_delay_time    = models.DecimalField(max_digits=3, decimal_places=0, default=90, verbose_name=_('Reject Delay Time'))                                                                                                             # noqa: E501, E221
    busy_delay_time      = models.DecimalField(max_digits=3, decimal_places=0, default=90, verbose_name=_('Busy Delay Time'))                                                                                                               # noqa: E501, E221
    created              = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                                                                        # noqa: E501, E221
    updated              = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                                                                            # noqa: E501, E221
    synchronised         = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                                                                      # noqa: E501, E221
    updated_by           = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                                                                                    # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Call Centre Agents'
        db_table = 'pbx_call_centre_agents'
        unique_together = ('domain_id', 'agent_id')

    def __str__(self):
        return f'{self.name}-{self.agent_id}'


class CallCentreQueues(models.Model):
    id                    = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Call Centre Agent'))                                                                                           # noqa: E501, E221
    domain_id             = models.ForeignKey('tenants.Domain', db_column='domain_uuid', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))                                                               # noqa: E501, E221
    name                  = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Name'), help_text=_('Enter a name'))                                                                                           # noqa: E501, E221
    extension             = models.CharField(max_length=32, blank=False, null=False, verbose_name=_('Extension'), help_text=_('Enter the extension number for this Call Centre'))                                                 # noqa: E501, E221
    greeting              = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Greeting'), help_text=_('Select the desired Greeting or leave blank'))                                                        # noqa: E501, E221
    strategy              = models.CharField(max_length=32, blank=True, null=True, choices=CallCentreQueueStrategyChoice.choices, default=CallCentreQueueStrategyChoice.CLIA, verbose_name=_('Strategy'))                         # noqa: E501, E221
    moh_sound             = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Musin On Hold'), help_text=_('Select the desired hold music'))                                                                # noqa: E501, E221
    record_template       = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Record'), help_text=_('Save a recording'))                                                                                    # noqa: E501, E221
    time_base_score       = models.CharField(max_length=16, blank=True, null=True, choices=CallCentreQueueTimeBScoreChoice.choices, default=CallCentreQueueTimeBScoreChoice.CSYSTEM, verbose_name=_('Time Base Score'))           # noqa: E501, E221
    max_wait_time         = models.DecimalField(max_digits=3, decimal_places=0, default=0, verbose_name=_('Max Wail Time'))                                                                                                       # noqa: E501, E221
    max_wait_time_na      = models.DecimalField(max_digits=3, decimal_places=0, default=90, verbose_name=_('Max Wait Time with No Agent'))                                                                                        # noqa: E501, E221
    max_wait_time_natr    = models.DecimalField(max_digits=3, decimal_places=0, default=30, verbose_name=_('Max Wait Time with No Agent Time Reached'))                                                                           # noqa: E501, E221
    timeout_action        = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Timeout Destination'), help_text=_('Select the destination when the max wait time is reached.'))                              # noqa: E501, E221
    tier_rules_apply      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Tier Rules Apply'))                                                      # noqa: E501, E221
    tier_rule_wait_sec    = models.DecimalField(max_digits=3, decimal_places=0, default=30, verbose_name=_('Tier Rule Wait Second'))                                                                                              # noqa: E501, E221
    tier_rule_wm_level    = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Tier Rule Wait Multiply Level'))                                         # noqa: E501, E221
    tier_rule_nanw        = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Tier Rule No Agent No Wait'))                                            # noqa: E501, E221
    discard_abndnd_after  = models.DecimalField(max_digits=4, decimal_places=0, default=900, verbose_name=_('Discard Abandoned After'))                                                                                           # noqa: E501, E221
    abndnd_resume_allowed = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Abandoned Resume Allowed'))                                              # noqa: E501, E221
    cid_name_prefix       = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('CID Name Prefix'), help_text=_('Set a prefix on the caller ID name'))                                                          # noqa: E501, E221
    announce_sound        = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Announce Sound'), help_text=_('sound to play to a caller every announce sound seconds. Needs the full path to the wav file')) # noqa: E501, E221
    announce_frequency    = models.DecimalField(max_digits=3, decimal_places=0, blank=True, null=True, default=None, verbose_name=_('Announce Frequency'))                                                                        # noqa: E501, E221
    cc_exit_keys          = models.CharField(max_length=8, blank=True, null=True, verbose_name=_('Exit Key'), help_text=_('Keys to quit the current queue waiting'))                                                              # noqa: E501, E221
    wb_wait_warn_level    = models.DecimalField(max_digits=3, decimal_places=0, default=5, verbose_name=_('Waiting Warning Level'))                                                                                               # noqa: E501, E221
    wb_wait_crit_level    = models.DecimalField(max_digits=3, decimal_places=0, default=20, verbose_name=_('Waiting Critical Level'))                                                                                             # noqa: E501, E221
    wb_aban_warn_level    = models.DecimalField(max_digits=3, decimal_places=0, default=5, verbose_name=_('Abandoned Warning Level'))                                                                                             # noqa: E501, E221
    wb_aban_crit_level    = models.DecimalField(max_digits=3, decimal_places=0, default=20, verbose_name=_('Abandoned Critical Level'))                                                                                           # noqa: E501, E221
    wb_show_agents        = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Show Agents'))                                                           # noqa: E501, E221
    wb_agents_per_row     = models.DecimalField(max_digits=3, decimal_places=0, default=6, verbose_name=_('Number of Agents per row'))                                                                                            # noqa: E501, E221
    enabled               = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))                                                               # noqa: E501, E221
    description           = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Description'))                                                                                                                 # noqa: E501, E221
    dialplan_id           = models.UUIDField(blank=True, null=True, verbose_name=_('Dialplan UUID'))                                                                                                                              # noqa: E501, E221
    created               = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                                                             # noqa: E501, E221
    updated               = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                                                                 # noqa: E501, E221
    synchronised          = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                                                           # noqa: E501, E221
    updated_by            = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                                                                         # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Call Centre Queues'
        db_table = 'pbx_call_centre_queues'

    def __str__(self):
        return f'{self.name}-{self.extension}'


class CallCentreTiers(models.Model):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Call Centre Tier')) # noqa: E501, E221
    queue_id      = models.ForeignKey('CallCentreQueues', on_delete=models.CASCADE, verbose_name=_('Call Centre Queue'))       # noqa: E501, E221
    agent_id      = models.ForeignKey('CallCentreAgents', on_delete=models.CASCADE, verbose_name=_('Call Centre Agent'))       # noqa: E501, E221
    tier_level    = models.DecimalField(max_digits=4, decimal_places=0, default=0, verbose_name=_('Tier Level'))               # noqa: E501, E221
    tier_position = models.DecimalField(max_digits=4, decimal_places=0, default=0, verbose_name=_('Tier Position'))            # noqa: E501, E221
    created       = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                  # noqa: E501, E221
    updated       = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                      # noqa: E501, E221
    synchronised  = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                # noqa: E501, E221
    updated_by    = models.CharField(max_length=64, verbose_name=_('Updated by'))                                              # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Call Centre Tiers'
        db_table = 'pbx_call_centre_tiers'

    def __str__(self):
        return str(self.id)


class CallCentreAgentStatusLog(models.Model):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Agent Status Log')) # noqa: E501, E221
    agent_id      = models.ForeignKey('CallCentreAgents', on_delete=models.CASCADE, verbose_name=_('Call Centre Agent'))       # noqa: E501, E221
    status        = models.CharField(max_length=32, blank=True, null=True, default='Unknown', verbose_name=_('Status'))        # noqa: E501, E221
    created       = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                  # noqa: E501, E221
    updated       = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                      # noqa: E501, E221
    synchronised  = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                # noqa: E501, E221
    updated_by    = models.CharField(max_length=64, verbose_name=_('Updated by'))                                              # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Agent Status Log'
        db_table = 'pbx_cc_agent_status_log'

    def __str__(self):
        return str(self.id)
