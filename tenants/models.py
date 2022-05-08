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


class Profile(models.Model):
    class Meta:
        db_table = "pbx_users"

    user_uuid      = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4, editable=False)
    domain_id    = models.ForeignKey('Domain', models.SET_NULL, blank=True, null=True, verbose_name=_('Domain'))
    username     = models.CharField(max_length=150, db_index=True, unique=True, verbose_name=_('User ID'))
    email        = models.CharField(max_length=254, null=True, verbose_name=_('Email'))
    status       = models.CharField(max_length=32, blank=True, choices=StatusDefaultChoice.choices, default=StatusDefaultChoice.CNONE, verbose_name=_('Status'))
    api_key      = models.CharField(max_length=254, blank=True, null=True, editable=True, verbose_name=_('API Key'))
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))
    user         = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('User'))

    def __str__(self):
        return self.username


class Domain(models.Model):
    class Meta:
        db_table = "pbx_domains"
        permissions = (("can_select_domain", "can_select_domain"),)

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name         = models.CharField(max_length=128, db_index=True, unique=True, verbose_name=_('Name'), help_text="Eg. tenant.djangopbx.com")
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))
    description  = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Description'))
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))

    def select_domain(self):
        return mark_safe('<a class="grp-button" href="%s">%s</a>' % (reverse('selectdomain', args=[self.id]), _('Select Domain')))

    select_domain.short_description = _('Select Domain')

    def __str__(self):
        return self.name


class ProfileSetting(models.Model):
    class Meta:
        db_table = "pbx_user_settings"

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id      = models.ForeignKey('Profile', on_delete=models.CASCADE, verbose_name=_('User'))
    category     = models.CharField(max_length=32, verbose_name=_('Category'))
    subcategory  = models.CharField(max_length=32, verbose_name=_('Subcategory'))
    value_type   = models.CharField(max_length=32, choices=SettingTypeChoice.choices, default=SettingTypeChoice.CTEXT, verbose_name=_('Type'))
    value        = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Value'))
    sequence     = models.DecimalField(max_digits=11, decimal_places=0, default=10, verbose_name=_('Order'))
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))
    description  = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Description'))
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))

    def __str__(self):
        return f"{self.category}->{self.subcategory}: {self.value}"


class DomainSetting(models.Model):
    class Meta:
        db_table = "pbx_domain_settings"

    id        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    domain_id    = models.ForeignKey('Domain', on_delete=models.CASCADE, verbose_name=_('Domain'))
    app_uuid     = models.UUIDField(blank=True, null=True, editable=False)
    category     = models.CharField(max_length=32, verbose_name=_('Category'))
    subcategory  = models.CharField(max_length=32, verbose_name=_('Subcategory'))
    value_type   = models.CharField(max_length=32, choices=SettingTypeChoice.choices, default=SettingTypeChoice.CTEXT, verbose_name=_('Type'))
    value        = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Value'))
    sequence     = models.DecimalField(max_digits=11, decimal_places=0, default=10, verbose_name=_('Order'))
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))
    description  = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Description'))
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))

    def __str__(self):
        return f"{self.category}->{self.subcategory}: {self.value}"


class DefaultSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    app_uuid = models.UUIDField(blank=True, null=True, editable=False)
    category     = models.CharField(max_length=32, verbose_name=_('Category'))
    subcategory  = models.CharField(max_length=32, verbose_name=_('Subcategory'))
    value_type   = models.CharField(max_length=32, choices=SettingTypeChoice.choices, default=SettingTypeChoice.CTEXT, verbose_name=_('Type'))
    value        = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Value'))
    sequence     = models.DecimalField(max_digits=11, decimal_places=0, default=10, verbose_name=_('Order'))
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))
    description  = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Description'))
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        db_table = 'pbx_default_settings'

    def __str__(self):
        return f"{self.category}->{self.subcategory}: {self.value}"

