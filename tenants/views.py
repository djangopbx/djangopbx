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

from django.conf import settings
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Domain, Profile, DefaultSetting, DomainSetting, ProfileSetting
)
from .serializers import (
    UserSerializer, GroupSerializer, DomainSerializer, ProfileSerializer, DefaultSettingSerializer,
    DomainSettingSerializer, ProfileSettingSerializer, GenericItemValueSerializer
)
from pbx.restpermissions import (
    AdminApiAccessPermission
)
from dialplans.dialplanfunctions import SwitchDp
from voicemail.voicemailfunctions import VoicemailFunctions
from utilities.reloadxml import ReloadXml


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['username']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class DomainViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Domains to be viewed or edited.
    """
    queryset = Domain.objects.all().order_by('name')
    serializer_class = DomainSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['home_switch', 'enabled']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        instance = serializer.save(updated_by=self.request.user.username)
        SwitchDp().import_xml(instance.name, False, instance.id)  # Create dialplans

    @action(detail=True)
    def sync_voicemail_greeting_files_with_db(self, request, pk=None):
        obj = self.get_object()
        vf = VoicemailFunctions()
        if not vf.sync_greetings(str(obj.id)):
            return Response({'status': 'host/socket error'})
        return Response({'status': 'voicemail greeting sync ok'})


class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows User Profiles to be viewed or edited.
    """
    queryset = Profile.objects.all().order_by('username')
    serializer_class = ProfileSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'username']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        instance = serializer.save(updated_by=self.request.user.username)


class DefaultSettingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Default Settings to be viewed or edited.
    """
    queryset = DefaultSetting.objects.all().order_by('category', 'subcategory')
    serializer_class = DefaultSettingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['app_uuid', 'category', 'subcategory', 'value_type']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        instance = serializer.save(updated_by=self.request.user.username)


class GenericItemValueViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Item/Value data to be viewed.
    """
    serializer_class = GenericItemValueSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def get_queryset(self):
        pass

    def append_data(self, key, value):
        return {'item': key, 'value': value}

    def list(self, request):
        raise NotImplementedError



class FreeswitchesViewSet(GenericItemValueViewSet):
    """
    API endpoint that allows Switches to be viewed.
    """
    def list(self, request):
        data = []
        i = 0
        for s in settings.PBX_FREESWITCHES:
            data.append(self.append_data(str(i), s))
            i += 1

        results = self.serializer_class(data, many=True, context={'request': request}).data
        return Response({'count': len(data), 'results': results})

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if not pk:
             return {'detail': 'Not found.'}
        try:
            pk = int(pk)
        except ValueError:
             return {'detail': 'Not found.'}
        data = []
        data.append(self.append_data(pk, settings.PBX_FREESWITCHES[pk]))
        serializer = self.serializer_class(data, many=True, context={'request': request})
        return Response(serializer.data)

    def get_fs_object(self, pk):
        if not pk:
             return -1
        try:
            pk = int(pk)
        except ValueError:
             return -1
        return settings.PBX_FREESWITCHES[pk]

    @action(detail=True)
    def reload_xml_single(self, request, pk=None):
        obj = self.get_fs_object(pk)
        rload = ReloadXml()
        if not rload.connect():
            return Response({'status': 'broker/socket error'})
        rload.xml(obj)
        return Response({'status': 'reloadxml ok'})

    @action(detail=True)
    def reload_acl_single(self, request, pk=None):
        obj = self.get_fs_object(pk)
        rload = ReloadXml()
        if not rload.connect():
            return Response({'status': 'broker/socket error'})
        rload.acl(obj)
        return Response({'status': 'reloadacl ok'})

    @action(detail=False)
    def reload_xml_global(self, request):
        rload = ReloadXml()
        if not rload.connect():
            return Response({'status': 'broker/socket error'})
        rload.xml()
        return Response({'status': 'reloadxml ok'})

    @action(detail=False)
    def reload_acl_global(self, request):
        rload = ReloadXml()
        if not rload.connect():
            return Response({'status': 'broker/socket error'})
        rload.acl()
        return Response({'status': 'reloadacl ok'})


class TimeConditionPresetsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Timecondition Presets Settings to be viewed or edited.
    """
    queryset = DefaultSetting.objects.filter(category='time_conditions').order_by('subcategory')
    serializer_class = DefaultSettingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['app_uuid', 'subcategory', 'value_type']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        instance = serializer.save(updated_by=self.request.user.username)


class DomainSettingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Domain Settings to be viewed or edited.
    """
    queryset = DomainSetting.objects.all().order_by('domain_id', 'category', 'subcategory')
    serializer_class = DomainSettingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'app_uuid', 'category', 'subcategory', 'value_type']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        instance = serializer.save(updated_by=self.request.user.username)


class ProfileSettingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Profile Settings to be viewed or edited.
    """
    queryset = ProfileSetting.objects.all().order_by('user_id', 'category', 'subcategory')
    serializer_class = ProfileSettingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user_id', 'category', 'subcategory', 'value_type']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        instance = serializer.save(updated_by=self.request.user.username)
