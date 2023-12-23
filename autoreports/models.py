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

# for view report link
from django.urls import reverse
from django.utils.html import mark_safe


class AutoReportFrequencyChoice(models.TextChoices):
    CMONTHLY = 'month', _('Monthly') # noqa: E221
    CWEEKLY  = 'week',  _('Weekly')  # noqa: E221
    CDAILY   = 'day',   _('Daily')   # noqa: E221
    CHOURLY  = 'hour',  _('Hourly')  # noqa: E221


class AutoReports(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Report'))                                                                         # noqa: E501, E221
    domain_id    = models.ForeignKey('tenants.Domain', db_column='domain_uuid', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))                                  # noqa: E501, E221
    name         = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Name'))                                                                                           # noqa: E501, E221
    title        = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Title'))                                                                                         # noqa: E501, E221
    message      = models.TextField(blank=True, null=True, verbose_name=_('Message'), help_text=_('Enter any message to be show with the report.  Eg. Company address'))                    # noqa: E501, E221
    footer       = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Footer'), help_text=_('Appears in small print at the end of the report'))                        # noqa: E501, E221
    recipients   = models.TextField(verbose_name=_('Recipients'), help_text=_('Enter email addresses, one per line'))                                                                       # noqa: E501, E221
    frequency    = models.CharField(max_length=8, blank=True, null=True, choices=AutoReportFrequencyChoice.choices, default=AutoReportFrequencyChoice.CWEEKLY, verbose_name=_('Frequency')) # noqa: E501, E221
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))                                  # noqa: E501, E221
    description  = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Description'))                                                                                   # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                                # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                                    # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                              # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                                            # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Auto Report'
        db_table = 'pbx_auto_report'

    def view_report(self):
        return mark_safe('<a class="grp-button" href="%s">%s</a>' % (
                    reverse('viewreport', args=[self.id]), _('View Report')
                    ))

    view_report.short_description = _('View Report')

    def __str__(self):
        return self.name


class AutoReportSections(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Report'))                                         # noqa: E501, E221
    auto_report_id = models.ForeignKey('AutoReports', db_column='auto_report_id', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Report'))  # noqa: E501, E221
    title          = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('(sub) Title'))                                                   # noqa: E501, E221
    sequence       = models.DecimalField(max_digits=3, decimal_places=0, default=10, verbose_name=_('Sequence'))                                              # noqa: E501, E221
    sql            = models.TextField(verbose_name=_('SQL'), help_text=_('Enter the SQL query for this report section'))                                      # noqa: E501, E221
    message        = models.TextField(blank=True, null=True, verbose_name=_('Message'), help_text=_('Notes about this section for the customer'))             # noqa: E501, E221
    enabled        = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))  # noqa: E501, E221
    description    = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Description'))                                                   # noqa: E501, E221
    created        = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                # noqa: E501, E221
    updated        = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                    # noqa: E501, E221
    synchronised   = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                              # noqa: E501, E221
    updated_by     = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                            # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Auto Report Section'
        db_table = 'pbx_auto_report_section'

    def __str__(self):
        return self.title

