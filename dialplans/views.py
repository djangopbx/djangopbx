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

from django.utils.translation import gettext, gettext_lazy as _
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from lxml import etree

from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    Dialplan, DialplanDetail,
)
from .serializers import (
    DialplanSerializer, DialplanDetailSerializer,
)

from .forms import NewIbRouteForm
from .dialplanfunctions import SwitchDp, DpDestAction
from pbx.commonfunctions import str2regex


class DialplanViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Dialplans to be viewed or edited.
    """
    queryset = Dialplan.objects.all().order_by('sequence', 'name')
    serializer_class = DialplanSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'name']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class DialplanDetailViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows DialplanDetails to be viewed or edited.
    """
    queryset = DialplanDetail.objects.all().order_by('dialplan_id', 'sequence')
    serializer_class = DialplanDetailSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dialplan_id']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


@staff_member_required
def newibroute(request):
    dp_uuid = False
    if request.method == 'POST':

        form = NewIbRouteForm(request.POST)
        form.fields['action'].choices = DpDestAction().get_dp_action_choices(request.session['domain_uuid'])

        if form.is_valid():

            prefix             = form.cleaned_data['prefix']
            destination        = form.cleaned_data['destination']
            calleridname       = form.cleaned_data['calleridname']
            calleridnumber     = form.cleaned_data['calleridnumber']
            context            = form.cleaned_data['context']
            action             = form.cleaned_data['action']
            calleridnameprefix = form.cleaned_data['calleridnameprefix']
            record             = form.cleaned_data['record']
            accountcode        = form.cleaned_data['accountcode']
            enabled            = form.cleaned_data['enabled']
            description        = form.cleaned_data['description']

            dp = SwitchDp().dp_add(request.session['domain_uuid'], 'c03b422e-13a8-bd1b-e42b-b6b9b4d27ce4', destination, destination, 'false', context, 'Inbound route', 'false', 100, enabled, description, request.user.username)

            dp_uuid = str(dp.id)
            x_root = etree.Element('extension', name= dp.name)
            x_root.set('continue', dp.dp_continue)
            x_root.set('uuid', dp_uuid)
            x_condition = etree.SubElement(x_root, 'condition', field='destination_number', expression=str2regex(destination, prefix))
            etree.SubElement(x_condition, 'action', application='export', data='call_direction=inbound', inline='true')
            etree.SubElement(x_condition, 'action', application='set', data='domain_uuid=%s' % request.session['domain_uuid'], inline='true')
            etree.SubElement(x_condition, 'action', application='set', data='domain_name=%s' % request.session['domain_name'], inline='true')
            etree.SubElement(x_condition, 'action', application='set', data='hangup_after_bridge=true')
            etree.SubElement(x_condition, 'action', application='set', data='continue_on_fail=true')
            if calleridnameprefix:
                etree.SubElement(x_condition, 'action', application='set', data='effective_caller_id_name=%s#${caller_id_name}' % calleridnameprefix)
            if record == 'true':
                etree.SubElement(x_condition, 'action', application='set', data='record_path=${recordings_dir}/${domain_name}/archive/${strftime(%Y)}/${strftime(%b)}/${strftime(%d)}', inline='true')
                etree.SubElement(x_condition, 'action', application='set', data='record_name=${uuid}.${record_ext}', inline='true')
                etree.SubElement(x_condition, 'action', application='set', data='record_append=true', inline='true')
                etree.SubElement(x_condition, 'action', application='set', data='record_in_progress=true', inline='true')
                etree.SubElement(x_condition, 'action', application='set', data='recording_follow_transfer=true', inline='true')
                etree.SubElement(x_condition, 'action', application='record_session', data='${record_path}/${record_name}')
            if accountcode:
                etree.SubElement(x_condition, 'action', application='set', data='accountcode=%s' % accountcode)

            if ':' in action:
                parts = action.split(':', 1)
            etree.SubElement(x_condition, 'action', application=parts[0], data=parts[1])

            etree.indent(x_root)
            dp.xml = str(etree.tostring(x_root), "utf-8").replace('&lt;', '<')
            dp.save()
            messages.add_message(request, messages.INFO, _('Inbound route added'))
        else:
            messages.add_message(request, messages.INFO, _('Supplied data is invalid'))
    else:
        form = NewIbRouteForm()
        form.fields['action'].choices = DpDestAction().get_dp_action_choices(request.session['domain_uuid'])

    return render(request, 'dialplans/newibroute.html', {'dp_uuid': dp_uuid, 'form': form, 'refresher': 'dialplans:newibroute',})
