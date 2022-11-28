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

import logging
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from tenants.pbxsettings import PbxSettings


from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    XmlCdr,
)
from .serializers import (
    XmlCdrSerializer,
)

from .xmlcdrfunctions import XmlCdrFunctions

logger = logging.getLogger(__name__)

@csrf_exempt
def xml_cdr_import(request):
    debug = False
    aa_cache_key = 'xmlcdr:allowed_addresses'
    aa = cache.get(aa_cache_key)
    if aa:
        allowed_addresses = aa.split(',')
    else:
        allowed_addresses = PbxSettings().default_settings('cdr', 'allowed_address', 'array')
        aa = ','.join(allowed_addresses)
        cache.set(aa_cache_key, aa)

    if request.META['REMOTE_ADDR'] not in allowed_addresses:
        return HttpResponseNotFound()

    if request.method == 'POST':
        if debug:
            logger.info('XML CDR request: {}'.format(request.POST))
        XmlCdrFunctions().xml_cdr_import(request.GET.get('uuid', 'a_none'), request.POST.get('cdr', '<?xml version=\"1.0\"?><none switchname=\"django-pbx-dev1\">'))

    return HttpResponse('')


class XmlCdrViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Xml CDRs to be viewed or edited.
    """
    queryset = XmlCdr.objects.all().order_by('domain_id', 'extension_id', '-start_stamp')
    serializer_class = XmlCdrSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'direction', 'hangup_cause']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

