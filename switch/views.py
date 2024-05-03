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

from django.utils.http import urlsafe_base64_decode
from rest_framework import viewsets
from rest_framework import views
from rest_framework.response import Response
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from pbx.fscmdabslayer import FsCmdAbsLayer
import json

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
    FsRegistrationsSerializer,
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


class FsRegistrationsView(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Switch Registrations to be viewed.
    """
    serializer_class = FsRegistrationsSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def parseregdetail(self, regdetail):
        lines = regdetail.splitlines()
        i = 1
        info = {}
        for line in lines:
            if i > 3 and i < 17:
                if ':' in line:
                    data = line.split(':', 1)
                    info[data[0]] = data[1].strip()
            i += 1
        return info

    def get_queryset(self):
        pass

    def list(self, request):
        reg_data = []
        reg_count = 0
        es = FsCmdAbsLayer()
        if not es.connect():
            return Response({'status': 'err', 'message': 'Broker/Socket Error'})
        es.clear_responses()
        es.send('api show registrations as json')
        es.process_events()
        es.get_responses()
        es.disconnect()
        print(request.build_absolute_uri())
        for resp in es.responses:
            try:
                registrations = json.loads(resp)
            except:
                registrations = {'row_count': 0}
            if registrations['row_count'] > 0:
                reg_count += registrations.get('row_count', 0)
                for i in registrations['rows']:
                    reg_data.append(i)
        results = FsRegistrationsSerializer(reg_data, many=True, context={'request': request}).data
        return Response({'count': reg_count, 'results': results})

    def retrieve(self, request, pk=None):
        if not pk:
            return Response({'status': 'err', 'message': 'pk not found'})
        sip_user, host, sip_profile = urlsafe_base64_decode(pk).decode().split('::')
        es = FsCmdAbsLayer()
        if not es.connect():
            return Response({'status': 'err', 'message': 'Broker/Socket Error'})
        es.clear_responses()
        es.send('api sofia status profile %s user %s' % (sip_profile, sip_user), host)
        es.process_events()
        es.get_responses()
        es.disconnect()
        regdetail = next(iter(es.responses or []), None)
        if regdetail:
            info = self.parseregdetail(regdetail)
        return Response(info)
