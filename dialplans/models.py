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


#
# Choice classes
#
class DialplanInlineChoice(models.TextChoices):
    CNONE    = '',    _('Not Set')  # noqa: E221
    CTRUE  = 'true',  _('True')     # noqa: E221
    CFALSE = 'false', _('False')    # noqa: E221


class DialplanBreakChoice(models.TextChoices):
    CNONE    = '',         _('Not Set')  # noqa: E221
    CONTRUE  = 'on-true',  'On True'     # noqa: E221
    CONFALSE = 'on-false', 'On False'    # noqa: E221
    CALWAYS  = 'always',   'Always'      # noqa: E221
    CNEVER   = 'never',    'Never'       # noqa: E221


class DialplanTagChoice(models.TextChoices):
    CCONDITION  = 'condition',   'Condition'           # noqa: E221
    CREGEXP     = 'regex',       'Regular Expression'  # noqa: E221
    CACTION     = 'action',      'Action'              # noqa: E221
    CANTIACTION = 'anti-action', 'Anti Action'         # noqa: E221


class TimeConditionConditionChoice(models.TextChoices):
    CYEAR     = 'year',          _('Year')           # noqa: E221
    CMON      = 'mon',           _('Month')          # noqa: E221
    CMDAY     = 'mday',          _('Day of Month')   # noqa: E221
    CWDAY     = 'wday',          _('Day of Week')    # noqa: E221
    CWEEK     = 'week',          _('Week of Year')   # noqa: E221
    CMWEEK    = 'mweek',         _('Week of Month')  # noqa: E221
    CHOUR     = 'hour',          _('Hour of Day')    # noqa: E221
    CMINOFDAY = 'minute-of-day', _('Time of Day')    # noqa: E221
    CDATETIME = 'date-time',     _('Date & Time')    # noqa: E221


#
# Model classes
#
class Dialplan(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Dialplan'))                                                          # noqa: E501, E221
    domain_id    = models.ForeignKey('tenants.Domain', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))                                              # noqa: E501, E221
    app_id       = models.UUIDField(blank=True, null=True, verbose_name=_('AppUuid'))                                                                                          # noqa: E501, E221
    hostname     = models.CharField(max_length=128, db_index=True, blank=True, null=True, verbose_name=_('Hostname'))                                                          # noqa: E501, E221
    context      = models.CharField(max_length=128, db_index=True, blank=True, null=True, verbose_name=_('Context'))                                                           # noqa: E501, E221
    category     = models.CharField(max_length=32, db_index=True, blank=True, null=True, default=_('General'), verbose_name=_('Category'))                                     # noqa: E501, E221
    name         = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Name'))                                                                              # noqa: E501, E221
    number       = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Number'))                                                                            # noqa: E501, E221
    destination  = models.CharField(max_length=8, db_index=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Destination')) # noqa: E501, E221
    dp_continue  = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Continue'))                   # noqa: E501, E221
    xml          = models.TextField(blank=True, null=True, verbose_name=_('Xml'))                                                                                              # noqa: E501, E221
    sequence     = models.DecimalField(max_digits=3, decimal_places=0, default=200, verbose_name=_('Order'))                                                                   # noqa: E501, E221
    enabled      = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))         # noqa: E501, E221
    description  = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))                                                                      # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                   # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                       # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                 # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                               # noqa: E501, E221

    class Meta:
        db_table = 'pbx_dialplans'

    def __str__(self):
        return self.name


class DialplanDetail(models.Model):

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('DialplanDetail'))                                                   # noqa: E501, E221
    dialplan_id  = models.ForeignKey('Dialplan', on_delete=models.CASCADE, verbose_name=_('Dialplan'))                                                                        # noqa: E501, E221
    tag          = models.CharField(max_length=32, choices=DialplanTagChoice.choices, default=DialplanTagChoice.CCONDITION, verbose_name=_('Tag'))                            # noqa: E501, E221
    type         = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Type'))                                                                            # noqa: E501, E221
    data         = models.CharField(max_length=512, blank=True, null=True, verbose_name=_('Data'))                                                                            # noqa: E501, E221
    dp_break     = models.CharField(max_length=8, blank=True, null=True, choices=DialplanBreakChoice.choices, default=DialplanBreakChoice.CNONE, verbose_name=_('Break'))     # noqa: E501, E221
    inline       = models.CharField(max_length=8, blank=True, null=True, choices=DialplanInlineChoice.choices, default=DialplanInlineChoice.CNONE, verbose_name=_('Inline'))  # noqa: E501, E221
    group        = models.DecimalField(max_digits=11, decimal_places=0, default=0, verbose_name=_('Group'))                                                                   # noqa: E501, E221
    enabled      = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))        # noqa: E501, E221
    sequence     = models.DecimalField(max_digits=11, decimal_places=0, default=10, verbose_name=_('Order'))                                                                  # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                  # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                      # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                              # noqa: E501, E221

    class Meta:
        db_table = 'pbx_dialplan_details'

    def __str__(self):
        return str(self.id)


class DialplanExcludes(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Dialplan Excludes'))     # noqa: E501, E221
    domain_id    = models.ForeignKey('tenants.Domain', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))  # noqa: E501, E221
    domain_name  = models.CharField(max_length=128, db_index=True, verbose_name=_('Domain Name'))                                  # noqa: E501, E221
    name         = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Dialplan Name'))                         # noqa: E501, E221
    app_id       = models.UUIDField(verbose_name=_('AppUuid'))                                                                     # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                       # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                           # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                     # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                   # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Dialplan Excludes'
        db_table = 'pbx_dialplan_excludes'

    def __str__(self):
        return f"{self.id}->{self.app_id}: {self.name}"
