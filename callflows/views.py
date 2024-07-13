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
    CallFlows,
)
from .serializers import (
    CallFlowsSerializer,
)
from .callflowfunctions import CfFunctions
from pbx.commonevents import PresenceIn


class CallFlowsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CallFlows to be viewed or edited.
    """
    queryset = CallFlows.objects.all().order_by('domain_id', 'name')
    serializer_class = CallFlowsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'name']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)
        obj = self.get_object()
        pe = PresenceIn()
        pe.send(str(obj.id), obj.status, obj.feature_code, obj.domain_id.name)
        pbxsettings = PbxSettings()
        if (pbxsettings.default_settings('dialplan', 'auto_generate_xml', 'boolean', 'true', True)[0]) == 'true':
            cff = CfFunctions(obj, self.request.user.username)
            cff.generate_xml()
        if (pbxsettings.default_settings('dialplan', 'auto_flush_cache', 'boolean', 'true', True)[0]) == 'true':
            cc = ClearCache()
            cc.dialplan(obj.domain_id.name)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    @action(detail=True)
    def generatexml(self, request, pk=None):
        obj = self.get_object()
        objf = CfFunctions(obj, request.user.username)
        dp_id = objf.generate_xml()
        if dp_id:
            obj.dialplan_id = dp_id
            obj.save()
            return Response({'status': 'ok'})
        else:
            return Response({'status': 'err'})

    @action(detail=True)
    def flush_cache_dialplan(self, request, pk=None):
        obj = self.get_object()
        ClearCache().dialplan(obj.domain_id.name)
        return Response({'status': 'dialplan cache flushed'})
