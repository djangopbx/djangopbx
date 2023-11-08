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


class NumberTranslations(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Number Translation'))                            # noqa: E501, E221
    name         = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Name'))                                                          # noqa: E501, E221
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled')) # noqa: E501, E221
    description  = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Description'))                                                   # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                               # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                   # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                             # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                           # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Number Translations'
        db_table = 'pbx_number_translations'

    def __str__(self):
        return self.name


class NumberTranslationDetails(models.Model):
    id                    = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Number Translation Detail')) # noqa: E501, E221
    number_translation_id = models.ForeignKey('NumberTranslations', on_delete=models.CASCADE, verbose_name=_('Number Translation'))             # noqa: E501, E221
    td_regex              = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Regular Expression'))                       # noqa: E501, E221
    td_replace            = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Replace'))                                  # noqa: E501, E221
    td_order              = models.DecimalField(max_digits=3, decimal_places=0, default=10, verbose_name=_('Order'))                            # noqa: E501, E221
    created               = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                           # noqa: E501, E221
    updated               = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                               # noqa: E501, E221
    synchronised          = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                         # noqa: E501, E221
    updated_by            = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                       # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Number Translation Details'
        db_table = 'pbx_number_translation_details'

    def __str__(self):
        return str(self.number_translation_id)
