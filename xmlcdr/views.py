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

import os
import logging
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.html import format_html
import django_tables2 as tables
from django_filters.views import FilterView
import django_filters as filters

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
        XmlCdrFunctions().xml_cdr_import(request.GET.get('uuid', 'a_none'), request.POST.get(
            'cdr', '<?xml version=\"1.0\"?><none switchname=\"django-pbx-dev1\">'
            ))

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


class CdrViewerList(tables.Table):
    class Meta:
        model = XmlCdr
        attrs = {"class": "paleblue"}
        fields = (
            'id', 'extension_id', 'direction', 'caller_id_name', 'caller_id_number', 'destination_number',
            'caller_destination', 'recording', 'start_stamp', 'duration', 'status'
            )
        order_by = '-start_stamp'

    start_stamp = tables.DateTimeColumn(
        verbose_name=_('Date Time'), attrs={"td": {"style": "white-space: nowrap;"}}, format='Y-m-d H:i:s'
        )
    status = tables.Column(verbose_name=_('Status'), empty_values=())
    recording = tables.Column(verbose_name=_('Recording'), empty_values=())

    # id = tables.Column(linkify=("selectcdr", [tables.A("id")]))
    def render_id(self, value, record):
        return format_html('<a href=\"/xmlcdr/selectcdr/{}/\">{}</a>', value, str(value)[0:8])

    def render_status(self, value, record):
        return XmlCdrFunctions.get_call_status(record)

    def render_recording(self, value, record):
        rec_result = _('No')
        if record.record_name and record.record_path:
            rec_result = _('Yes')

        return rec_result


class CdrViewerFilter(filters.FilterSet):
    caller_id_name = filters.CharFilter(lookup_expr='icontains')
    caller_id_number = filters.CharFilter(lookup_expr='icontains')
    start_stamp = filters.DateTimeFilter(lookup_expr='gt')
    end_stamp = filters.DateTimeFilter(lookup_expr='lt')
    duration = filters.DateTimeFilter(lookup_expr='gt')

    class Meta:
        model = XmlCdr
        fields = [
            'extension_id', 'direction', 'caller_id_name', 'caller_id_number',
            'destination_number', 'caller_destination', 'start_stamp',
            'end_stamp', 'duration'
            ]


@method_decorator(login_required, name='dispatch')
class CdrViewer(tables.SingleTableMixin, FilterView):
    table_class = CdrViewerList
    filterset_class = CdrViewerFilter
    paginator_class = tables.LazyPaginator

    table_pagination = {
        "per_page": 25
    }

    def get_queryset(self):
        extension_list = self.request.session['extension_list_uuid'].split(',')
        if self.request.user.is_superuser:
            qs = XmlCdr.objects.filter(domain_id=self.request.session['domain_uuid'])
        else:
            qs = XmlCdr.objects.filter(domain_id=self.request.session['domain_uuid'], extension_id__in=extension_list)
        return qs


@login_required
def selectcdr(request, cdruuid=None):
    cache_key = 'xmlcdr:record_path'
    cdr_record_path = cache.get(cache_key)
    if not cdr_record_path:
        cdr_record_path = PbxSettings().default_settings('cdr', 'recordings', 'text', '/fs/recordings', True)[0]
        cache.set(cache_key, cdr_record_path)

    cache_key = 'switch:record_path'
    switch_record_path = cache.get(cache_key)
    if not switch_record_path:
        switch_record_path = PbxSettings().default_settings(
            'switch', 'recordings', 'dir', '/var/lib/freeswitch/recordings', True
            )[0]
        cache.set(cache_key, switch_record_path)

    extension_list = request.session['extension_list_uuid'].split(',')
    info = {}
    if request.user.is_superuser:
        cdr = XmlCdr.objects.get(domain_id=request.session['domain_uuid'], id=cdruuid)
    else:
        cdr = XmlCdr.objects.get(domain_id=request.session['domain_uuid'], extension_id__in=extension_list, id=cdruuid)
    info[cdr._meta.get_field('extension_id').verbose_name] = cdr.extension_id
    info[cdr._meta.get_field('direction').verbose_name] = cdr.direction
    info[cdr._meta.get_field('caller_id_name').verbose_name] = cdr.caller_id_name
    info[cdr._meta.get_field('caller_id_number').verbose_name] = cdr.caller_id_number
    info[cdr._meta.get_field('caller_destination').verbose_name] = cdr.caller_destination
    info[cdr._meta.get_field('source_number').verbose_name] = cdr.source_number
    info[cdr._meta.get_field('start_stamp').verbose_name] = cdr.start_stamp
    info[cdr._meta.get_field('answer_stamp').verbose_name] = cdr.answer_stamp
    info[cdr._meta.get_field('end_stamp').verbose_name] = cdr.end_stamp
    info[cdr._meta.get_field('duration').verbose_name] = cdr.duration
    info[cdr._meta.get_field('missed_call').verbose_name] = cdr.missed_call
    info[cdr._meta.get_field('waitsec').verbose_name] = cdr.waitsec

    if cdr.record_path and cdr.record_name:
        file_ext = os.path.splitext(cdr.record_name)[1]
        atype = 'audio/wav'
        if file_ext == 'mp3':
            atype = 'audio/mpeg'

        record_path_tmp = cdr.record_path.replace(switch_record_path, cdr_record_path)
        info[_('Recording')] = '<audio controls><source src="%s/%s" type="%s"> %s</audio>' % (
                record_path_tmp, cdr.record_name, atype, _('Your browser does not support the audio tag.')
                )

    return render(request, 'infotable.html', {'back': 'cdrviewer', 'info': info, 'title': 'Call Detail Record'})
