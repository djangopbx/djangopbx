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

from rest_framework import viewsets
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend

from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    Contact, ContactTel, ContactEmail, ContactGeo, ContactUrl, ContactOrg, ContactAddress, 
    ContactDate, ContactCategory, ContactGroup,
)
from .serializers import (
    ContactSerializer, ContactTelSerializer, ContactEmailSerializer, ContactGeoSerializer,
    ContactUrlSerializer, ContactOrgSerializer, ContactAddressSerializer,
    ContactDateSerializer, ContactCategorySerializer, ContactGroupSerializer,
)


class ContactViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Contacts to be viewed or edited.
    """
    queryset = Contact.objects.all().order_by('fn')
    serializer_class = ContactSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'user_id', 'family_name', 'fn', 'nickname', 'enabled']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactTelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ContactTel to be viewed or edited.
    """
    queryset = ContactTel.objects.all().order_by('number')
    serializer_class = ContactTelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contact_id', 'tel_type', 'number']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactEmailViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ContactEmail to be viewed or edited.
    """
    queryset = ContactEmail.objects.all().order_by('email')
    serializer_class = ContactEmailSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contact_id', 'email_type']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactGeoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ContactGeo to be viewed or edited.
    """
    queryset = ContactGeo.objects.all().order_by('geo_uri')
    serializer_class = ContactGeoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contact_id',]
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactUrlViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ContactUrl to be viewed or edited.
    """
    queryset = ContactUrl.objects.all().order_by('url_uri')
    serializer_class = ContactUrlSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contact_id',]
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactOrgViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ContactOrg to be viewed or edited.
    """
    queryset = ContactOrg.objects.all().order_by('organisation_name')
    serializer_class = ContactOrgSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contact_id',]
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactAddressViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ContactAddress to be viewed or edited.
    """
    queryset = ContactAddress.objects.all().order_by('postal_code')
    serializer_class = ContactAddressSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contact_id', 'locality', 'region']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactDateViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ContactDate to be viewed or edited.
    """
    queryset = ContactDate.objects.all().order_by('contact_id')
    serializer_class = ContactDateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['label', 'sig_date']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ContactCategory to be viewed or edited.
    """
    queryset = ContactCategory.objects.all().order_by('category')
    serializer_class = ContactCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contact_id', 'category']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ContactGroup to be viewed or edited.
    """
    queryset = ContactGroup.objects.all().order_by('name')
    serializer_class = ContactGroupSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contact_id', 'group_id']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


