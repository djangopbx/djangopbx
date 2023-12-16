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
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django_tables2 import Table, SingleTableView, LazyPaginator
from django.utils.html import format_html


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
