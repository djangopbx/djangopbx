#
#    DjangoPBX
#
#    MIT License
#
#    Copyright (c) 2016 - 2023 Adrian Fretwell <adrian@djangopbx.com>
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

# VcardParse
# ============
# This class is designed to work with VCARD VERSION:2.1
# It is a very simple parser designed specifically to only deal with data required by
# the Contacts application.  It will ignore some tags and encoding.
#
# Suggestions for improvments welcome
#

import re
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from .models import (
    Contact, ContactTel, ContactEmail, ContactGeo, ContactUrl, ContactOrg, ContactAddress, 
    ContactDate, ContactCategory, ContactGroup,
)
from pbx.commonfunctions import DomainUtils


class VCardParse():
    start = 'BEGIN:'
    end = 'END:'

    # N fields
    family_name = 0
    given_name = 1
    additional_name = 2
    honorific_prefix = 3
    honorific_suffix = 4

    # GEO fields
    latitude = 0
    longitude = 1

    # ORG fields
    organization_name = 0
    organization_unit = 1

    # ADR fields
    post_office_box = 0
    extended_address = 1
    street_address = 2
    locality = 3
    region = 4
    postal_code = 5
    country_name = 6


    # tags : (type, fields:<position>, min, max)
    tags = {
        'VERSION': ('text', None, 0, 1),
        # model: Contact
        'FN': ('text', None, 1, 1),
        'N': ('text', (
                        'family-name',
                        'given-name',
                        'additional-name',
                        'honorific-prefix',
                        'honorific-suffix'), 1, 1),
        'NICKNAME': ('text', None, 0, 1),
        'TZ': ('text', None, 0, 1),
        'NOTE': ('text', None, 0, 1),
        # model: ContactTel
        'TEL': ('text', None, 0, None),
        # model: ContactEmail
        'EMAIL': ('text', None, 0, None),
        # model: ContactGeo
        'GEO': ('float', (
                        'latitude',
                        'longitude'), 0, None),
        # model: Contact
        'URL': ('text', None, 0, None),
        # model: ContactOrg
        'ORG': ('text', (
                        'organization-name',
                        'organization-unit'), 0, None),
        # model: ContactAddress
        'ADR': ('text', (
                        'post-office-box',
                        'extended-address',
                        'street-address',
                        'locality',
                        'region',
                        'postal-code',
                        'country-name'), 0, None),
        # model: ContactDate
        'BDAY': ('datetime', None, 0, None),
        # model: ContactCategory
        'CATEGORIES': ('text', (), 0, None),
        }


    def __init__(self, f, request):
        self.f = f
        self.domain = DomainUtils().domain_from_session(request)
        self.profile = request.user.profile
        self.user_name = request.user.username
        self.make_public = (False if request.POST.get('public', 'false') == 'false' else True)
        self.vcs = []
        self.v_count = 0
        self.card_no = 0
        self.import_errors = []
        self.errors = False
        self.error_text = '<br>'
        self.contacts_added = 0
        self.tel_added = 0
        self.email_added = 0
        self.geo_added = 0
        self.url_added = 0
        self.org_added = 0
        self.adr_added = 0
        self.dte_added = 0
        self.cat_added = 0

    def create_contact(self, vcs):
        self.contact = Contact()
        n = vcs['N'].get('v')
        if not n:
            self.import_errors.append(_('<b>Error:</b> Vcard %s problem with the data in N' % self.card_no))
            return False
        fn = '%s %s %s %s %s' % (
        n[self.honorific_prefix],
        n[self.given_name],
        n[self.additional_name],
        n[self.family_name],
        n[self.honorific_suffix],
        )
        self.contact.fn = re.sub('\s+', ' ', fn.strip())
        if n[self.family_name]:
            self.contact.family_name = n[self.family_name]
        else:
            self.contact.family_name = self.contact.fn
        if n[self.given_name]:
            self.contact.given_name = n[self.given_name]
        if n[self.additional_name]:
            self.contact.given_name = n[self.additional_name]
        if n[self.honorific_prefix]:
            self.contact.honorific_prefix = n[self.honorific_prefix]
        if n[self.honorific_suffix]:
            self.contact.honorific_suffix = n[self.honorific_suffix]
        self.contact.nickname = vcs.get('NICKNAME')
        self.contact.timezone = vcs.get('TZ')
        self.contact.notes = vcs.get('NOTE')
        self.contact.updated_by = self.user_name
        self.contact.domain_id = self.domain
        self.contact.user_id = self.profile
        try:
            self.contact.save()
        except:
            self.import_errors.append(_('<b>Error:</b> Vcard %s database error, unable to save contact' % self.card_no))
            return False
        if self.make_public:
            user_group = Group.objects.get(name='user')
            try:
                ContactGroup.objects.create(contact_id=self.contact, name='user', group_id=user_group)
            except:
                self.import_errors.append(_('<b>Warning:</b> Vcard %s unable to make contact public' % self.card_no))
        self.contacts_added += 1
        return True

    def get_or_create_contact(self, vcs):
        fn = vcs['FN'].get('v')
        if not fn:
            self.import_errors.append(_('<b>Error:</b> Vcard %s problem with the data in FN' % self.card_no))
            return False
        try:
            self.contact = Contact.objects.get(domain_id=self.domain, fn=fn, enabled='true')
        except Contact.DoesNotExist:
            self.create_contact(vcs)
        except Contact.MultipleObjectsReturned:
            self.import_errors.append(_('<b>Error:</b> Vcard %s we have more than one contact that matches FN: %s.' % (self.card_no, vcs['FN'])))
            return False
        return True

    def check_mandatory_fields(self, vcs):
        retval = True
        for tag, attr in self.tags.items():
            if attr[2] > 0:  # VCard must have one of these
                if not tag in vcs:
                    self.import_errors.append(_('<b>Error:</b> Vcard %s does not contain the mangatory %s field.' % (self.card_no, tag)))
                    retval = False
        return retval


    def save_data(self, vcs):
        if not self.check_mandatory_fields(vcs):
            return False
        if not self.get_or_create_contact(vcs):
            return False
        # TEL
        tag = vcs.get('TEL')
        if tag:
            for t in tag:
                tag_type = t.get('t', 'WORK').lower()
                tag_attr = t.get('a', '').lower()
                if tag_attr == 'pref':
                        tag_type = tag_attr
                number = t.get('v')
                if number:
                    number = number.replace('-', '')
                    try:
                        obj, created = ContactTel.objects.update_or_create(
                            contact_id=self.contact,
                            number=number,
                            defaults={'tel_type': tag_type, 'updated_by': self.user_name}
                        )
                    except:
                        pass
                    else:
                        if created:
                            self.tel_added += 1
        # EMAIL
        tag = vcs.get('EMAIL')
        if tag:
            for t in tag:
                tag_type = t.get('t', 'PREF').lower()
                tag_attr = t.get('a', '').lower()
                if tag_attr == 'pref':
                        tag_type = tag_attr
                email = t.get('v')
                if email:
                    try:
                        obj, created = ContactEmail.objects.update_or_create(
                            contact_id=self.contact,
                            email=email,
                            defaults={'email_type': tag_type, 'updated_by': self.user_name}
                        )
                    except:
                        pass
                    else:
                        if created:
                            self.email_added += 1
        # ADR
        tag = vcs.get('ADR')
        if tag:
            for t in tag:
                tag_type = t.get('t', 'WORK').lower()
                tag_attr = t.get('a', '').lower()
                if tag_attr == 'pref':
                        tag_type = tag_attr
                adr = t.get('v')
                if adr:
                    try:
                        obj, created = ContactAddress.objects.update_or_create(
                            contact_id=self.contact,
                            post_office_box=adr[self.post_office_box],
                            extended_address=adr[self.extended_address],
                            street_address=adr[self.street_address],
                            locality=adr[self.locality],
                            region=adr[self.region],
                            postal_code=adr[self.postal_code],
                            country_name=adr[self.country_name],
                            defaults={'addr_type': tag_type, 'updated_by': self.user_name}
                        )
                    except:
                        pass
                    else:
                        if created:
                            self.adr_added += 1
        # GEO
        tag = vcs.get('GEO')
        if tag:
            for t in tag:
                geo = t.get('v')
                if geo:
                    latlong = '%s,%s' % (geo[latitude], geo[longitude])
                    try:
                        obj, created = ContactGeo.objects.update_or_create(
                            contact_id=self.contact,
                            geo_uri=latlong,
                            defaults={'updated_by': self.user_name}
                        )
                    except:
                        pass
                    else:
                        if created:
                            self.geo_added += 1
        # URL
        tag = vcs.get('URL')
        if tag:
            for t in tag:
                url = t.get('v')
                if url:
                    try:
                        obj, created = ContactUrl.objects.update_or_create(
                            contact_id=self.contact,
                            url_uri=url,
                            defaults={'updated_by': self.user_name}
                        )
                    except:
                        pass
                    else:
                        if created:
                            self.url_added += 1
        # ORG
        tag = vcs.get('ORG')
        if tag:
            for t in tag:
                org = t.get('v')
                if org:
                    try:
                        obj, created = ContactOrg.objects.update_or_create(
                            contact_id=self.contact,
                            organisation_name=org[organization_name],
                            organisation_unit=org[organization_unit],
                            defaults={'updated_by': self.user_name}
                        )
                    except:
                        pass
                    else:
                        if created:
                            self.org_added += 1
        # BDAY
        tag = vcs.get('BDAY')
        if tag:
            for t in tag:
                dte = t.get('v')
                if dte:
                    try:
                        sig_date = parse_datetime(dte)
                    except ValueError:
                        sig_date = None

                    if sig_date:
                        try:
                            obj, created = ContactDate.objects.update_or_create(
                                contact_id=self.contact,
                                sig_date=sig_date,
                                organisation_unit=org[organization_unit],
                                defaults={'label': 'Birthday', 'updated_by': self.user_name}
                            )
                        except:
                            pass
                        else:
                            if created:
                                self.dte_added += 1
        # CATEGORIES
        tag = vcs.get('CATEGORIES')
        if tag:
            for t in tag:
                cat = t.get('v')
                if cat:
                    try:
                        obj, created = ContactCategory.objects.update_or_create(
                            contact_id=self.contact,
                            category=cat,
                            defaults={'updated_by': self.user_name}
                        )
                    except:
                        pass
                    else:
                        if created:
                            self.cat_added += 1
        return True

    def v_read(self):
        self.card_no = 0
        in_card = False
        if not self.f:
            return False
        for line in self.f:
            if line.startswith(self.start):
                in_card = True
                self.card_no += 1
                vcs = {}
                continue
            if line.startswith(self.end):
                in_card = False
                if not self.save_data(vcs):
                    self.errors = True
                continue
            if in_card:
                try:
                    k, v = line.split(':', 1)
                except ValueError:
                    continue
                if ';' in k:
                    kta = list(map(str.strip, k.split(';')))
                else:
                    kta = [k.strip()]
                if not kta[0] in self.tags:
                    continue

                tag_attrs = self.tags[kta[0]]
                if tag_attrs[1]:  # Has fields so split them into a list
                    vv = list(map(str.strip, v.split(';')))
                else:
                    vv = v.strip(' \n')

                v_dict = {'v': vv}
                if len(kta) > 1:
                    v_dict['t'] = kta[1]
                if len(kta) == 3:
                    v_dict['a'] = kta[2]

                if tag_attrs[3]:  # Can have more than one so encapsulate in a list
                    vcs[kta[0]] = v_dict
                else:
                    if kta[0] in vcs:
                        vcs[kta[0]].append(v_dict)
                    else:
                        vcs[kta[0]] = [v_dict]

        self.v_count = self.card_no
        self.error_text.join(self.import_errors)
