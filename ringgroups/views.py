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
    RingGroup, RingGroupDestination, RingGroupUser
)
from .serializers import (
    RingGroupSerializer, RingGroupDestinationSerializer, RingGroupUserSerializer
)


class RingGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows RingGroups to be viewed or edited.
    """
    queryset = RingGroup.objects.all().order_by('domain_id', 'name', 'extension')
    serializer_class = RingGroupSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'enabled']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class RingGroupDestinationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows RingGroupDestinations to be viewed or edited.
    """
    queryset = RingGroupDestination.objects.all().order_by('ring_group_id', 'number')
    serializer_class = RingGroupDestinationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ring_group_id']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class RingGroupUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows RingGroupUsers to be viewed or edited.
    """
    queryset = RingGroupUser.objects.all().order_by('ring_group_id', 'user_uuid')
    serializer_class = RingGroupUserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ring_group_id']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]
