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

import uuid
from django.utils.translation import gettext_lazy as _
from pbx.commonchoices import EnabledTrueFalseChoice


class RingGroupStrategyChoice(models.TextChoices):
    CSIM  = 'simultaneous', _('Simultaneous') # noqa: E221
    CSEQ  = 'sequence',     _('Sequence')     # noqa: E221
    CENT  = 'enterprise',   _('Enterprise')   # noqa: E221
    CROL  = 'rollover',     _('Rollover')     # noqa: E221
    CRAN  = 'random',       _('Random')       # noqa: E221


class RingGroupDestPromptChoice(models.IntegerChoices):
    CNONE     = 0,   ''                # noqa: E221
    CCONFIRM  = 1,   _('Confirm')      # noqa: E221


class RingGroupTimeoutAppChoice(models.TextChoices):
    CNONE      = '', ''                    # noqa: E221
    CHANGUP    = 'hangup', _('Hangup')     # noqa: E221
    CTRANSFER  = 'transfer', _('Transfer') # noqa: E221
    CPLAYBACK  = 'playback', _('Playback') # noqa: E221


class RingGroupMissedCallAppChoice(models.TextChoices):
    CNONE  = '',         _('Not Set')  # noqa: E221
    CEMAIL = 'email',    _('Email')    # noqa: E221


class RingGroup(models.Model):
    id                  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Ring Group'))                                                                                                                           # noqa: E501, E221
    domain_id           = models.ForeignKey('tenants.Domain', db_column='domain_uuid', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))                                                                                        # noqa: E501, E221
    name                = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Name'), help_text=_('Enter a name'))                                                                                                                    # noqa: E501, E221
    extension           = models.CharField(max_length=32, blank=False, null=False, verbose_name=_('Extension'), help_text=_('Enter the extension number for this ring group'))                                                                           # noqa: E501, E221
    greeting            = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Greeting'), help_text=_('Select the desired Greeting or leave blank'))                                                                                 # noqa: E501, E221
    strategy            = models.CharField(max_length=16, blank=True, null=True, choices=RingGroupStrategyChoice.choices, default=RingGroupStrategyChoice.CSIM, verbose_name=_('Strategy'), help_text=_('Select the ring strategy'))                     # noqa: E501, E221
    timeout_app         = models.CharField(max_length=32, blank=True, null=True, choices=RingGroupTimeoutAppChoice.choices, default=RingGroupTimeoutAppChoice.CNONE, verbose_name=_('Timeout App.'), help_text=_('Select the timeout destination type')) # noqa: E501, E221
    timeout_data        = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Timeout Destination'), help_text=_('Select the timeout destination  for this ring group'))                                         # noqa: E501, E221
    call_timeout        = models.DecimalField(max_digits=3, decimal_places=0, default=0, verbose_name=_('Timeout'), help_text=_('Timeout time in seconds'))                                                                                              # noqa: E501, E221
    caller_id_name      = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Caller ID Name'), help_text=_('Set the caller ID name for outbound external calls'))                                                                    # noqa: E501, E221
    caller_id_number    = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Caller ID Number'), help_text=_('Set the caller ID number for outbound external calls'))                                                                # noqa: E501, E221
    cid_name_prefix     = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('CID Name Prefix'), help_text=_('Set a prefix on the caller ID name'))                                                                                   # noqa: E501, E221
    cid_number_prefix   = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('CID Number Prefix'), help_text=_('Set a prefix on the caller ID number'))                                                                               # noqa: E501, E221
    distinctive_ring    = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Distinctive Ring'), help_text=_('Select a sound for a distinctive ring'))                                                                               # noqa: E501, E221
    ring_group_ringback = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Ring Back'), help_text=_('Defines what the caller will hear while the destination is being called'))                                                   # noqa: E501, E221
    follow_me_enabled   = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Follow Me Enabled'), help_text=_('Choose to follow a ring group destinations follow me'))        # noqa: E501, E221
    missed_call_app     = models.CharField(max_length=32, blank=True, null=True, choices=RingGroupMissedCallAppChoice.choices, default=RingGroupMissedCallAppChoice.CNONE, verbose_name=_('Missed Call'), help_text=_('Select the missed call destination type'))          # noqa: E501, E221
    missed_call_data    = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Missed Call Data'), help_text=_('Typically an email address or comma separated addresses'))                                                            # noqa: E501, E221
    forward_enabled     = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Forward Enabled'), help_text=_('Forward a called Ring Group to an alternate destination'))       # noqa: E501, E221
    forward_destination = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Forward Destination'), help_text=_('Forward Destination'))                                                                                             # noqa: E501, E221
    forward_toll_allow  = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Forward Toll Allow'), help_text=_('Ring group forwarding toll allow'))                                                                                  # noqa: E501, E221
    context             = models.CharField(max_length=128, db_index=True, blank=True, null=True, verbose_name=_('Context'), help_text=_('Enter the context'))                                                                                            # noqa: E501, E221
    enabled             = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'), help_text=_('Set the status of this ring group'))                                      # noqa: E501, E221
    description         = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Description'))                                                                                                                                          # noqa: E501, E221
    dialplan_id         = models.UUIDField(blank=True, null=True, verbose_name=_('Dialplan UUID'))                                                                                                                                                       # noqa: E501, E221
    created             = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                                                                                      # noqa: E501, E221
    updated             = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                                                                                          # noqa: E501, E221
    synchronised        = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                                                                                    # noqa: E501, E221
    updated_by          = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                                                                                                  # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Ring Groups'
        db_table = 'pbx_ring_groups'

    def __str__(self):
        return f'{self.extension}->{self.name}'


class RingGroupDestination(models.Model):
    id                 = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Ring Group Destination'))                                                  # noqa: E501, E221
    ring_group_id      = models.ForeignKey('RingGroup', on_delete=models.CASCADE, verbose_name=_('Ring Group'))                                                                            # noqa: E501, E221
    number             = models.CharField(max_length=128, blank=False, null=False, verbose_name=_('Number'))                                                                               # noqa: E501, E221
    delay              = models.DecimalField(max_digits=3, decimal_places=0, default=0, verbose_name=_('Delay'))                                                                           # noqa: E501, E221
    timeout            = models.DecimalField(max_digits=3, decimal_places=0, default=30, verbose_name=_('Timeout'))                                                                        # noqa: E501, E221
    destination_prompt = models.DecimalField(max_digits=3, decimal_places=0, choices=RingGroupDestPromptChoice.choices, default=RingGroupDestPromptChoice.CNONE, verbose_name=_('Prompt')) # noqa: E501, E221
    created            = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                         # noqa: E501, E221
    updated            = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                             # noqa: E501, E221
    synchronised       = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                       # noqa: E501, E221
    updated_by         = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                                     # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Ring Group Destinations'
        db_table = 'pbx_ring_group_destinations'

    def __str__(self):
        return self.number


class RingGroupUser(models.Model):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Ring Group User'))                                         # noqa: E501, E221
    ring_group_id = models.ForeignKey('RingGroup', on_delete=models.CASCADE, verbose_name=_('Ring Group'))                                                            # noqa: E501, E221
    user_uuid     = models.ForeignKey('tenants.Profile', models.SET_NULL, to_field='user_uuid', db_column='user_uuid', blank=True, null=True, verbose_name=_('User')) # noqa: E501, E221
    created       = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                         # noqa: E501, E221
    updated       = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                             # noqa: E501, E221
    synchronised  = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                       # noqa: E501, E221
    updated_by    = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                     # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Ring Group Users'
        db_table = 'pbx_ring_group_users'

    def __str__(self):
        return str(self.id)
