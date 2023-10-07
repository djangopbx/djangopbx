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

from rest_framework import serializers
from .models import (
    Contact, ContactTel, ContactEmail, ContactGeo, ContactUrl, ContactOrg,
    ContactAddress, ContactDate, ContactCategory, ContactGroup
)


class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact
        fields = [
                'url', 'id',
                'domain_id', 'user_id', 'fn', 'family_name', 'given_name',
                'additional_name', 'honorific_prefix', 'honorific_suffix',
                'nickname', 'timezone', 'notes', 'enabled',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class ContactTelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactTel
        fields = [
                'url', 'id',
                'contact_id', 'tel_type', 'number',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class ContactEmailSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactEmail
        fields = [
                'url', 'id',
                'contact_id', 'email_type', 'email',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class ContactGeoSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactGeo
        fields = [
                'url', 'id',
                'contact_id', 'geo_uri',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class ContactUrlSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactUrl
        fields = [
                'url', 'id',
                'contact_id', 'url_uri',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class ContactOrgSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactOrg
        fields = [
                'url', 'id',
                'contact_id', 'organisation_name', 'organisation_unit',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class ContactAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactAddress
        fields = [
                'url', 'id',
                'contact_id', 'post_office_box', 'extended_address', 'street_address',
                'locality', 'region', 'postal_code', 'country_name',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class ContactDateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactDate
        fields = [
                'url', 'id',
                'contact_id', 'sig_date', 'label',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class ContactCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactCategory
        fields = [
                'url', 'id',
                'contact_id', 'category',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class ContactGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactGroup
        fields = [
                'url', 'id',
                'contact_id', 'name', 'group_id',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


