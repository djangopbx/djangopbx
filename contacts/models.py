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
from pbx.commonchoices import EnabledTrueFalseChoice


class TelTypeChoice(models.TextChoices):
    CVOICE = 'VOICE',  _('INTL')         # noqa: E221
    CHOME  = 'HOME',   _('Home')         # noqa: E221
    CMSG   = 'MSG',    _('Message')      # noqa: E221
    CWORK  = 'WORK',   _('Work')         # noqa: E221
    CPREF  = 'pref',   _('Preferred')    # noqa: E221
    CFAX   = 'fax',    _('Fax')          # noqa: E221
    CCELL  = 'cell',   _('Mobile phone') # noqa: E221
    CVIDEO = 'video',  _('Video')        # noqa: E221
    CPAGER = 'pager',  _('Pager')        # noqa: E221
    CBBS   = 'bbs',    _('BBS')          # noqa: E221
    CMODEM = 'modem',  _('Modem')        # noqa: E221
    CCAR   = 'car',    _('Car phone')    # noqa: E221
    CISDN  = 'isdn',   _('ISDN')         # noqa: E221
    CPCS   = 'pcs',    _('PCS')          # noqa: E221


class EmailTypeChoice(models.TextChoices):
    CINTERNET = 'INTERNET',  _('Internet')  # noqa: E221
    CX400     = 'x400',      _('x400')      # noqa: E221
    CPREF     = 'pref',      _('Preferred') # noqa: E221


class AddressTypeChoice(models.TextChoices):
    CINTL   = 'INTL',    _('INTL')         # noqa: E221
    CPOSTAL = 'POSTAL',  _('Postal')       # noqa: E221
    CPARCEL = 'PARCEL',  _('Parcel')       # noqa: E221
    CWORK   = 'WORK',    _('Work')         # noqa: E221
    CDOM    = 'dom',     _('Dom')          # noqa: E221
    CHOME   = 'home',    _('Home')         # noqa: E221
    CPREF   = 'pref',    _('Preferred')    # noqa: E221


class Contact(models.Model):
    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Contact ID'))                                                          # noqa: E501, E221
    domain_id        = models.ForeignKey('tenants.Domain', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))                                                # noqa: E501, E221
    user_id          = models.ForeignKey('tenants.Profile', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('User'))                                                 # noqa: E501, E221
    fn               = models.CharField(max_length=254, blank=False, null=False, verbose_name=_('Display Name'), help_text=_('The formatted name string associated with the vCard')) # noqa: E501, E221
    family_name      = models.CharField(max_length=64, verbose_name=_('Last Name'))                                                                                                  # noqa: E501, E221
    given_name       = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('First Name'))                                                                          # noqa: E501, E221
    additional_name  = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Middle Name'))                                                                         # noqa: E501, E221
    honorific_prefix = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Prefix'))                                                                              # noqa: E501, E221
    honorific_suffix = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Suffix'))                                                                              # noqa: E501, E221
    nickname         = models.CharField(max_length=64, blank = True, null=True, verbose_name=_('Nickname'))                                                                          # noqa: E501, E221
    timezone         = models.CharField(max_length=128, blank = True, null=True, verbose_name=_('Timezone'))                                                                         # noqa: E501, E221
    notes            = models.TextField(blank=True, null=True, verbose_name=_('Notes'))                                                                                              # noqa: E501, E221
    enabled          = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))           # noqa: E501, E221
    created          = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                     # noqa: E501, E221
    updated          = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                         # noqa: E501, E221
    synchronised     = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                   # noqa: E501, E221
    updated_by       = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                                 # noqa: E501, E221

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        db_table = 'pbx_contacts'

    def __str__(self):
        return self.fn


class ContactTel(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Telephone ID'))                                                                       # noqa: E501, E221
    contact_id   = models.ForeignKey('Contact', on_delete=models.CASCADE, verbose_name=_('Contact'))                                                                                            # noqa: E501, E221
    tel_type     = models.CharField(max_length=32, choices=TelTypeChoice.choices, default=TelTypeChoice.CWORK, verbose_name=_('Type of Phone Number'), help_text=_('for example WORK or HOME')) # noqa: E501, E221
    number       = models.CharField(max_length=128, verbose_name=_('Number'))                                                                                                                   # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                                    # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                                        # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                                  # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                                                # noqa: E501, E221

    class Meta:
        verbose_name = 'Telephone'
        verbose_name_plural = 'Telephones'
        db_table = 'pbx_contacts_tel'

    def __str__(self):
        return self.number


class ContactEmail(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Email ID'))                                   # noqa: E501, E221
    contact_id   = models.ForeignKey('Contact', on_delete=models.CASCADE, verbose_name=_('Contact'))                                                    # noqa: E501, E221
    email_type   = models.CharField(max_length=16, choices=EmailTypeChoice.choices, default=EmailTypeChoice.CINTERNET, verbose_name=_('Type of Email')) # noqa: E501, E221
    email        = models.CharField(max_length=1024, verbose_name=_('Email'))                                                                           # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                            # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                          # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                        # noqa: E501, E221

    class Meta:
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'
        db_table = 'pbx_contacts_email'

    def __str__(self):
        return self.email


class ContactGeo(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Geo Tag ID'))  # noqa: E501, E221
    contact_id   = models.ForeignKey('Contact', on_delete=models.CASCADE, verbose_name=_('Contact'))                     # noqa: E501, E221
    geo_uri      = models.CharField(max_length=1024, verbose_name=_('Geographic URI'))                                   # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))             # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                 # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                           # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                         # noqa: E501, E221

    class Meta:
        verbose_name = 'Geoghraphic URI'
        verbose_name_plural = 'Geoghraphic URI\'s'
        db_table = 'pbx_contacts_geo'

    def __str__(self):
        return self.geo_uri


class ContactUrl(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Geo Tag ID'))  # noqa: E501, E221
    contact_id   = models.ForeignKey('Contact', on_delete=models.CASCADE, verbose_name=_('Contact'))                     # noqa: E501, E221
    url_uri      = models.CharField(max_length=1024, verbose_name=_('URL (Website)'))                                    # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))             # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                 # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                           # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                         # noqa: E501, E221

    class Meta:
        verbose_name = 'URL'
        verbose_name_plural = 'URL\'s'
        db_table = 'pbx_contacts_url'

    def __str__(self):
        return self.url_uri


class ContactOrg(models.Model):
    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Organisation')) # noqa: E501, E221
    contact_id        = models.ForeignKey('Contact', on_delete=models.CASCADE, verbose_name=_('Contact'))                      # noqa: E501, E221
    organisation_name = models.CharField(max_length=128, verbose_name=_('Organisation Name'))                                  # noqa: E501, E221
    organisation_unit = models.CharField(max_length=128, blank=True, verbose_name=_('Organisation Unit'))                      # noqa: E501, E221
    created           = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))              # noqa: E501, E221
    updated           = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                  # noqa: E501, E221
    synchronised      = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                            # noqa: E501, E221
    updated_by        = models.CharField(max_length=64, verbose_name=_('Updated by'))                                          # noqa: E501, E221

    class Meta:
        verbose_name = 'Organisation'
        verbose_name_plural = 'Organisations'
        db_table = 'pbx_contacts_org'

    def __str__(self):
        return self.organisation_name


class ContactAddress(models.Model):
    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Email ID'))                          # noqa: E501, E221
    contact_id       = models.ForeignKey('Contact', on_delete=models.CASCADE, verbose_name=_('Contact'))                                           # noqa: E501, E221
    post_office_box  = models.CharField(max_length=64, blank=True, verbose_name=_('Post Office Box'))                                              # noqa: E501, E221
    extended_address = models.CharField(max_length=128, blank=True, verbose_name=_('Extended Address'))                                            # noqa: E501, E221
    street_address   = models.CharField(max_length=128, verbose_name=_('Street Address'))                                                          # noqa: E501, E221
    locality         = models.CharField(max_length=128, verbose_name=_('Locality'))                                                                # noqa: E501, E221
    region           = models.CharField(max_length=128, verbose_name=_('Region'))                                                                  # noqa: E501, E221
    postal_code      = models.CharField(max_length=16, verbose_name=_('Postal Code'))                                                              # noqa: E501, E221
    country_name     = models.CharField(max_length=128, verbose_name=_('Country Name'))                                                            # noqa: E501, E221
    addr_type        = models.CharField(max_length=16, choices=AddressTypeChoice.choices, default=AddressTypeChoice.CWORK, verbose_name=_('Type')) # noqa: E501, E221
    created          = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                   # noqa: E501, E221
    updated          = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                       # noqa: E501, E221
    synchronised     = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                 # noqa: E501, E221
    updated_by       = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                               # noqa: E501, E221

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        db_table = 'pbx_contacts_address'

    def __str__(self):
        return self.postal_code


class ContactDate(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Significant Date'))  # noqa: E501, E221
    contact_id   = models.ForeignKey('Contact', on_delete=models.CASCADE, verbose_name=_('Contact'))                           # noqa: E501, E221
    sig_date     = models.DateField(blank=True, null=True, verbose_name=_('Significant Date'))                                 # noqa: E501, E221
    label        = models.CharField(max_length=64, verbose_name=_('Label'))                                                    # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                   # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                       # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                 # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                               # noqa: E501, E221

    class Meta:
        verbose_name = 'Significant Date'
        verbose_name_plural = 'Significant Dates'
        db_table = 'pbx_contacts_dates'

    def __str__(self):
        return self.label


class ContactCategory(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Significant Date'))  # noqa: E501, E221
    contact_id   = models.ForeignKey('Contact', on_delete=models.CASCADE, verbose_name=_('Contact'))                           # noqa: E501, E221
    category     = models.CharField(max_length=64, verbose_name=_('Label'))                                                    # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                   # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                       # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                 # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                               # noqa: E501, E221

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        db_table = 'pbx_contacts_category'

    def __str__(self):
        return self.category


class ContactGroup(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Group'))                 # noqa: E501, E221
    contact_id   = models.ForeignKey('contact', on_delete=models.CASCADE, verbose_name=_('Contact'))                               # noqa: E501, E221
    name         = models.CharField(max_length=64, blank=True, null=True)                                                          # noqa: E501, E221
    group_id     = models.ForeignKey('auth.Group', db_column='group_id', on_delete=models.CASCADE, verbose_name=_('Group'))        # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                       # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                           # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                     # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                   # noqa: E501, E221

    class Meta:
        db_table = 'pbx_contacts_groups'

    def save(self, *args, **kwargs):
        self.name = self.group_id.name
        super(ContactGroup, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.group_id)
