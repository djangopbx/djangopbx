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
    EnabledTrueFalseChoice, PrimaryTrueFalseChoice, CallDirectionChoice,
)
from django.db.models import Q

#
# Choice classes
#
class DialplanInlineChoice(models.TextChoices):
    CNONE    = '',    _('Not Set')
    CTRUE  = 'true',  _('True')
    CFALSE = 'false', _('False')


class DialplanBreakChoice(models.TextChoices):
    CNONE    = '',         _('Not Set')
    CONTRUE  = 'on-true',  'On True'
    CONFALSE = 'on-false', 'On False'
    CALWAYS  = 'always',   'Always'
    CNEVER   = 'never',    'Never'


class DialplanTagChoice(models.TextChoices):
    CCONDITION  = 'condition',   'Condition'
    CREGEXP     = 'regex',       'Regular Expression'
    CACTION     = 'action',      'Action'
    CANTIACTION = 'anti-action', 'Anti Action'


class DestinationUsageChoice(models.TextChoices):
    CVOICE = 1,  _('Voice')
    CFAX   = 2,  _('Fax')
    CTEXT  = 3,  _('Text')


class CallDirectionChoice(models.TextChoices):
    CINBOUND  = 'inbound' , _('Inbound')
    COUTBOUND = 'outbound', _('Outbound')


#
# Model classes
#
class Dialplan(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Dialplan'))
    domain_id    = models.ForeignKey('tenants.Domain', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))
    app_id       = models.UUIDField(blank=True, null=True, verbose_name=_('AppUuid'))
    hostname     = models.CharField(max_length=128, db_index=True, blank=True, null=True, verbose_name=_('Hostname'))
    context      = models.CharField(max_length=128, db_index=True, blank=True, null=True, verbose_name=_('Context'))
    category     = models.CharField(max_length=32, db_index=True, blank=True, null=True, default=_('General'), verbose_name=_('Category'))
    name         = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Name'))
    number       = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Number'))
    destination  = models.CharField(max_length=8, db_index=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Destination'))
    dp_continue  = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Continue'))
    xml          = models.TextField(blank=True, null=True, verbose_name=_('Xml'))
    sequence     = models.DecimalField(max_digits=3, decimal_places=0, default=200, verbose_name=_('Order'))
    enabled      = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))
    description  = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        db_table = 'pbx_dialplans'

    def __str__(self):
        return self.name


class DialplanDetail(models.Model):

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('DialplanDetail'))
    dialplan_id  = models.ForeignKey('Dialplan', on_delete=models.CASCADE, verbose_name=_('Dialplan'))
    tag          = models.CharField(max_length=32, choices=DialplanTagChoice.choices, default=DialplanTagChoice.CCONDITION, verbose_name=_('Tag'))
    type         = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Type'))
    data         = models.CharField(max_length=512, blank=True, null=True, verbose_name=_('Data'))
    dp_break     = models.CharField(max_length=8, blank=True, null=True, choices=DialplanBreakChoice.choices, default=DialplanBreakChoice.CNONE, verbose_name=_('Break'))
    inline       = models.CharField(max_length=8, blank=True, null=True, choices=DialplanInlineChoice.choices, default=DialplanInlineChoice.CNONE, verbose_name=_('Inline'))
    group        = models.DecimalField(max_digits=11, decimal_places=0, default=0, verbose_name=_('Group'))
    sequence     = models.DecimalField(max_digits=11, decimal_places=0, default=10, verbose_name=_('Order'))
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        db_table = 'pbx_dialplan_details'

    def __str__(self):
        return str(self.id)


