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
    Extension, FollowMeDestination, Gateway, Bridge,
)
from .serializers import (
    ExtensionSerializer, FollowMeDestinationSerializer, GatewaySerializer, BridgeSerializer,
)


class ExtensionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Extensions to be viewed or edited.
    """
    queryset = Extension.objects.all().order_by('domain_id', 'extension')
    serializer_class = ExtensionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'toll_allow', 'call_group', 'user_context', 'enabled']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class FollowMeDestinationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows FollowMeDestination to be viewed or edited.
    """
    queryset = FollowMeDestination.objects.all().order_by('extension_id', 'destination')
    serializer_class = FollowMeDestinationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['extension_id', 'destination']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class GatewayViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Gateways to be viewed or edited.
    """
    queryset = Gateway.objects.all().order_by('domain_id', 'gateway')
    serializer_class = GatewaySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'from_domain', 'proxy', 'realm', 'enabled']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class BridgeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Bridges to be viewed or edited.
    """
    queryset = Bridge.objects.all().order_by('domain_id', 'name')
    serializer_class = BridgeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'enabled']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]
