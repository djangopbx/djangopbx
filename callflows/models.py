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

import uuid
from django.db import models

from django.utils.translation import gettext_lazy as _
from pbx.commonchoices import EnabledTrueFalseChoice


class CallFlowStatusChoice(models.TextChoices):
    CDAY    = 'true',  _('Day Mode')   # noqa: E221
    CNIGHT  = 'false', _('Night Mode') # noqa: E221


class CallFlows(models.Model):
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Call Flow'))                                                                                     # noqa: E501, E221
    domain_id       = models.ForeignKey('tenants.Domain', db_column='domain_uuid', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))                                                 # noqa: E501, E221
    name            = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Name'), help_text=_('Enter a name'))                                                                             # noqa: E501, E221
    extension       = models.CharField(max_length=32, blank=False, null=False, verbose_name=_('Extension'), help_text=_('Enter the extension number for this call flow'))                                     # noqa: E501, E221
    feature_code    = models.CharField(max_length=8, default='*30', verbose_name=_('Feature Code'), help_text=_('Enter the feature code'))                                                                    # noqa: E501, E221
    status          = models.CharField(max_length=8, choices=CallFlowStatusChoice.choices, default=CallFlowStatusChoice.CDAY, verbose_name=_('Status'), help_text=_('select the status'))                     # noqa: E501, E221
    pin_number      = models.CharField(max_length=16, blank=True, null=True, default='0000', verbose_name=_('PIN Number'), help_text=_('Enter the pin number'))                                               # noqa: E501, E221
    label           = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Destination label'))                                                                                             # noqa: E501, E221
    sound           = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Sound'), help_text=_('Select the sound to play when the status is set to the destination'))                     # noqa: E501, E221
    app             = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Destination App.'))                                                                                              # noqa: E501, E221
    data            = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Destination'), help_text=_('Select the destination'))                                                           # noqa: E501, E221
    alternate_label = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Alternate label'))                                                                                               # noqa: E501, E221
    alternate_sound = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Alternate Sound'), help_text=_('Select the sound to play when the status is set to the alternate destination')) # noqa: E501, E221
    alternate_app   = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Alternate Destination App.'))                                                                                    # noqa: E501, E221
    alternate_data  = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Alternate Destination'), help_text=_('Select the alternate destination'))                                       # noqa: E501, E221
    context         = models.CharField(max_length=128, db_index=True, blank=True, null=True, verbose_name=_('Context'), help_text=_('Enter the context'))                                                     # noqa: E501, E221
    description     = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Description'))                                                                                                   # noqa: E501, E221
    dialplan_id     = models.UUIDField(blank=True, null=True, verbose_name=_('Dialplan UUID'))                                                                                                                # noqa: E501, E221
    created         = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                                               # noqa: E501, E221
    updated         = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                                                   # noqa: E501, E221
    synchronised    = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                                             # noqa: E501, E221
    updated_by      = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                                                           # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Call Flows'
        db_table = 'pbx_call_flows'

    def __str__(self):
        return self.name
