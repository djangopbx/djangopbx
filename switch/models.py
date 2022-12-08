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


class AccessControlDefaultChoice(models.TextChoices):
    CALLOW = 'allow',      'allow'
    CDENY  = 'deny', 'deny'


class EmailTemplateTypeChoice(models.TextChoices):
    CHTML     = 'html', 'HTML'
    CTEXT = 'text', 'Text'


class SwitchModuleCategoryChoice(models.TextChoices):
    C1 = 'Streams / Files', _('Streams / Files')
    C2 = 'File Format Interfaces', _('File Format Interfaces')
    C3 = 'Auto', _('Auto')
    C4 = 'Say', _('Say')
    C5 = 'Loggers', _('Loggers')
    C6 = 'Languages', _('Languages')
    C7 = 'XML Interfaces', _('XML Interfaces')
    C8 = 'Speech Recognition / Text to Speech', _('Speech Recognition / Text to Speech')
    C9 = 'Codecs', _('Codecs')
    CA = 'Endpoints', _('Endpoints')
    CB = 'Applications', _('Applications')
    CC = 'Dialplan Interfaces', _('Dialplan Interfaces')
    CD = 'Event Handlers', _('Event Handlers')
    CE = 'Other', _('Other')


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


class AccessControl(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Access Control'))
    name         = models.CharField(max_length=64, verbose_name=_('Name'))
    default      = models.CharField(max_length=8, choices=AccessControlDefaultChoice.choices, default=AccessControlDefaultChoice.CDENY, verbose_name=_('Default'))
    description  = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        db_table = 'pbx_access_controls'

    def __str__(self):
        return self.name


class AccessControlNode(models.Model):
    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Access Control None'))
    access_control_id = models.ForeignKey('AccessControl', on_delete=models.CASCADE, verbose_name=_('Access Control'))
    type              = models.CharField(max_length=8, choices=AccessControlDefaultChoice.choices, default=AccessControlDefaultChoice.CDENY,verbose_name=_('Type'))
    cidr              = models.CharField(max_length=64, blank=True, null=True, verbose_name='CIDR')
    domain            = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Domain'))
    description       = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))
    created           = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated           = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised      = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by        = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        db_table = 'pbx_access_control_nodes'

    def __str__(self):
        return str(self.id)


class EmailTemplate(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Email Template'))
    domain_id    = models.ForeignKey('tenants.Domain', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))
    language     = models.CharField(max_length=8, default='en-gb', verbose_name=_('Language'))
    category     = models.CharField(max_length=32, verbose_name=_('Category'))
    subcategory  = models.CharField(max_length=32, default='default', verbose_name=_('Sub category'))
    subject      = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Subject'))
    type         = models.CharField(max_length=8, choices=EmailTemplateTypeChoice.choices, default=EmailTemplateTypeChoice.CHTML, verbose_name=_('Type'))
    body         = models.TextField(blank=True, null=True, verbose_name=_('Body'))
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))
    description  = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        db_table = 'pbx_email_templates'

    def __str__(self):
        return f"{self.language}->{self.category}->{self.subcategory}->{self.type}"


class Modules(models.Model):
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Module'))
    label           = models.CharField(max_length=64, verbose_name=_('Label'))
    name            = models.CharField(max_length=64, verbose_name=_('Name'))
    category        = models.CharField(max_length=64, choices=SwitchModuleCategoryChoice.choices, default=SwitchModuleCategoryChoice.CB, verbose_name=_('Category'))
    sequence        = models.DecimalField(max_digits=11, decimal_places=0, default=10, verbose_name=_('Order'))
    enabled         = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))
    default_enabled = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Default Enabled'))
    description     = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))
    created         = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated         = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised    = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by      = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        db_table = 'pbx_modules'

