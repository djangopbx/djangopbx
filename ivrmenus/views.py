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
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from utilities.clearcache import ClearCache
from tenants.pbxsettings import PbxSettings

from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    IvrMenus, IvrMenuOptions
)
from .serializers import (
    IvrMenusSerializer, IvrMenuOptionsSerializer,
)
from .ivrmenufunctions import IvrFunctions


class IvrMenusViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows IvrMenus to be viewed or edited.
    """
    queryset = IvrMenus.objects.all().order_by('domain_id', 'name', 'extension')
    serializer_class = IvrMenusSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'enabled']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)
        obj = self.get_object()
        pbxsettings = PbxSettings()
        if pbxsettings.default_settings('dialplan', 'auto_generate_xml', 'boolean', True, True):
            objf = IvrFunctions(obj, self.request.user.username)
            objf.generate_xml()
        if pbxsettings.default_settings('dialplan', 'auto_flush_cache', 'boolean', True, True):
            cc = ClearCache()
            cc.dialplan(obj.domain_id.name)
            cc.ivrmenus(obj.domain_id.name)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    @action(detail=True)
    def generate_xml(self, request, pk=None):
        obj = self.get_object()
        objf = IvrFunctions(obj, request.user.username)
        dp_id = objf.generate_xml()
        if dp_id:
            obj.dialplan_id = dp_id
            obj.save()
            return Response({'status': 'ok'})
        else:
            return Response({'status': 'err'})

    @action(detail=True)
    def flush_cache_ivrmenu(self, request, pk=None):
        obj = self.get_object()
        cc = ClearCache()
        cc.dialplan(obj.domain_id.name)
        cc.ivrmenus(obj.domain_id.name)
        return Response({'status': 'ivrmenu cache flushed'})


class IvrMenuOptionsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows IvrMenuOptions to be viewed or edited.
    """
    queryset = IvrMenuOptions.objects.all().order_by('ivr_menu_id', 'sequence')
    serializer_class = IvrMenuOptionsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ivr_menu_id']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)
