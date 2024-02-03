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

from rest_framework import viewsets
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend


from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    SipProfileDomain, SipProfileSetting, SipProfile, SwitchVariable, AccessControl,
    AccessControlNode, EmailTemplate, Modules
)
from .serializers import (
    SipProfileDomainSerializer, SipProfileSettingSerializer, SipProfileSerializer, SwitchVariableSerializer,
    AccessControlSerializer, AccessControlNodeSerializer,  EmailTemplateSerializer, ModulesSerializer,
)


class SipProfileDomainViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows SipProfileDomains to be viewed or edited.
    """
    queryset = SipProfileDomain.objects.all().order_by('sip_profile_id', 'name')
    serializer_class = SipProfileDomainSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sip_profile_id', 'name']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class SipProfileSettingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows SipProfileSettings to be viewed or edited.
    """
    queryset = SipProfileSetting.objects.all().order_by('sip_profile_id', 'name')
    serializer_class = SipProfileSettingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sip_profile_id', 'name']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class SipProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows SipProfiles to be viewed or edited.
    """
    queryset = SipProfile.objects.all().order_by('name')
    serializer_class = SipProfileSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class SwitchVariableViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows SwitchVariables to be viewed or edited.
    """
    queryset = SwitchVariable.objects.all().order_by('category', 'name')
    serializer_class = SwitchVariableSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'name']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class AccessControlViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows AccessControls to be viewed or edited.
    """
    queryset = AccessControl.objects.all().order_by('name')
    serializer_class = AccessControlSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class AccessControlNodeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows AccessControlNodes to be viewed or edited.
    """
    queryset = AccessControlNode.objects.all().order_by('description')
    serializer_class = AccessControlNodeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['description']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Email templates to be viewed or edited.
    """
    queryset = EmailTemplate.objects.all().order_by('language', 'category', 'subcategory')
    serializer_class = EmailTemplateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['language', 'category', 'subcategory', 'type']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class ModulesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Switch Modules to be viewed or edited.
    """
    queryset = Modules.objects.all().order_by('sequence', 'category', 'name')
    serializer_class = ModulesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'name']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)
