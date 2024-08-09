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

from django.views.generic.edit import UpdateView
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django_tables2 import Table, SingleTableView, LazyPaginator
from django.utils.html import format_html
from utilities.clearcache import ClearCache
from tenants.pbxsettings import PbxSettings

from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    RingGroup, RingGroupDestination, RingGroupUser
)
from .serializers import (
    RingGroupSerializer, RingGroupDestinationSerializer, RingGroupUserSerializer
)
from .ringgroupfunctions import RgFunctions


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

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)
        obj = self.get_object()
        pbxsettings = PbxSettings()
        if pbxsettings.default_settings('dialplan', 'auto_generate_xml', 'boolean', True, True):
            objf = RgFunctions(str(obj.domain_id.id), obj.domain_id.name, obj, self.request.user.username)
            dp_id = objf.generate_xml()
            if dp_id:
                obj.dialplan_id = dp_id
                obj.save()
        if pbxsettings.default_settings('dialplan', 'auto_flush_cache', 'boolean', True, True):
            ClearCache().dialplan(obj.domain_id.name)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    @action(detail=True)
    def generate_xml(self, request, pk=None):
        obj = self.get_object()
        objf = RgFunctions(str(obj.domain_id.id), obj.domain_id.name, obj, request.user.username)
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

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


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

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class RingGroupViewerList(Table):
    class Meta:
        model = RingGroup
        attrs = {"class": "paleblue"}
        fields = (
            'name',
            'extension',
            'forward_enabled',
            'forward_destination',
            'description'
            )
        order_by = 'name'

    def render_name(self, value, record):
        return format_html('<a href=\"/ringgroups/fwdedit/{}/\">{}</a>', record.id, value)

    def render_forward_enabled(self, value, record):
        return format_html(self.checkbox_conversion(value))

    def checkbox_conversion(self, value):
        if value == 'True':
            return '<i class=\"fa fa-check\"></i>'
        else:
            return '<i class=\"fa fa-times\"></i>'


@method_decorator(login_required, name='dispatch')
class RingGroupViewer(SingleTableView):
    table_class = RingGroupViewerList
    model = RingGroup
    template_name = "ringgroups/group.html"
    paginator_class = LazyPaginator

    table_pagination = {
        "per_page": 25
    }

    def get_queryset(self):
        if self.request.user.is_superuser:
            qs = RingGroup.objects.filter(domain_id=self.request.session['domain_uuid']).order_by('name')
        else:
            qs = RingGroup.objects.filter(domain_id=self.request.session['domain_uuid'],
                ringgroupuser__user_uuid=self.request.session['user_uuid']).order_by('name')
        return qs


class FwdEdit(LoginRequiredMixin, UpdateView):
    template_name = "ringgroups/fwd_edit.html"
    model = RingGroup
    fields = [
            'forward_enabled',
            'forward_destination',
            ]
    success_url = '/ringgroups/groups/'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back'] = '/ringgroups/groups/'
        return context
