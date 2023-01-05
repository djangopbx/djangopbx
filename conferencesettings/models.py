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
from pbx.commonchoices import EnabledTrueFalseChoice


class ConferenceControlDetails(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Conference Control Details'))
    conf_ctrl_id = models.ForeignKey('ConferenceControls', on_delete=models.CASCADE, verbose_name=_('Conference Control'))
    digits       = models.CharField(max_length=8, default='0', verbose_name=_('Digits'))
    action       = models.CharField(max_length=64, default='mute', verbose_name=_('Action'))
    data         = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Data'))
    enabled      = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        verbose_name_plural = 'Conference Control Details'
        db_table = 'pbx_conference_control_details'

    def __str__(self):
        return self.action


class ConferenceControls(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Conference Controls'))
    name         = models.CharField(max_length=32, default='new', verbose_name=_('Name'))
    enabled      = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))
    description  = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Description'))
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        verbose_name_plural = 'Conference Controls'
        db_table = 'pbx_conference_controls'

    def __str__(self):
        return self.name


class ConferenceProfileParams(models.Model):
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Conference Profile Params'))
    conf_profile_id = models.ForeignKey('ConferenceProfiles', on_delete=models.CASCADE, verbose_name=_('Conference Profile'))
    name            = models.CharField(max_length=64, default='new', verbose_name=_('Name'))
    value           = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Value'))
    enabled         = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))
    description     = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))
    created         = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated         = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised    = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by      = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        verbose_name_plural = 'Conference Profile Params'
        db_table = 'pbx_conference_profile_params'

    def __str__(self):
        return self.name


class ConferenceProfiles(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Conference Profiles'))
    name         = models.CharField(max_length=32, default='default', verbose_name=_('Name'))
    enabled      = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))
    description  = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        verbose_name_plural = 'Conference Profiles'
        db_table = 'pbx_conference_profiles'

    def __str__(self):
        return self.name

