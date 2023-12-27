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
    EnabledTrueFalseChoice, EnabledTrueFalseNoneChoice
)


#
# Choice classes
#
class DeviceKeyCategoryChoice(models.TextChoices):
    CNONE        = '',    _('Not Set')                # noqa: E221
    CLINE        = 'line',  _('Line')                 # noqa: E221
    CMEMORY      = 'memory', _('Memory')              # noqa: E221
    CPROGRAMABLE = 'programmable', _('Programmable')  # noqa: E221
    CEXPANSION1  = 'expansion-1', _('Expansion 1')    # noqa: E221
    CEXPANSION2  = 'expansion-2', _('Expansion 2')    # noqa: E221
    CEXPANSION3  = 'expansion-3', _('Expansion 3')    # noqa: E221
    CEXPANSION4  = 'expansion-4', _('Expansion 4')    # noqa: E221
    CEXPANSION5  = 'expansion-5', _('Expansion 5')    # noqa: E221
    CEXPANSION6  = 'expansion-6', _('Expansion 6')    # noqa: E221


class LineTransportChoice(models.TextChoices):
    CUDP    = 'udp',     _('UDP')     # noqa: E221
    CTCP    = 'tcp',     _('TCP')     # noqa: E221
    CTLS    = 'tls',     _('TLS')     # noqa: E221
    CDNSSRV = 'dns srv', _('DNS SRV') # noqa: E221


class DeviceVendors(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Vendor'))                                                            # noqa: E501, E221
    name         = models.CharField(max_length=64, verbose_name=_('Name'))                                                                                                     # noqa: E501, E221
    enabled      = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))         # noqa: E501, E221
    description  = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))                                                                      # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                   # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                       # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                 # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                               # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Device Vendors'
        db_table = 'pbx_device_vendors'

    def __str__(self):
        return self.name


class DeviceVendorFunctions(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Function'))                                                          # noqa: E501, E221
    vendor_id    = models.ForeignKey('DeviceVendors', db_column='vendor_id', on_delete=models.CASCADE, verbose_name=_('Vendor'))                                               # noqa: E501, E221
    name         = models.CharField(max_length=64, verbose_name=_('Name'))                                                                                                     # noqa: E501, E221
    value        = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Value'))                                                                            # noqa: E501, E221
    enabled      = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))         # noqa: E501, E221
    description  = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))                                                                      # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                   # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                       # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                 # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                               # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Device Vendor Functions'
        db_table = 'pbx_device_vendor_functions'

    def __str__(self):
        return self.name


class DeviceVendorFunctionChoice():
    def choices(self, vendor=None):
        # This try/except is a workaround to prevent a relation not found error on initial migrate
        try:
            if vendor:
                return [(c.value, c.name) for c in DeviceVendorFunctions.objects.filter(enabled='true', vendor_id_id=vendor)]
            return [(c.value, '%s -> %s' % (c.vendor_id.name, c.name)) for c in DeviceVendorFunctions.objects.filter(enabled='true')]
        except:
            return [('None', 'None')]


class DeviceVendorFunctionGroups(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Function'))                                                          # noqa: E501, E221
    function_id  = models.ForeignKey('DeviceVendorFunctions', db_column='function_id', on_delete=models.CASCADE, verbose_name=_('Function'))                                   # noqa: E501, E221
    group_id     = models.ForeignKey('auth.Group', db_column='group_id', on_delete=models.CASCADE, verbose_name=_('Group'))                                                    # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                   # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                       # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                 # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                               # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Device Vendor Function Groups'
        db_table = 'pbx_device_vendor_function_groups'

    def __str__(self):
        return str(self.id)


class DeviceProfiles(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Profile'))                                                           # noqa: E501, E221
    domain_id    = models.ForeignKey('tenants.Domain', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))                                              # noqa: E501, E221
    vendor       = models.ForeignKey('DeviceVendors', on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Vendor'))                                              # noqa: E501, E221
    name         = models.CharField(max_length=64, verbose_name=_('Name'))                                                                                                     # noqa: E501, E221
    enabled      = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))         # noqa: E501, E221
    description  = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))                                                                      # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                   # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                       # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                 # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                               # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Device Profiles'
        db_table = 'pbx_device_profiles'

    def __str__(self):
        return f"{self.domain_id}->{self.name}"


class DeviceProfileSettings(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Setting'))                                                           # noqa: E501, E221
    profile_id   = models.ForeignKey('DeviceProfiles', db_column='profile_id', on_delete=models.CASCADE, verbose_name=_('Profile'))                                            # noqa: E501, E221
    name         = models.CharField(max_length=64, verbose_name=_('Name'))                                                                                                     # noqa: E501, E221
    value        = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Value'))                                                                            # noqa: E501, E221
    enabled      = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))         # noqa: E501, E221
    description  = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))                                                                      # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                   # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                       # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                 # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                               # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Device Profile Settings'
        db_table = 'pbx_device_profile_settings'

    def __str__(self):
        return self.name


class DeviceProfileKeys(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Key'))                                                                  # noqa: E501, E221
    profile_id   = models.ForeignKey('DeviceProfiles', db_column='profile_id', on_delete=models.CASCADE, verbose_name=_('Profile'))                                               # noqa: E501, E221
    category     = models.CharField(max_length=16, blank=True, choices=DeviceKeyCategoryChoice.choices, default=DeviceKeyCategoryChoice.CLINE, verbose_name=_('Category'))        # noqa: E501, E221
    key_id       = models.DecimalField(max_digits=11, decimal_places=0, default=1, verbose_name=_('Key'))                                                                         # noqa: E501, E221
    #vendor_id    = models.ForeignKey('DeviceVendors', db_column='vendor_id', on_delete=models.CASCADE, verbose_name=_('Vendor'))                                                 # noqa: E501, E221
    key_type     = models.CharField(max_length=64, choices=DeviceVendorFunctionChoice().choices(), verbose_name=_('Key type'))                                                    # noqa: E501, E221
    line         = models.DecimalField(max_digits=3, decimal_places=0, default=1, verbose_name=_('Line'))                                                                         # noqa: E501, E221
    value        = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Value'))                                                                               # noqa: E501, E221
    extension    = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Extension'))                                                                            # noqa: E501, E221
    protected    = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseNoneChoice.choices, default=EnabledTrueFalseNoneChoice.CNONE, verbose_name=_('Protected'))  # noqa: E501, E221
    label        = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Label'))                                                                                # noqa: E501, E221
    icon         = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Icon'))                                                                                 # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                      # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                          # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                    # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                                  # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Device Profile Keys'
        db_table = 'pbx_device_profile_keys'

    def __str__(self):
        return f"{self.category}->{self.key_id}: {self.value}"


class Devices(models.Model):
    id                 = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Device'))                                                      # noqa: E501, E221
    domain_id          = models.ForeignKey('tenants.Domain', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))                                        # noqa: E501, E221
    profile_id         = models.ForeignKey('DeviceProfiles', on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Profile'))                                      # noqa: E501, E221
    mac_address        = models.CharField(max_length=24, verbose_name=_('MAC Address'))                                                                                        # noqa: E501, E221
    label              = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Label'))                                                                       # noqa: E501, E221
    vendor             = models.ForeignKey('DeviceVendors', on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Vendor'))                                        # noqa: E501, E221
    model              = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Model'))                                                                       # noqa: E501, E221
    firmware_version   = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Firmware Version'))                                                            # noqa: E501, E221
    template           = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Template'))                                                                   # noqa: E501, E221
    user_id            = models.ForeignKey('tenants.Profile', on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('User'))                                        # noqa: E501, E221
    username           = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Username'))                                                                    # noqa: E501, E221
    password           = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Password'))                                                                    # noqa: E501, E221
    provisioned_date   = models.DateTimeField(blank=True, null=True, verbose_name=_('Provisioned Date'))                                                                       # noqa: E501, E221
    provisioned_method = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Prov. Method'))                                                                # noqa: E501, E221
    enabled            = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))   # noqa: E501, E221
    description        = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))                                                                # noqa: E501, E221
    provisioned_ip     = models.GenericIPAddressField(blank=True, null=True, protocol='both', unpack_ipv4=False, verbose_name=_('Provisioned Address'))                        # noqa: E501, E221
    created            = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                             # noqa: E501, E221
    updated            = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                 # noqa: E501, E221
    synchronised       = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                           # noqa: E501, E221
    updated_by         = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                         # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Devices'
        db_table = 'pbx_devices'

    def __str__(self):
        return self.mac_address


class DeviceLines(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Key'))                                                               # noqa: E501, E221
    device_id    = models.ForeignKey('Devices', db_column='device_id', on_delete=models.CASCADE, verbose_name=_('Device'))                                                     # noqa: E501, E221
    line_number  = models.DecimalField(max_digits=3, decimal_places=0, default=1, verbose_name=_('Line'))                                                                      # noqa: E501, E221
    server_address = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Server Address'))                                                                 # noqa: E501, E221
    server_address_primary = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Primary Address'))                                                        # noqa: E501, E221
    server_address_secondary = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Secondary Address'))                                                    # noqa: E501, E221
    outbound_proxy_primary = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Primary Proxy'))                                                          # noqa: E501, E221
    outbound_proxy_secondary = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Secondary Proxy'))                                                      # noqa: E501, E221
    display_name = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Display Name'))                                                                     # noqa: E501, E221
    user_id = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('User ID'))                                                                               # noqa: E501, E221
    auth_id = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Auth ID'))                                                                               # noqa: E501, E221
    password = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Password'))                                                                             # noqa: E501, E221
    sip_port = models.DecimalField(max_digits=5, decimal_places=0, default=5060, blank=True, null=True, verbose_name=_('SIP Port'))                                            # noqa: E501, E221
    sip_transport = models.CharField(max_length=254, blank=True, null=True, choices=LineTransportChoice.choices, default=LineTransportChoice.CUDP, verbose_name=_('Transport'))# noqa: E501, E221
    register_expires = models.DecimalField(max_digits=5, decimal_places=0, default=1800, blank=True, null=True, verbose_name=_('Expires'))                                     # noqa: E501, E221
    shared_line = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Shared Line'))                                                                       # noqa: E501, E221
    enabled      = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))         # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                   # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                       # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                 # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                               # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Device Lines'
        db_table = 'pbx_device_lines'

    def __str__(self):
        return f"{self.line_number}: {self.display_name}"


class DeviceKeys(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Key'))                                                                  # noqa: E501, E221
    device_id    = models.ForeignKey('Devices', db_column='device_id', on_delete=models.CASCADE, verbose_name=_('Device'))                                                        # noqa: E501, E221
    category     = models.CharField(max_length=16, blank=True, choices=DeviceKeyCategoryChoice.choices, default=DeviceKeyCategoryChoice.CLINE, verbose_name=_('Category'))        # noqa: E501, E221
    key_id       = models.DecimalField(max_digits=11, decimal_places=0, default=1, verbose_name=_('Key'))                                                                         # noqa: E501, E221
    #vendor_id    = models.ForeignKey('DeviceVendors', db_column='vendor_id', on_delete=models.CASCADE, verbose_name=_('Vendor'))                                                 # noqa: E501, E221
    key_type     = models.CharField(max_length=64, choices=DeviceVendorFunctionChoice().choices(), verbose_name=_('Key type'))                                                    # noqa: E501, E221
    line         = models.DecimalField(max_digits=3, decimal_places=0, default=1, verbose_name=_('Line'))                                                                         # noqa: E501, E221
    value        = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Value'))                                                                               # noqa: E501, E221
    extension    = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Extension'))                                                                            # noqa: E501, E221
    protected    = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseNoneChoice.choices, default=EnabledTrueFalseNoneChoice.CNONE, verbose_name=_('Protected'))  # noqa: E501, E221
    label        = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Label'))                                                                                # noqa: E501, E221
    icon         = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Icon'))                                                                                 # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                      # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                          # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                    # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                                  # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Device Keys'
        db_table = 'pbx_device_keys'

    def __str__(self):
        return f"{self.category}->{self.key_id}: {self.value}"


class DeviceSettings(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Setting'))                                                           # noqa: E501, E221
    device_id    = models.ForeignKey('Devices', db_column='device_id', on_delete=models.CASCADE, verbose_name=_('Device'))                                                     # noqa: E501, E221
    name         = models.CharField(max_length=64, verbose_name=_('Name'))                                                                                                     # noqa: E501, E221
    value        = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Value'))                                                                            # noqa: E501, E221
    enabled      = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))         # noqa: E501, E221
    description  = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))                                                                      # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                   # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                       # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                 # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                               # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Device Settings'
        db_table = 'pbx_device_settings'

    def __str__(self):
        return self.name
