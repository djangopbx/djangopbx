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

from .forms import NewIbRouteForm, NewObRouteForm
from .dialplanfunctions import SwitchDp, DpDestAction
from pbx.commonfunctions import str2regex
from accounts.accountfunctions import AccountFunctions


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


@staff_member_required
def newobroute(request):
    dp_uuid = False
    gws = []
    gw_list = [('', '')]
    gw_list.extend(AccountFunctions().list_gateways(request.session['domain_uuid']))
    if len(gw_list) > 0:
            gws.append((_('Gateways'), gw_list))

    bg_list = []
    bg_list.extend(AccountFunctions().list_bridges(request.session['domain_uuid']))
    if len(bg_list) > 0:
            gws.append((_('Bridges'), bg_list))

    other_list = [('enum', 'enum'), ('freetdm', 'freetdm'), ('transfer:$1 XML ${domain_name}', 'transfer'), ('xmpp', 'xmpp')]
    gws.append((_('Other'), other_list))


    if request.method == 'POST':

        form = NewObRouteForm(request.POST)
        form.fields['gateway1'].choices = gws
        form.fields['gateway2'].choices = gws
        form.fields['gateway3'].choices = gws

        if form.is_valid():

            routename     = form.cleaned_data['routename']
            gateway1      = form.cleaned_data['gateway1']
            gateway2      = form.cleaned_data['gateway2']
            gateway3      = form.cleaned_data['gateway3']
            dpexpression  = form.cleaned_data['dpexpression']
            prefix        = form.cleaned_data['prefix']
            limit         = form.cleaned_data['limit']
            accountcode   = form.cleaned_data['accountcode']
            tollallow     = form.cleaned_data['tollallow']
            pinnumbers    = form.cleaned_data['pinnumbers']
            dporder       = form.cleaned_data['dporder']
            enabled       = form.cleaned_data['enabled']
            description   = form.cleaned_data['description']

            dp = SwitchDp().dp_add(request.session['domain_uuid'], '8c914ec3-9fc0-8ab5-4cda-6c9288bdc9a3', routename, dpexpression[:31], 'false', request.session['domain_name'], 'Outbound route', 'false', dporder, enabled, description, request.user.username)

            gateway1_bridge_data = False
            gateway2_bridge_data = False
            gateway3_bridge_data = False

            if gateway1:
                gateway1_type = AccountFunctions().gateway_type(gateway1)
                gateway1_bridge_data = AccountFunctions().gateway_bridge_data(gateway1, gateway1_type, prefix)
            if gateway2:
                gateway2_type = AccountFunctions().gateway_type(gateway2)
                gateway2_bridge_data = AccountFunctions().gateway_bridge_data(gateway2, gateway2_type, prefix)
            if gateway3:
                gateway3_type = AccountFunctions().gateway_type(gateway3)
                gateway3_bridge_data = AccountFunctions().gateway_bridge_data(gateway3, gateway3_type, prefix)


            dp_uuid = str(dp.id)
            x_root = etree.Element('extension', name= dp.name)
            x_root.set('continue', dp.dp_continue)
            x_root.set('uuid', dp_uuid)
            etree.SubElement(x_root, 'condition', field='${user_exists}', expression='false')
            if tollallow:
                etree.SubElement(x_root, 'condition', field='${toll_allow}', expression='^%s$' % tollallow)
            x_condition = etree.SubElement(x_root, 'condition', field='destination_number', expression=dpexpression)
            etree.SubElement(x_condition, 'action', application='export', data='call_direction=outbound', inline='true')
            etree.SubElement(x_condition, 'action', application='unset', data='call_timeout')
            if gateway1_type == 'transfer':
                dialplan_detail_type = 'transfer'
            else:
                dialplan_detail_type = 'bridge'
                if accountcode:
                    etree.SubElement(x_condition, 'action', application='set', data='sip_h_X-accountcode=%s' % accountcode)
                else:
                    etree.SubElement(x_condition, 'action', application='set', data='sip_h_X-accountcode=%{accountcode}')

                etree.SubElement(x_condition, 'action', application='set', data='hangup_after_bridge=true')
                if dpexpression == '(^911$|^933$)' or dpexpression == '(^999$|^112$)':
                    etree.SubElement(x_condition, 'action', application='set', data='effective_caller_id_name=${emergency_caller_id_name}')
                else:
                    etree.SubElement(x_condition, 'action', application='set', data='effective_caller_id_name=${outbound_caller_id_name}')

                etree.SubElement(x_condition, 'action', application='set', data='inherit_codec=true')
                etree.SubElement(x_condition, 'action', application='set', data='ignore_display_updates=true')
                etree.SubElement(x_condition, 'action', application='set', data='callee_id_number=$1')
                etree.SubElement(x_condition, 'action', application='set', data='continue_on_fail=true')

            if gateway1_type == 'enum' or gateway2_type == 'enum':
                etree.SubElement(x_condition, 'action', application='enum', data='%s$1 e164.org' % prefix)

            if limit > 0:
                etree.SubElement(x_condition, 'action', application='limit', data='hash ${domain_name} outbound %s !USER_BUSY' % limit)
            if prefix:
                etree.SubElement(x_condition, 'action', application='set', data='outbound_prefix=%s' % prefix)
            if pinnumbers == 'true':
                etree.SubElement(x_condition, 'action', application='set', data='pin_number=database')
                etree.SubElement(x_condition, 'action', application='python', data='pin_number')
            etree.SubElement(x_condition, 'action', application='sleep', data='${sleep}')

            if gateway1_bridge_data:
                etree.SubElement(x_condition, 'action', application=dialplan_detail_type, data=gateway1_bridge_data)

            if gateway2_bridge_data:
                etree.SubElement(x_condition, 'action', application='bridge', data=gateway2_bridge_data)

            if gateway3_bridge_data:
                etree.SubElement(x_condition, 'action', application='bridge', data=gateway3_bridge_data)

            etree.indent(x_root)
            dp.xml = str(etree.tostring(x_root), "utf-8").replace('&lt;', '<')
            dp.save()
            messages.add_message(request, messages.INFO, _('Outbound route added'))
        else:
            messages.add_message(request, messages.INFO, _('Supplied data is invalid'))
    else:
        form = NewObRouteForm()
        form.fields['gateway1'].choices = gws
        form.fields['gateway2'].choices = gws
        form.fields['gateway3'].choices = gws

    return render(request, 'dialplans/newobroute.html', {'dp_uuid': dp_uuid, 'form': form, 'refresher': 'dialplans:newobroute',})

