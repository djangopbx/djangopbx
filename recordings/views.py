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
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from tenants.pbxsettings import PbxSettings
from pbx.commonfunctions import DomainUtils
from pbx.pbxipaddresscheck import pbx_ip_address_check, loopback_default
from pbx.putuploadhandler import putuploadhandler

from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    Recording, CallRecording
)
from .serializers import (
    RecordingSerializer, CallRecordingSerializer
)
from tenants.models import Domain


class RecordingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Recordings to be viewed or edited.
    """
    queryset = Recording.objects.all().order_by('domain_id', 'name')
    serializer_class = RecordingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'name', 'filestore']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_destroy(self, instance):
        instance.filename.delete(save=False)
        instance.delete()


class CallRecordingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Call Recordings to be viewed or edited.
    """
    queryset = CallRecording.objects.all().order_by('domain_id', 'name')
    serializer_class = CallRecordingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'year', 'month', 'day', 'filestore']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_destroy(self, instance):
        instance.filename.delete(save=False)
        instance.delete()


def rec_check_address(request):
    aa_cache_key = 'recordings:allowed_addresses'
    aa = cache.get(aa_cache_key)
    if not aa:
        aa = PbxSettings().default_settings('recordings', 'allowed_address', 'array')
        if not aa:
            aa = loopback_default
        cache.set(aa_cache_key, aa)
    if not pbx_ip_address_check(request, aa):
        return False
    return True

@csrf_exempt
def rec_import(request, domain, recfile):
    if not rec_check_address(request):
        return HttpResponseNotFound()
    try:
        d = Domain.objects.get(name=domain)
    except Domain.DoesNotExist:
        return HttpResponseNotFound()

    if request.method == "PUT": # FreeSWITCH mod_http_cache PUT request
        if not putuploadhandler(request):
            return HttpResponse(status=400)

    if request.method == "POST" or request.method == "PUT": # Multipart form data with file field POST request
        rec = Recording.objects.create(name=recfile,
                domain_id=d, updated_by='Recording Import %s' % request.method)
        rec.filename.save(recfile, request.FILES[recfile])
    return HttpResponse('')

@csrf_exempt
def call_rec_import(request, domain, year, month, day, recfile):
    if not rec_check_address(request):
        return HttpResponseNotFound()
    try:
        d = Domain.objects.get(name=domain)
    except Domain.DoesNotExist:
        return HttpResponseNotFound()

    if request.method == "PUT": # FreeSWITCH mod_http_cache PUT request
        if not putuploadhandler(request):
            return HttpResponse(status=400)

    if request.method == "POST" or request.method == "PUT": # Multipart form data with file field POST request
        rec = CallRecording.objects.create(name=recfile,
                domain_id=d, year=year, month=month, day=day,
                updated_by='Call Record Import %s' % request.method)
        rec.filename.save(recfile, request.FILES[recfile])
    return HttpResponse('')
