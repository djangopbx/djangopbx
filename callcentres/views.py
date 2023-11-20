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
    CallCentreQueues, CallCentreAgents, CallCentreTiers
)
from .serializers import (
    CallCentreQueuesSerializer, CallCentreAgentsSerializer, CallCentreTiersSerializer
)


class CallCentreQueuesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CallCentreQueues to be viewed or edited.
    """
    queryset = CallCentreQueues.objects.all().order_by('domain_id', 'name', 'extension')
    serializer_class = CallCentreQueuesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'name', 'extension', 'enabled']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class CallCentreAgentsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CallCentreAgents to be viewed or edited.
    """
    queryset = CallCentreAgents.objects.all().order_by('domain_id', 'user_uuid', 'name')
    serializer_class = CallCentreAgentsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'user_uuid', 'name']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class CallCentreTiersViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CallCentreTiers to be viewed or edited.
    """
    queryset = CallCentreTiers.objects.all().order_by('queue_id', 'agent_id')
    serializer_class = CallCentreTiersSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['queue_id', 'agent_id']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]
