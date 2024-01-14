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

from django.views.generic.edit import UpdateView
from django.forms.models import inlineformset_factory
from rest_framework import viewsets
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django_tables2 import Table, SingleTableView, LazyPaginator
from django.utils.html import format_html
from django.http import HttpResponseRedirect

from pbx.commonvalidators import clean_uuid4_list
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


class CallRoutingViewerList(Table):
    class Meta:
        model = Extension
        attrs = {"class": "paleblue"}
        fields = (
            'extension',
            'do_not_disturb',
            'forward_all_enabled',
            'forward_busy_enabled',
            'forward_no_answer_enabled',
            'forward_user_not_registered_enabled',
            'follow_me_enabled'
            )
        order_by = 'extension'

    def render_extension(self, value, record):
        return format_html('<a href=\"/accounts/callroutingedit/{}/\">{}</a>', record.id, value)

    def render_do_not_disturb(self, value, record):
        return format_html(self.checkbox_conversion(value))

    def render_forward_all_enabled(self, value, record):
        return format_html(self.checkbox_conversion(value))

    def render_forward_busy_enabled(self, value, record):
        return format_html(self.checkbox_conversion(value))

    def render_forward_no_answer_enabled(self, value, record):
        return format_html(self.checkbox_conversion(value))

    def render_forward_user_not_registered_enabled(self, value, record):
        return format_html(self.checkbox_conversion(value))

    def render_follow_me_enabled(self, value, record):
        return format_html(self.checkbox_conversion(value))

    def checkbox_conversion(self, value):
        if value == 'True':
            return '<i class=\"fa fa-check\"></i>'
        else:
            return '<i class=\"fa fa-times\"></i>'


@method_decorator(login_required, name='dispatch')
class CallRoutingViewer(SingleTableView):
    table_class = CallRoutingViewerList
    model = Extension
    template_name = "accounts/call_routing.html"
    paginator_class = LazyPaginator

    table_pagination = {
        "per_page": 25
    }

    def get_queryset(self):
        extension_list = self.request.session['extension_list_uuid'].split(',')
        clean_uuid4_list(extension_list)
        if self.request.user.is_superuser:
            qs = Extension.objects.filter(domain_id=self.request.session['domain_uuid'])
        else:
            qs = Extension.objects.filter(domain_id=self.request.session['domain_uuid'], id__in=extension_list)
        return qs


class CallRoutingEdit(LoginRequiredMixin, UpdateView):
    template_name = "accounts/call_routing_edit.html"
    model = Extension
    fields = [
            'forward_all_enabled', 'forward_all_destination',
            'forward_busy_enabled', 'forward_busy_destination',
            'forward_no_answer_enabled', 'forward_no_answer_destination',
            'forward_user_not_registered_enabled', 'forward_user_not_registered_destination',
            'do_not_disturb',
            'follow_me_enabled'
            ]
    success_url = '/accounts/callrouting/'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.FollowMeDestinationFormset = inlineformset_factory(Extension, FollowMeDestination,
                fields=('destination', 'delay', 'timeout', 'prompt'), extra=3, can_delete=True)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        followme_formset = self.FollowMeDestinationFormset(instance = self.object)
        return self.render_to_response(self.get_context_data(form = form, followme_formset = followme_formset))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        followme_formset = self.FollowMeDestinationFormset(request.POST, instance=self.object)
        if (form.is_valid() and followme_formset.is_valid()):
            return self.form_valid(form, followme_formset)
        return self.form_invalid(form, followme_formset)

    def form_valid(self, form, followme_formset):
        form.instance.updated_by = self.request.user.username
        form.save()
        followme_formset.instance = self.object
        followme_formset.instance.updated_by = self.request.user.username
        followme_formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields['forward_all_destination'].widget.attrs["class"] = "form-control form-control-sm form-group"
        for key, f in form.fields.items():
            if 'destination' in key:
                f.widget.attrs['class'] = 'form-control form-control-sm form-group'
                f.label = 'Destination'
            else:
                f.widget.attrs['class'] = 'form-control form-control-sm'
        return form

    def form_invalid(self, form, followme_formset):
        return self.render_to_response(self.get_context_data(form=form, followme_formset=followme_formset))
