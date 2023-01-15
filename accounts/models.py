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
    EnabledTrueFalseChoice, EnabledTrueFalseNoneChoice, ConfirmChoice,
)


class MissedCallAppChoice(models.TextChoices):
    CNONE  = '',         _('Not Set')  # noqa: E221
    CEMAIL = 'email',    _('Email')    # noqa: E221


class RecordChoice(models.TextChoices):
    CDISABLED = '',         _('Disabled')  # noqa: E221
    CALL      = 'all',      _('All')       # noqa: E221
    CLOCAL    = 'local',    _('Local')     # noqa: E221
    CINBOUND  = 'inbound',  _('Inbound')   # noqa: E221
    COUTBOUND = 'outbound', _('Outbound')  # noqa: E221


class SipForceContactChoice(models.TextChoices):
    CNONE    = '',                                _('')                                 # noqa: E221
    CIPPORT  = 'NDLB-connectile-dysfunction',     _('Rewrite Contact IP and Port')      # noqa: E221
    CIPPORT2 = 'NDLB-connectile-dysfunction-2.0', _('Rewrite Contact IP and Port 2.0')  # noqa: E221
    CTLSPORT = 'NDLB-tls-connectile-dysfunction', _('Rewrite TLS Contact Port')         # noqa: E221


class SipBypassMediaChoice(models.TextChoices):
    CNONE    = '',                          _('')                           # noqa: E221
    CIPPORT  = 'bypass-media',              _('Bypass Media')               # noqa: E221
    CIPPORT2 = 'bypass-media-after-bridge', _('Bypass Media After Bridge')  # noqa: E221
    CTLSPORT = 'proxy-media',               _('Proxy Media')                # noqa: E221


class RegisterTransportChoice(models.TextChoices):
    CNONE = '',     ''    # noqa: E221
    CUDP  = 'udp', 'udp'  # noqa: E221
    CTCP  = 'tcp', 'tcp'  # noqa: E221
    CTLS  = 'tls', 'tls'  # noqa: E221


class Extension(models.Model):

    id                                      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Extension'))                                                                      # noqa: E501, E221
    domain_id                               = models.ForeignKey('tenants.Domain', db_column='domain_uuid', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))                                  # noqa: E501, E221
    extension                               = models.CharField(max_length=32, db_index=True, verbose_name=_('Extension'))                                                                                              # noqa: E501, E221
    number_alias                            = models.CharField(max_length=16, db_index=True, blank=True, null=True, verbose_name=_('Number Alias'))                                                                    # noqa: E501, E221
    password                                = models.CharField(max_length=32, verbose_name=_('Password'))                                                                                                              # noqa: E501, E221
    accountcode                             = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Account Code'))                                                                                   # noqa: E501, E221
    effective_caller_id_name                = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Effective Caller ID Name'))                                                                       # noqa: E501, E221
    effective_caller_id_number              = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Effective Caller ID Number'))                                                                     # noqa: E501, E221
    outbound_caller_id_name                 = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Outbound Caller ID Name'))                                                                        # noqa: E501, E221
    outbound_caller_id_number               = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Outbound Caller ID Number'))                                                                      # noqa: E501, E221
    emergency_caller_id_name                = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Emergency Caller ID Name'))                                                                       # noqa: E501, E221
    emergency_caller_id_number              = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Emergency Caller ID Number'))                                                                     # noqa: E501, E221
    directory_first_name                    = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Directory First Name'))                                                                           # noqa: E501, E221
    directory_last_name                     = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Directory Family Name'))                                                                          # noqa: E501, E221
    directory_visible                       = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Directory Visible'))                        # noqa: E501, E221
    directory_exten_visible                 = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Directory Ext. Visible'))                   # noqa: E501, E221
    limit_max                               = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True, default=5, verbose_name=_('Limit Max'))                                                      # noqa: E501, E221
    limit_destination                       = models.CharField(max_length=32, blank=True, null=True, default="error/user_busy", verbose_name=_('Limit Destination'))                                                   # noqa: E501, E221
    missed_call_app                         = models.CharField(max_length=32, blank=True, null=True, choices=MissedCallAppChoice.choices, default=MissedCallAppChoice.CNONE, verbose_name=_('Missed Call'))            # noqa: E501, E221
    missed_call_data                        = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Missed Call Data'), help_text=_('Typically an email address or comma separated addresses'))      # noqa: E501, E221
    user_context                            = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Context'))                                                                                       # noqa: E501, E221
    toll_allow                              = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Toll Allow'))                                                                                     # noqa: E501, E221
    call_timeout                            = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True, default=300, verbose_name=_('Call Timeout'))                                                 # noqa: E501, E221
    call_group                              = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Call Group'))                                                                                     # noqa: E501, E221
    call_screen_enabled                     = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Call Screen'))                             # noqa: E501, E221
    user_record                             = models.CharField(max_length=8, choices=RecordChoice.choices, default=RecordChoice.CDISABLED, blank=True, null=True, verbose_name=_('Record'))                            # noqa: E501, E221
    hold_music                              = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Hold Music'))                                                                                     # noqa: E501, E221
    auth_acl                                = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Auth ACL'))                                                                                       # noqa: E501, E221
    cidr                                    = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('CIDR'))                                                                                          # noqa: E501, E221
    sip_force_contact                       = models.CharField(max_length=64, choices=SipForceContactChoice.choices, default=SipForceContactChoice.CNONE, blank=True, null=True, verbose_name=_('SIP Force Contact'))  # noqa: E501, E221
    nibble_account                          = models.DecimalField(max_digits=1, decimal_places=0, blank=True, null=True, verbose_name=_('Nibble Account'))                                                             # noqa: E501, E221
    sip_force_expires                       = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True, verbose_name=_('SIP Force Expires'))                                                         # noqa: E501, E221
    mwi_account                             = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('MWI Account'))                                                                                   # noqa: E501, E221
    sip_bypass_media                        = models.CharField(max_length=32, choices=SipForceContactChoice.choices, default=SipForceContactChoice.CNONE, blank=True, null=True, verbose_name=_('SIP Bypass Media'))   # noqa: E501, E221
    unique_id                               = models.DecimalField(max_digits=1, decimal_places=0, blank=True, null=True, verbose_name=_('Unique ID'))                                                                  # noqa: E501, E221
    dial_string                             = models.TextField(blank=True, null=True, verbose_name=_('Dial String'))                                                                                                   # noqa: E501, E221
    dial_user                               = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Dial User'))                                                                                      # noqa: E501, E221
    dial_domain                             = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Dial Domain'))                                                                                   # noqa: E501, E221
    do_not_disturb                          = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Do Not Disturb'))                          # noqa: E501, E221
    forward_all_destination                 = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Forward All Destination'))                                                                        # noqa: E501, E221
    forward_all_enabled                     = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Forward All Enabled'))                     # noqa: E501, E221
    forward_busy_destination                = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Forward Busy Destination'))                                                                       # noqa: E501, E221
    forward_busy_enabled                    = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Forward Busy Enabled'))                    # noqa: E501, E221
    forward_no_answer_destination           = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Forward No Answer Destination'))                                                                  # noqa: E501, E221
    forward_no_answer_enabled               = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Forward No Answer Enabled'))               # noqa: E501, E221
    forward_user_not_registered_destination = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Forward Not Registered Destination'))                                                             # noqa: E501, E221
    forward_user_not_registered_enabled     = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Forward Not Registered Enabled'))          # noqa: E501, E221
    follow_me_uuid                          = models.UUIDField(blank=True, null=True, verbose_name=_('Follow Me UUID'))                                                                                                # noqa: E501, E221
    forward_caller_id                       = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Caller ID Number'))                                                                               # noqa: E501, E221
    follow_me_enabled                       = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE,  verbose_name=_('Follow Me Enabled'))                      # noqa: E501, E221
    follow_me_destinations                  = models.TextField(blank=True, null=True, verbose_name=_('Follow me Destinations'))                                                                                        # noqa: E501, E221
    enabled                                 = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))                                  # noqa: E501, E221
    description                             = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Description'))                                                                                    # noqa: E501, E221
    absolute_codec_string                   = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Absolute Codec String'))                                                                          # noqa: E501, E221
    force_ping                              = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Force Ping'))                              # noqa: E501, E221
    created                                 = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                                # noqa: E501, E221
    updated                                 = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                                    # noqa: E501, E221
    synchronised                            = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                              # noqa: E501, E221
    updated_by                              = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                                            # noqa: E501, E221

    class Meta:
        db_table = 'pbx_extensions'
        unique_together = (('domain_id', 'extension'), ('domain_id', 'number_alias'))

    def __str__(self):
        return self.extension


class ExtensionUser(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Extension User'))                                                                # noqa: E501, E221
    extension_id   = models.ForeignKey('Extension', db_column='extension_uuid', related_name='extensionuser', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Extension'))  # noqa: E501, E221
    user_uuid      = models.ForeignKey('tenants.Profile', models.SET_NULL, to_field='user_uuid', db_column='user_uuid', blank=True, null=True, verbose_name=_('User'))                       # noqa: E501, E221
    default_user   = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Default'))                                 # noqa: E501, E221
    created        = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                               # noqa: E501, E221
    updated        = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                                   # noqa: E501, E221
    synchronised   = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                             # noqa: E501, E221
    updated_by     = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                                           # noqa: E501, E221

    class Meta:
        db_table = 'pbx_extension_users'

    def __str__(self):
        return str(self.id)


class FollowMeDestination(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Extension User'))                                     # noqa: E501, E221
    extension_id = models.ForeignKey('Extension', db_column='extension_uuid', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Extension'))     # noqa: E501, E221
    destination  = models.CharField(max_length=32, verbose_name=_('Destination'))                                                                               # noqa: E501, E221
    delay        = models.DecimalField(max_digits=3, decimal_places=0,  default=0, verbose_name=_('Delay'))                                                     # noqa: E501, E221
    timeout      = models.DecimalField(max_digits=3, decimal_places=0,  default=30, verbose_name=_('Timeout'))                                                  # noqa: E501, E221
    prompt       = models.CharField(max_length=8, blank=True, null=True, choices=ConfirmChoice.choices, default=ConfirmChoice.CNONE, verbose_name=_('Prompt'))  # noqa: E501, E221
    sequence     = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True, default=10, verbose_name=_('Order'))                             # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                    # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                        # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                  # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                # noqa: E501, E221

    class Meta:
        db_table = 'pbx_follow_me_destinations'

    def __str__(self):
        return str(self.id)


class Gateway(models.Model):
    id                   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Gateway'))                                                                                    # noqa: E501, E221
    domain_id            = models.ForeignKey('tenants.Domain', db_column='domain_uuid', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))                                              # noqa: E501, E221
    gateway              = models.CharField(max_length=32, verbose_name=_('Gateway'))                                                                                                                           # noqa: E501, E221
    username             = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Username'))                                                                                                   # noqa: E501, E221
    password             = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Password'))                                                                                                   # noqa: E501, E221
    distinct_to          = models.CharField(max_length=8, choices=EnabledTrueFalseNoneChoice.choices, default=EnabledTrueFalseNoneChoice.CNONE, blank=True, null=True, verbose_name=_('Distinct To'))           # noqa: E501, E221
    auth_username        = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Auth Username'))                                                                                              # noqa: E501, E221
    realm                = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Realm'))                                                                                                     # noqa: E501, E221
    from_user            = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('From User'))                                                                                                  # noqa: E501, E221
    from_domain          = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('From Domain'))                                                                                               # noqa: E501, E221
    proxy                = models.CharField(max_length=128, verbose_name=_('Proxy'))                                                                                                                            # noqa: E501, E221
    register_proxy       = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Register Proxy'))                                                                                            # noqa: E501, E221
    outbound_proxy       = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Outbound Proxy'))                                                                                            # noqa: E501, E221
    expire_seconds       = models.DecimalField(max_digits=5, decimal_places=0, default=1800, verbose_name=_('Expire Seconds'))                                                                                  # noqa: E501, E221
    register             = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Register'))                                            # noqa: E501, E221
    register_transport   = models.CharField(max_length=8, choices=RegisterTransportChoice.choices, default=RegisterTransportChoice.CNONE, blank=True, null=True, verbose_name=_('Register Transport'))          # noqa: E501, E221
    retry_seconds        = models.DecimalField(max_digits=4, decimal_places=0, default=30, verbose_name=_('Retry Seconds'))                                                                                     # noqa: E501, E221
    extension            = models.CharField(max_length=32, blank=True, null=True, default='auto_to_user', verbose_name=_('Extension'))                                                                          # noqa: E501, E221
    ping                 = models.CharField(max_length=8, blank=True, null=True, verbose_name=_('Ping'))                                                                                                        # noqa: E501, E221
    caller_id_in_from    = models.CharField(max_length=8, choices=EnabledTrueFalseNoneChoice.choices, default=EnabledTrueFalseNoneChoice.CNONE, blank=True, null=True, verbose_name=_('Caller ID In From'))     # noqa: E501, E221
    supress_cng          = models.CharField(max_length=8, choices=EnabledTrueFalseNoneChoice.choices, default=EnabledTrueFalseNoneChoice.CNONE, blank=True, null=True, verbose_name=_('Supress CNG'))           # noqa: E501, E221
    sip_cid_type         = models.CharField(max_length=8, blank=True, null=True, verbose_name=_('SIP CID Type'))                                                                                                # noqa: E501, E221
    codec_prefs          = models.CharField(max_length=34, blank=True, null=True, verbose_name=_('Codec Preferences'))                                                                                          # noqa: E501, E221
    channels             = models.DecimalField(max_digits=4, decimal_places=0, default=0, verbose_name=_('Channels'))                                                                                           # noqa: E501, E221
    extension_in_contact = models.CharField(max_length=8, choices=EnabledTrueFalseNoneChoice.choices, default=EnabledTrueFalseNoneChoice.CNONE, blank=True, null=True, verbose_name=_('Extension In Contact'))  # noqa: E501, E221
    context              = models.CharField(max_length=128, default='public', verbose_name=_('Context'))                                                                                                        # noqa: E501, E221
    profile              = models.CharField(max_length=64, default='external', verbose_name=_('Profile'))  # Needs a dynamic select                                                                             # noqa: E501, E221
    hostname             = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Hostname'))                                                                                                  # noqa: E501, E221
    enabled              = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))                                              # noqa: E501, E221
    description          = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Description'))                                                                                                # noqa: E501, E221
    created              = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                                            # noqa: E501, E221
    updated              = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                                                # noqa: E501, E221
    synchronised         = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                                          # noqa: E501, E221
    updated_by           = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                                                        # noqa: E501, E221

    class Meta:
        db_table = 'pbx_gateways'

    def __str__(self):
        return f'{self.gateway}->{self.id}'


class Bridge(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Bridge'))                                         # noqa: E501, E221
    domain_id    = models.ForeignKey('tenants.Domain', db_column='domain_uuid', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))  # noqa: E501, E221
    name         = models.CharField(max_length=32, verbose_name=_('Name'))                                                                                  # noqa: E501, E221
    destination  = models.CharField(max_length=256, verbose_name=_('Destination'))                                                                          # noqa: E501, E221
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))  # noqa: E501, E221
    description  = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Description'))                                                    # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                    # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                              # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                            # noqa: E501, E221

    class Meta:
        db_table = 'pbx_bridges'

    def __str__(self):
        return str(self.name)
