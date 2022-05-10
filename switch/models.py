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
class SwitchVariableCategoryChoice(models.TextChoices):
    CTONES              = 'Tones',                 _('Tones')
    CRINGTONES          = 'Ringtones',             _('Ringtones')
    CMUSICONHOLD        = 'Music on Hold',         _('Music on Hold')
    CSIP                = 'SIP',                   _('SIP')
    CSIPPROFILEINTERNAL = 'SIP Profile: Internal', _('SIP Profile: Internal')
    CSIPPROFILEEXTERNAL = 'SIP Profile: External', _('SIP Profile: External')
    CODECS              = 'Codecs',                _('Codecs')
    CXMPP               = 'XMPP',                  _('XMPP')
    CDEFAULTS           = 'Defaults',              _('Defaults')
    CSOUND              = 'Sound',                 _('Sound')
    CIPADDRESS          = 'IP Address',            _('IP Address')
    COTHER              = 'Other',                 _('Other')


class SwitchVariableCommandChoice(models.TextChoices):
    CSET     = 'set',      'set'
    CEXECSET = 'exec-set', 'exec-set'


#
# model classes
#
class SipProfileDomain(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('SIP Profile Domain'))
    sip_profile_id = models.ForeignKey('SipProfile', db_column='sip_profile_id', on_delete=models.CASCADE, verbose_name=_('SIP Profile'))
    name           = models.CharField(max_length=128, default='all', verbose_name=_('Name'))
    alias          = models.CharField(max_length=8, default='false', verbose_name=_('Alias'))
    parse          = models.CharField(max_length=8, default='false', verbose_name=_('Parse'))
    created        = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated        = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised   = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by     = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        db_table = 'pbx_sip_profile_domains'

    def __str__(self):
        return self.name


class SipProfileSetting(models.Model):
    id        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('SIP Profile Setting'))
    sip_profile_id = models.ForeignKey('SipProfile', db_column='sip_profile_id', on_delete=models.CASCADE, verbose_name=_('SIP Profile'))
    name           = models.CharField(max_length=64, verbose_name=_('Setting Name'))
    value          = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Value'))
    enabled        = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))
    description    = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))
    created        = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated        = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised   = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by     = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        db_table = 'pbx_sip_profile_settings'

    def __str__(self):
        return self.name


class SipProfile(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('SIP Profile'))
    name         = models.CharField(max_length=64, verbose_name=_('Name'))
    hostname     = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Hostname'))
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))
    description  = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        db_table = 'pbx_sip_profiles'

    def __str__(self):
        return self.name


class SwitchVariable(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Switch Variable'))
    category     = models.CharField(max_length=64, choices=SwitchVariableCategoryChoice.choices, default=SwitchVariableCategoryChoice.CDEFAULTS, verbose_name=_('Category'))
    name         = models.CharField(max_length=64, verbose_name=_('Name'))
    value        = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Value'))
    command      = models.CharField(max_length=16, choices=SwitchVariableCommandChoice.choices, default=SwitchVariableCommandChoice.CSET, blank=True, null=True, verbose_name=_('Command'))
    hostname     = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Hostname'))
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))
    sequence     = models.DecimalField(max_digits=11, decimal_places=0, default=10, verbose_name=_('Order'))
    description  = models.TextField(max_length=254, blank=True, null=True, verbose_name=_('Description'))
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        db_table = 'pbx_vars'

    def __str__(self):
        return self.name
