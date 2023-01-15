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
from django.contrib.auth.models import User
from pbx.commonchoices import (
    EnabledTrueFalseChoice, SettingTypeChoice, StatusDefaultChoice
)

# for select domain link
from django.urls import reverse
from django.utils.html import mark_safe


#
# Becomes effectivly the pbx users table
#
class Profile(models.Model):

    class Meta:
        db_table = "pbx_users"

    user_uuid    = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4, editable=False)                                                               # noqa: E501, E221
    domain_id    = models.ForeignKey('Domain', models.SET_NULL, blank=True, null=True, verbose_name=_('Domain'))                                                  # noqa: E501, E221
    username     = models.CharField(max_length=150, db_index=True, unique=True, verbose_name=_('User ID'))                                                        # noqa: E501, E221
    email        = models.CharField(max_length=254, null=True, verbose_name=_('Email'))                                                                           # noqa: E501, E221
    status       = models.CharField(max_length=32, blank=True, choices=StatusDefaultChoice.choices, default=StatusDefaultChoice.CNONE, verbose_name=_('Status'))  # noqa: E501, E221
    api_key      = models.CharField(max_length=254, blank=True, null=True, editable=True, verbose_name=_('API Key'))                                              # noqa: E501, E221
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))        # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                      # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                          # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                    # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                  # noqa: E501, E221
    user         = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('User'))                                                                   # noqa: E501, E221

    def __str__(self):
        return self.username


#
# Domains - each domain represents a tenant
#
class Domain(models.Model):

    class Meta:
        db_table = "pbx_domains"
        permissions = (("can_select_domain", "can_select_domain"),)

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)                                                                   # noqa: E501, E221
    name         = models.CharField(max_length=128, db_index=True, unique=True, verbose_name=_('Name'), help_text="Eg. tenant.djangopbx.com")               # noqa: E501, E221
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))  # noqa: E501, E221
    description  = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Description'))                                                   # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                    # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                              # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                            # noqa: E501, E221

    def select_domain(self):
        return mark_safe('<a class="grp-button" href="%s">%s</a>' % (
                    reverse('selectdomain', args=[self.id]), _('Select Domain')
                    ))

    select_domain.short_description = _('Select Domain')

    def __str__(self):
        return self.name


#
# ProfileSetting overrides both domain and default settings
#
class ProfileSetting(models.Model):

    class Meta:
        db_table = "pbx_user_settings"

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)                                                                      # noqa: E501, E221
    user_id      = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name=_('User'))                                                              # noqa: E501, E221
    category     = models.CharField(max_length=32, db_index=True, verbose_name=_('Category'))                                                                  # noqa: E501, E221
    subcategory  = models.CharField(max_length=32, db_index=True, verbose_name=_('Subcategory'))                                                               # noqa: E501, E221
    value_type   = models.CharField(max_length=32, db_index=True, choices=SettingTypeChoice.choices, default=SettingTypeChoice.CTEXT, verbose_name=_('Type'))  # noqa: E501, E221
    value        = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Value'))                                                            # noqa: E501, E221
    sequence     = models.DecimalField(max_digits=11, decimal_places=0, default=10, verbose_name=_('Order'))                                                   # noqa: E501, E221
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))     # noqa: E501, E221
    description  = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Description'))                                                      # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                   # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                       # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                 # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                               # noqa: E501, E221

    def __str__(self):
        return f"{self.category}->{self.subcategory}: {self.value}"


#
# DomainSetting overrides default settings
#
class DomainSetting(models.Model):

    class Meta:
        db_table = "pbx_domain_settings"

    id        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)                                                                         # noqa: E501, E221
    domain_id    = models.ForeignKey('Domain', on_delete=models.CASCADE, verbose_name=_('Domain'))                                                             # noqa: E501, E221
    app_uuid     = models.UUIDField(blank=True, null=True, editable=False)                                                                                     # noqa: E501, E221
    category     = models.CharField(max_length=32, db_index=True, verbose_name=_('Category'))                                                                  # noqa: E501, E221
    subcategory  = models.CharField(max_length=32, db_index=True, verbose_name=_('Subcategory'))                                                               # noqa: E501, E221
    value_type   = models.CharField(max_length=32, db_index=True, choices=SettingTypeChoice.choices, default=SettingTypeChoice.CTEXT, verbose_name=_('Type'))  # noqa: E501, E221
    value        = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Value'))                                                            # noqa: E501, E221
    sequence     = models.DecimalField(max_digits=11, decimal_places=0, default=10, verbose_name=_('Order'))                                                   # noqa: E501, E221
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))     # noqa: E501, E221
    description  = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Description'))                                                      # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                   # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                       # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                 # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                               # noqa: E501, E221

    def __str__(self):
        return f"{self.category}->{self.subcategory}: {self.value}"


#
# DefaultSetting - default settings
#
class DefaultSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)                                                                                # noqa: E501, E221
    app_uuid = models.UUIDField(blank=True, null=True, editable=False)                                                                                         # noqa: E501, E221
    category     = models.CharField(max_length=32, db_index=True, verbose_name=_('Category'))                                                                  # noqa: E501, E221
    subcategory  = models.CharField(max_length=32, db_index=True, verbose_name=_('Subcategory'))                                                               # noqa: E501, E221
    value_type   = models.CharField(max_length=32, db_index=True, choices=SettingTypeChoice.choices, default=SettingTypeChoice.CTEXT, verbose_name=_('Type'))  # noqa: E501, E221
    value        = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Value'))                                                            # noqa: E501, E221
    sequence     = models.DecimalField(max_digits=11, decimal_places=0, default=10, verbose_name=_('Order'))                                                   # noqa: E501, E221
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))     # noqa: E501, E221
    description  = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Description'))                                                      # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                   # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                       # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                 # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                               # noqa: E501, E221

    class Meta:
        db_table = 'pbx_default_settings'

    def __str__(self):
        return f"{self.category}->{self.subcategory}: {self.value}"
