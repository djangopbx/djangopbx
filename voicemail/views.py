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

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend


from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    Voicemail, VoicemailGreeting,
)
from .serializers import (
    VoicemailSerializer, VoicemailGreetingSerializer,
)


class VoicemailViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Voicemails to be viewed or edited.
    """
    queryset = Voicemail.objects.all().order_by('extension_id')
    serializer_class = VoicemailSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'vm_id']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class VoicemailGreetingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows VoicemailGreetingss to be viewed or edited.
    """
    queryset = VoicemailGreeting.objects.all().order_by('voicemail_id', 'name')
    serializer_class = VoicemailGreetingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['voicemail_id', 'name']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


