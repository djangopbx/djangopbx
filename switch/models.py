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
    CTONES              = 'Tones',                 _('Tones')                  # noqa: E221
    CRINGTONES          = 'Ringtones',             _('Ringtones')              # noqa: E221
    CMUSICONHOLD        = 'Music on Hold',         _('Music on Hold')          # noqa: E221
    CSIP                = 'SIP',                   _('SIP')                    # noqa: E221
    CSIPPROFILEINTERNAL = 'SIP Profile: Internal', _('SIP Profile: Internal')  # noqa: E221
    CSIPPROFILEEXTERNAL = 'SIP Profile: External', _('SIP Profile: External')  # noqa: E221
    CODECS              = 'Codecs',                _('Codecs')                 # noqa: E221
    CXMPP               = 'XMPP',                  _('XMPP')                   # noqa: E221
    CDSN                = 'DSN',                   _('DSN')                    # noqa: E221
    CDEFAULTS           = 'Defaults',              _('Defaults')               # noqa: E221
    CSOUND              = 'Sound',                 _('Sound')                  # noqa: E221
    CIPADDRESS          = 'IP Address',            _('IP Address')             # noqa: E221
    COTHER              = 'Other',                 _('Other')                  # noqa: E221


class SwitchVariableCommandChoice(models.TextChoices):
    CSET     = 'set',      'set'       # noqa: E221
    CEXECSET = 'exec-set', 'exec-set'  # noqa: E221


class AccessControlDefaultChoice(models.TextChoices):
    CALLOW = 'allow',      'allow'  # noqa: E221
    CDENY  = 'deny', 'deny'         # noqa: E221


class EmailTemplateTypeChoice(models.TextChoices):
    CHTML     = 'html', 'HTML'  # noqa: E221
    CTEXT = 'text', 'Text'      # noqa: E221


class SwitchModuleCategoryChoice(models.TextChoices):
    C1 = 'Streams / Files', _('Streams / Files')                                          # noqa: E221
    C2 = 'File Format Interfaces', _('File Format Interfaces')                            # noqa: E221
    C3 = 'Auto', _('Auto')                                                                # noqa: E221
    C4 = 'Say', _('Say')                                                                  # noqa: E221
    C5 = 'Loggers', _('Loggers')                                                          # noqa: E221
    C6 = 'Languages', _('Languages')                                                      # noqa: E221
    C7 = 'XML Interfaces', _('XML Interfaces')                                            # noqa: E221
    C8 = 'Speech Recognition / Text to Speech', _('Speech Recognition / Text to Speech')  # noqa: E221
    C9 = 'Codecs', _('Codecs')                                                            # noqa: E221
    CA = 'Endpoints', _('Endpoints')                                                      # noqa: E221
    CB = 'Applications', _('Applications')                                                # noqa: E221
    CC = 'Dialplan Interfaces', _('Dialplan Interfaces')                                  # noqa: E221
    CD = 'Event Handlers', _('Event Handlers')                                            # noqa: E221
    CE = 'Other', _('Other')                                                              # noqa: E221


class IpStatusChoice(models.IntegerChoices):
    CPERM = 3, _('Permanent')  # noqa: E221
    CCUR  = 1, _('Current')    # noqa: E221
    COBS  = 0, _('Obsolete')   # noqa: E221


#
# model classes
#
class SipProfileDomain(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('SIP Profile Domain'))          # noqa: E501, E221
    sip_profile_id = models.ForeignKey('SipProfile', db_column='sip_profile_id', on_delete=models.CASCADE, verbose_name=_('SIP Profile'))  # noqa: E501, E221
    name           = models.CharField(max_length=128, default='all', verbose_name=_('Name'))                                               # noqa: E501, E221
    alias          = models.CharField(max_length=8, default='false', verbose_name=_('Alias'))                                              # noqa: E501, E221
    parse          = models.CharField(max_length=8, default='false', verbose_name=_('Parse'))                                              # noqa: E501, E221
    created        = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                             # noqa: E501, E221
    updated        = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                 # noqa: E501, E221
    synchronised   = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                           # noqa: E501, E221
    updated_by     = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                         # noqa: E501, E221

    class Meta:
        db_table = 'pbx_sip_profile_domains'

    def __str__(self):
        return self.name


class SipProfileSetting(models.Model):
    id        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('SIP Profile Setting'))                                 # noqa: E501, E221
    sip_profile_id = models.ForeignKey('SipProfile', db_column='sip_profile_id', on_delete=models.CASCADE, verbose_name=_('SIP Profile'))                     # noqa: E501, E221
    name           = models.CharField(max_length=64, verbose_name=_('Setting Name'))                                                                          # noqa: E501, E221
    value          = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Value'))                                                         # noqa: E501, E221
    enabled        = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))  # noqa: E501, E221
    description    = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))                                                   # noqa: E501, E221
    created        = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                # noqa: E501, E221
    updated        = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                    # noqa: E501, E221
    synchronised   = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                              # noqa: E501, E221
    updated_by     = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                            # noqa: E501, E221

    class Meta:
        db_table = 'pbx_sip_profile_settings'

    def __str__(self):
        return self.name


class SipProfile(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('SIP Profile'))                                    # noqa: E501, E221
    name         = models.CharField(max_length=64, verbose_name=_('Name'))                                                                                  # noqa: E501, E221
    hostname     = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Hostname'))                                                      # noqa: E501, E221
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))  # noqa: E501, E221
    description  = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))                                                   # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                    # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                              # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                            # noqa: E501, E221

    class Meta:
        db_table = 'pbx_sip_profiles'

    def __str__(self):
        return self.name


class SwitchVariable(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Switch Variable'))                                                                 # noqa: E501, E221
    category     = models.CharField(max_length=64, choices=SwitchVariableCategoryChoice.choices, default=SwitchVariableCategoryChoice.CDEFAULTS, verbose_name=_('Category'))                 # noqa: E501, E221
    name         = models.CharField(max_length=64, verbose_name=_('Name'))                                                                                                                   # noqa: E501, E221
    value        = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Value'))                                                                                          # noqa: E501, E221
    command      = models.CharField(max_length=16, choices=SwitchVariableCommandChoice.choices, default=SwitchVariableCommandChoice.CSET, blank=True, null=True, verbose_name=_('Command'))  # noqa: E501, E221
    hostname     = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Hostname'))                                                                                       # noqa: E501, E221
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))                                   # noqa: E501, E221
    sequence     = models.DecimalField(max_digits=11, decimal_places=0, default=10, verbose_name=_('Order'))                                                                                 # noqa: E501, E221
    description  = models.TextField(max_length=254, blank=True, null=True, verbose_name=_('Description'))                                                                                    # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                                 # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                                     # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                               # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                                             # noqa: E501, E221

    class Meta:
        db_table = 'pbx_vars'

    def __str__(self):
        return self.name


class AccessControl(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Access Control'))                                         # noqa: E501, E221
    name         = models.CharField(max_length=64, verbose_name=_('Name'))                                                                                          # noqa: E501, E221
    default      = models.CharField(max_length=8, choices=AccessControlDefaultChoice.choices, default=AccessControlDefaultChoice.CDENY, verbose_name=_('Default'))  # noqa: E501, E221
    description  = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))                                                           # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                        # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                            # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                      # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                    # noqa: E501, E221

    class Meta:
        db_table = 'pbx_access_controls'

    def __str__(self):
        return self.name


class AccessControlNode(models.Model):
    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Access Control None'))                                 # noqa: E501, E221
    access_control_id = models.ForeignKey('AccessControl', on_delete=models.CASCADE, verbose_name=_('Access Control'))                                                # noqa: E501, E221
    type              = models.CharField(max_length=8, choices=AccessControlDefaultChoice.choices, default=AccessControlDefaultChoice.CDENY, verbose_name=_('Type'))  # noqa: E501, E221
    cidr              = models.CharField(max_length=64, blank=True, null=True, verbose_name='CIDR')                                                                   # noqa: E501, E221
    domain            = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Domain'))                                                              # noqa: E501, E221
    description       = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))                                                        # noqa: E501, E221
    created           = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                     # noqa: E501, E221
    updated           = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                         # noqa: E501, E221
    synchronised      = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                   # noqa: E501, E221
    updated_by        = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                 # noqa: E501, E221

    class Meta:
        db_table = 'pbx_access_control_nodes'

    def __str__(self):
        return str(self.id)


class EmailTemplate(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Email Template'))                                 # noqa: E501, E221
    domain_id    = models.ForeignKey('tenants.Domain', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))                           # noqa: E501, E221
    language     = models.CharField(max_length=8, default='en-gb', verbose_name=_('Language'))                                                              # noqa: E501, E221
    category     = models.CharField(max_length=32, verbose_name=_('Category'))                                                                              # noqa: E501, E221
    subcategory  = models.CharField(max_length=32, default='default', verbose_name=_('Sub category'))                                                       # noqa: E501, E221
    subject      = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Subject'))                                                       # noqa: E501, E221
    type         = models.CharField(max_length=8, choices=EmailTemplateTypeChoice.choices, default=EmailTemplateTypeChoice.CHTML, verbose_name=_('Type'))   # noqa: E501, E221
    body         = models.TextField(blank=True, null=True, verbose_name=_('Body'))                                                                          # noqa: E501, E221
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))  # noqa: E501, E221
    description  = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))                                                   # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                    # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                              # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                            # noqa: E501, E221

    class Meta:
        db_table = 'pbx_email_templates'

    def __str__(self):
        return f"{self.language}->{self.category}->{self.subcategory}->{self.type}"


class Modules(models.Model):
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Module'))                                                 # noqa: E501, E221
    label           = models.CharField(max_length=64, verbose_name=_('Label'))                                                                                         # noqa: E501, E221
    name            = models.CharField(max_length=64, verbose_name=_('Name'))                                                                                          # noqa: E501, E221
    category        = models.CharField(max_length=64, choices=SwitchModuleCategoryChoice.choices, default=SwitchModuleCategoryChoice.CB, verbose_name=_('Category'))   # noqa: E501, E221
    sequence        = models.DecimalField(max_digits=11, decimal_places=0, default=10, verbose_name=_('Order'))                                                        # noqa: E501, E221
    enabled         = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))          # noqa: E501, E221
    default_enabled = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Default Enabled'))  # noqa: E501, E221
    description     = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))                                                           # noqa: E501, E221
    created         = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                        # noqa: E501, E221
    updated         = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                            # noqa: E501, E221
    synchronised    = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                      # noqa: E501, E221
    updated_by      = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                    # noqa: E501, E221

    class Meta:
        db_table = 'pbx_modules'


class IpRegister(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)                                                                                    # noqa: E501, E221
    address      = models.GenericIPAddressField(protocol='both', unpack_ipv4=False, unique=True, verbose_name=_('IP Address'))                                               # noqa: E501, E221
    status       = models.DecimalField(max_digits=2, decimal_places=0, choices=IpStatusChoice.choices, default=IpStatusChoice.CCUR, max_length=1, verbose_name=_('Status'))  # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                 # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                     # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                               # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, default='system', verbose_name=_('Updated by'))                                                                           # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'IP Register'
        db_table = 'pbx_ip_register'

    def __str__(self):
        return self.address
