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

class PhraseDetailFunctionChoice(models.TextChoices):
    CPLAY = 'play-file', _('Play')    # noqa: E221
    CEXEC = 'execute',   _('Execute') # noqa: E221


class PhraseDetails(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Phrase Detail'))                                           # noqa: E501, E221
    phrase_id    = models.ForeignKey('Phrases', on_delete=models.CASCADE, verbose_name=_('Phrase'))                                                                # noqa: E501, E221
    pfunction    = models.CharField(max_length=16, choices=PhraseDetailFunctionChoice.choices, default=PhraseDetailFunctionChoice.CPLAY, verbose_name=_('Function')) # noqa: E501, E221
    data         = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Action'))                                                                 # noqa: E501, E221
    sequence     = models.DecimalField(max_digits=11, decimal_places=0, default=0, verbose_name=_('Order'))                                                          # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                         # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                             # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                       # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                     # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Phrase Details'
        db_table = 'pbx_phrase_details'

    def __str__(self):
        return str(self.id)


class Phrases(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Phrase'))                                                                                     # noqa: E501, E221
    domain_id    = models.ForeignKey('tenants.Domain', db_column='domain_uuid', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))                                              # noqa: E501, E221
    name         = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Name'), help_text=_('Enter a name (Example: abc_audio)'))                                                     # noqa: E501, E221
    language     = models.CharField(max_length=8, blank=False, null=False, default='en', verbose_name=_('Language'), help_text=_('Language used in the phrase'))                                        # noqa: E501, E221
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'), help_text=_('Set the status of the phrase')) # noqa: E501, E221
    description  = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Description'))                                                                                                # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                                            # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                                                # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                                          # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                                                        # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Phrases'
        db_table = 'pbx_phrases'

    def __str__(self):
        return self.name
