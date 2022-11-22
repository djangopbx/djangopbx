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
from pbx.commonchoices import(
    EnabledTrueFalseChoice, EnabledTrueFalseNoneChoice, PrimaryTrueFalseChoice, EnabledDisabledChoice, ConfirmChoice,
)


class MissedCallAppChoice(models.TextChoices):
    CNONE     = ''         , _('Not Set')
    CEMAIL    = 'email'    , _('Email')


class RecordChoice(models.TextChoices):
    CDISABLED = ''         , _('Disabled')
    CALL      = 'all'      , _('All')
    CLOCAL    = 'local'    , _('Local')
    CINBOUND  = 'inbound'  , _('Inbound')
    COUTBOUND = 'outbound' , _('Outbound')


class SipForceContactChoice(models.TextChoices):
    CNONE    = ''         , _('')
    CIPPORT  = 'NDLB-connectile-dysfunction'     , _('Rewrite Contact IP and Port')
    CIPPORT2 = 'NDLB-connectile-dysfunction-2.0' , _('Rewrite Contact IP and Port 2.0')
    CTLSPORT = 'NDLB-tls-connectile-dysfunction' , _('Rewrite TLS Contact Port')


class SipBypassMediaChoice(models.TextChoices):
    CNONE    = ''         , _('')
    CIPPORT  = 'bypass-media'              , _('Bypass Media')
    CIPPORT2 = 'bypass-media-after-bridge' , _('Bypass Media After Bridge')
    CTLSPORT = 'proxy-media'               , _('Proxy Media')


class RegisterTransportChoice(models.TextChoices):
    CNONE = ''    , ''
    CUDP  = 'udp' , 'udp'
    CTCP  = 'tcp' , 'tcp'
    CTLS  = 'tls' , 'tls'


class Extension(models.Model):

    id                                      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Extension'))
    domain_id                               = models.ForeignKey('tenants.Domain', db_column='domain_uuid', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))
    extension                               = models.CharField(max_length=32, db_index=True, verbose_name=_('Extension'))
    number_alias                            = models.CharField(max_length=16, db_index=True, blank=True, null=True, verbose_name=_('Number Alias'))
    password                                = models.CharField(max_length=32, verbose_name=_('Password'))
    accountcode                             = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Account Code'))
    effective_caller_id_name                = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Effective Caller ID Name'))
    effective_caller_id_number              = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Effective Caller ID Number'))
    outbound_caller_id_name                 = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Outbound Caller ID Name'))
    outbound_caller_id_number               = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Outbound Caller ID Number'))
    emergency_caller_id_name                = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Emergency Caller ID Name'))
    emergency_caller_id_number              = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Emergency Caller ID Number'))
    directory_first_name                    = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Directory First Name'))
    directory_last_name                     = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Directory Family Name'))
    directory_visible                       = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Directory Visible'))
    directory_exten_visible                 = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Directory Ext. Visible'))
    limit_max                               = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True, default=5, verbose_name=_('Limit Max'))
    limit_destination                       = models.CharField(max_length=32, blank=True, null=True, default="error/user_busy", verbose_name=_('Limit Destination'))
    missed_call_app                         = models.CharField(max_length=32, blank=True, null=True, choices=MissedCallAppChoice.choices, default=MissedCallAppChoice.CNONE, verbose_name=_('Missed Call'))
    missed_call_data                        = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Missed Call Data'))
    user_context                            = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Context'))
    toll_allow                              = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Toll Allow'))
    call_timeout                            = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True, default=300, verbose_name=_('Call Timeout'))
    call_group                              = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Call Group'))
    call_screen_enabled                     = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Call Screen'))
    user_record                             = models.CharField(max_length=8, choices=RecordChoice.choices, default=RecordChoice.CDISABLED, blank=True, null=True, verbose_name=_('Record'))
    hold_music                              = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Hold Music'))
    auth_acl                                = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Auth ACL'))
    cidr                                    = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('CIDR'))
    sip_force_contact                       = models.CharField(max_length=64, choices=SipForceContactChoice.choices, default=SipForceContactChoice.CNONE, blank=True, null=True, verbose_name=_('SIP Force Contact'))
    nibble_account                          = models.DecimalField(max_digits=1, decimal_places=0, blank=True, null=True, verbose_name=_('Nibble Account'))
    sip_force_expires                       = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True, verbose_name=_('SIP Force Expires'))
    mwi_account                             = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('MWI Account'))
    sip_bypass_media                        = models.CharField(max_length=32, choices=SipForceContactChoice.choices, default=SipForceContactChoice.CNONE, blank=True, null=True, verbose_name=_('SIP Bypass Media'))
    unique_id                               = models.DecimalField(max_digits=1, decimal_places=0, blank=True, null=True, verbose_name=_('Unique ID'))
    dial_string                             = models.TextField(blank=True, null=True, verbose_name=_('Dial String'))
    dial_user                               = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Dial User'))
    dial_domain                             = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Dial Domain'))
    do_not_disturb                          = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Do Not Disturb'))
    forward_all_destination                 = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Forward All Destination'))
    forward_all_enabled                     = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Forward All Enabled'))
    forward_busy_destination                = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Forward Busy Destination'))
    forward_busy_enabled                    = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Forward Busy Enabled'))
    forward_no_answer_destination           = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Forward No Answer Destination'))
    forward_no_answer_enabled               = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Forward No Answer Enabled'))
    forward_user_not_registered_destination = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Forward Not Registered Destination'))
    forward_user_not_registered_enabled     = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Forward Not Registered Enabled'))
    follow_me_uuid                          = models.UUIDField(blank=True, null=True, verbose_name=_('Follow Me UUID'))
    forward_caller_id                       = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Caller ID Number'))
    follow_me_enabled                       = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE,  verbose_name=_('Follow Me Enabled'))
    follow_me_destinations                  = models.TextField(blank=True, null=True, verbose_name=_('Follow me Destinations'))
    enabled                                 = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))
    description                             = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Description'))
    absolute_codec_string                   = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Absolute Codec String'))
    force_ping                              = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Force Ping'))
    created                                 = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated                                 = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised                            = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by                              = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        db_table = 'pbx_extensions'

    def __str__(self):
        return self.extension


class ExtensionUser(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Extension User'))
    extension_id   = models.ForeignKey('Extension', db_column='extension_uuid', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Extension'))
    user_uuid      = models.ForeignKey('tenants.Profile', models.SET_NULL, to_field='user_uuid', db_column='user_uuid', blank=True, null=True, verbose_name=_('User'))
    default_user   = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Default'))
    created        = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated        = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised   = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by     = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        db_table = 'pbx_extension_users'

    def __str__(self):
        return str(self.id)


class FollowMeDestination(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Extension User'))
    extension_id = models.ForeignKey('Extension', db_column='extension_uuid', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Extension'))
    destination  = models.CharField(max_length=32, verbose_name=_('Destination'))
    delay        = models.DecimalField(max_digits=3, decimal_places=0,  default=0, verbose_name=_('Delay'))
    timeout      = models.DecimalField(max_digits=3, decimal_places=0,  default=30, verbose_name=_('Timeout'))
    prompt       = models.CharField(max_length=8, blank=True, null=True, choices=ConfirmChoice.choices, default=ConfirmChoice.CNONE, verbose_name=_('Prompt'))
    sequence     = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True, default=10, verbose_name=_('Order'))
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        db_table = 'pbx_follow_me_destinations'

    def __str__(self):
        return str(self.id)


class Gateway(models.Model):
    id                   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Gateway'))
    domain_id            = models.ForeignKey('tenants.Domain', db_column='domain_uuid', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))
    gateway              = models.CharField(max_length=32, verbose_name=_('Gateway'))
    username             = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Username'))
    password             = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Password'))
    distinct_to          = models.CharField(max_length=8, choices=EnabledTrueFalseNoneChoice.choices, default=EnabledTrueFalseNoneChoice.CNONE, blank=True, null=True,verbose_name=_('Distinct To'))
    auth_username        = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Auth Username'))
    realm                = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Realm'))
    from_user            = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('From User'))
    from_domain          = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('From Domain'))
    proxy                = models.CharField(max_length=128, verbose_name=_('Proxy'))
    register_proxy       = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Register Proxy'))
    outbound_proxy       = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Outbound Proxy'))
    expire_seconds       = models.DecimalField(max_digits=5, decimal_places=0, default=1800, verbose_name=_('Expire Seconds'))
    register             = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE,verbose_name=_('Register'))
    register_transport   = models.CharField(max_length=8, choices=RegisterTransportChoice.choices, default=RegisterTransportChoice.CNONE, blank=True, null=True, verbose_name=_('Register Transport'))
    retry_seconds        = models.DecimalField(max_digits=4, decimal_places=0, default=30, verbose_name=_('Retry Seconds'))
    extension            = models.CharField(max_length=32, blank=True, null=True, default='auto_to_user', verbose_name=_('Extension'))
    ping                 = models.CharField(max_length=8, blank=True, null=True, verbose_name=_('Ping'))
    caller_id_in_from    = models.CharField(max_length=8, choices=EnabledTrueFalseNoneChoice.choices, default=EnabledTrueFalseNoneChoice.CNONE, blank=True, null=True, verbose_name=_('Caller ID In From'))
    supress_cng          = models.CharField(max_length=8, choices=EnabledTrueFalseNoneChoice.choices, default=EnabledTrueFalseNoneChoice.CNONE, blank=True, null=True, verbose_name=_('Supress CNG'))
    sip_cid_type         = models.CharField(max_length=8, blank=True, null=True, verbose_name=_('SIP CID Type'))
    codec_prefs          = models.CharField(max_length=34, blank=True, null=True, verbose_name=_('Codec Preferences'))
    channels             = models.DecimalField(max_digits=4, decimal_places=0, default=0, verbose_name=_('Channels'))
    extension_in_contact = models.CharField(max_length=8, choices=EnabledTrueFalseNoneChoice.choices, default=EnabledTrueFalseNoneChoice.CNONE, blank=True, null=True, verbose_name=_('Extension In Contact'))
    context              = models.CharField(max_length=128, default='public', verbose_name=_('Context'))
    profile              = models.CharField(max_length=64, default='external', verbose_name=_('Profile')) #Needs a dynamic select
    hostname             = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Hostname'))
    enabled              = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))
    description          = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Description'))
    created              = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated              = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised         = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by           = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        db_table = 'pbx_gateways'

    def __str__(self):
        return self.gateway

