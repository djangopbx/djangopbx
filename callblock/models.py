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


class CallBlock(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Call Flow'))                                                           # noqa: E501, E221
    domain_id    = models.ForeignKey('tenants.Domain', db_column='domain_uuid', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))                       # noqa: E501, E221
    name         = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Name'), help_text=_('Enter the Caller ID Name to block.'))                             # noqa: E501, E221
    number       = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Number'), help_text=_('Enter the Caller ID Number to block.'))                         # noqa: E501, E221
    block_count  = models.DecimalField(max_digits=6, decimal_places=0, default=0, verbose_name=_('Block Count'), help_text=_('The number of time this number has been blocked')) # noqa: E501, E221
    app          = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Action App.'))                                                                         # noqa: E501, E221
    data         = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Action'), help_text=_('Set an action for calls from this number'))                    # noqa: E501, E221
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))                       # noqa: E501, E221
    description  = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Description'))                                                                         # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                     # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                         # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                   # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                                 # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Call Block'
        db_table = 'pbx_call_block'

    def __str__(self):
        return f'{self.name} {self.number}'
