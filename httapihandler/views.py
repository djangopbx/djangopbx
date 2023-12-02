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

from django.http import HttpResponse, HttpResponseNotFound
from rest_framework import viewsets
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.csrf import csrf_exempt

from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    HttApiSession,
)
from .serializers import (
    HttApiSessionSerializer,
)
from .callblockhandler import CallBlockHandler
from .callflowtogglehandler import CallFlowToggleHandler
from .ringgrouphandler import RingGroupHandler
from .registerhandler import RegisterHandler
from .hanguphandler import HangupHandler
from .failurehandler import FailureHandler
from .followmetogglehandler import FollowMeToggleHandler
from .followmehandler import FollowMeHandler
from .testhandler import TestHandler
from .recordingshandler import RecordingsHandler
from .conferencehandler import ConferenceHandler
from .agentstatushandler import AgentStatusHandler
from .speeddialhandler import SpeedDialHandler


class HttApiSessionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows HttApiSessions to be viewed or edited.
    """
    queryset = HttApiSession.objects.all().order_by('id')
    serializer_class = HttApiSessionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


def processhttapi(request, httapihf):
    if not request.method == 'POST':
        return HttpResponseNotFound()
    if not httapihf.address_allowed(request.META['REMOTE_ADDR']):
        return HttpResponseNotFound()
    return HttpResponse(httapihf.htt_get_data(), content_type='text/xml')

@csrf_exempt
def test(request):
    httapihf = TestHandler(request.POST)
    return processhttapi(request, httapihf)

@csrf_exempt
def followmetoggle(request):
    httapihf = FollowMeToggleHandler(request.POST)
    return processhttapi(request, httapihf)

@csrf_exempt
def followme(request):
    httapihf = FollowMeHandler(request.POST)
    return processhttapi(request, httapihf)

@csrf_exempt
def failurehandler(request):
    httapihf = FailureHandler(request.POST)
    return processhttapi(request, httapihf)

@csrf_exempt
def hangup(request):
    httapihf = HangupHandler(request.POST, False)
    return processhttapi(request, httapihf)

@csrf_exempt
def register(request):
    httapihf = RegisterHandler(request.POST, False)
    return processhttapi(request, httapihf)

@csrf_exempt
def ringgroup(request):
    httapihf = RingGroupHandler(request.POST)
    return processhttapi(request, httapihf)

@csrf_exempt
def recordings(request):
    if request.content_type.startswith('multipart'):
        post, files = request.parse_file_upload(request.META, request)
        httapihf = RecordingsHandler(post, True, True, files)
    else:
        httapihf = RecordingsHandler(request.POST)
    return processhttapi(request, httapihf)

@csrf_exempt
def callflowtoggle(request):
    httapihf = CallFlowToggleHandler(request.POST)
    return processhttapi(request, httapihf)

@csrf_exempt
def callblock(request):
    httapihf = CallBlockHandler(request.POST)
    return processhttapi(request, httapihf)

@csrf_exempt
def conference(request):
    if request.content_type.startswith('multipart'):
        post, files = request.parse_file_upload(request.META, request)
        httapihf = ConferenceHandler(post, True, True, files)
    else:
        httapihf = ConferenceHandler(request.POST)
    return processhttapi(request, httapihf)

@csrf_exempt
def agentstatus(request):
    httapihf = AgentStatusHandler(request.POST)
    return processhttapi(request, httapihf)

@csrf_exempt
def speeddial(request):
    httapihf = SpeedDialHandler(request.POST)
    return processhttapi(request, httapihf)
