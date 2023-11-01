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

from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseNotFound
from lxml import etree
import uuid
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils.html import format_html
import django_tables2 as tables
from django_filters.views import FilterView
import django_filters as filters
from io import StringIO
import json
from .timeconditions import TimeConditions

from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    Dialplan, DialplanDetail,
)
from .serializers import (
    DialplanSerializer, DialplanDetailSerializer,
)

from .forms import NewIbRouteForm, NewObRouteForm, TimeConditionForm
from .dialplanfunctions import SwitchDp, DpDestAction
from pbx.commonfunctions import str2regex
from accounts.accountfunctions import AccountFunctions
from tenants.pbxsettings import PbxSettings
from tenants.models import Domain


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

            prefix             = form.cleaned_data['prefix']              # noqa: E221
            destination        = form.cleaned_data['destination']         # noqa: E221
            # calleridname     = form.cleaned_data['calleridname']        # noqa: E221
            # calleridnumber   = form.cleaned_data['calleridnumber']      # noqa: E221
            context            = form.cleaned_data['context']             # noqa: E221
            action             = form.cleaned_data['action']              # noqa: E221
            calleridnameprefix = form.cleaned_data['calleridnameprefix']  # noqa: E221
            record             = form.cleaned_data['record']              # noqa: E221
            accountcode        = form.cleaned_data['accountcode']         # noqa: E221
            enabled            = form.cleaned_data['enabled']             # noqa: E221
            description        = form.cleaned_data['description']         # noqa: E221

            dp = SwitchDp().dp_add(
                                    request.session['domain_uuid'], 'c03b422e-13a8-bd1b-e42b-b6b9b4d27ce4',
                                    destination, destination, 'false', context, 'Inbound route', 'false',
                                    100, enabled, description, request.user.username
                                    )

            dp_uuid = str(dp.id)
            x_root = etree.Element('extension', name=dp.name)
            x_root.set('continue', dp.dp_continue)
            x_root.set('uuid', dp_uuid)
            x_condition = etree.SubElement(
                x_root, 'condition', field='destination_number',
                expression=str2regex(destination, prefix)
                )
            etree.SubElement(x_condition, 'action', application='export', data='call_direction=inbound', inline='true')
            etree.SubElement(
                x_condition, 'action', application='set',
                data='domain_uuid=%s' % request.session['domain_uuid'], inline='true'
                )
            etree.SubElement(
                x_condition, 'action', application='set',
                data='domain_name=%s' % request.session['domain_name'], inline='true'
                )
            etree.SubElement(x_condition, 'action', application='set', data='hangup_after_bridge=true')
            etree.SubElement(x_condition, 'action', application='set', data='continue_on_fail=true')
            if calleridnameprefix:
                etree.SubElement(
                    x_condition, 'action', application='set',
                    data='effective_caller_id_name=%s#${caller_id_name}' % calleridnameprefix
                    )
            if record == 'true':
                etree.SubElement(
                    x_condition, 'action', application='set',
                    data='record_path=${recordings_dir}/${domain_name}/'
                    'archive/${strftime(%Y)}/${strftime(%b)}/${strftime(%d)}',
                    inline='true'
                    )
                etree.SubElement(
                    x_condition, 'action', application='set',
                    data='record_name=${uuid}.${record_ext}', inline='true'
                    )
                etree.SubElement(
                    x_condition, 'action', application='set',
                    data='record_append=true', inline='true'
                    )
                etree.SubElement(
                    x_condition, 'action', application='set',
                    data='record_in_progress=true', inline='true'
                    )
                etree.SubElement(
                    x_condition, 'action', application='set',
                    data='recording_follow_transfer=true', inline='true'
                    )
                etree.SubElement(
                    x_condition, 'action', application='record_session',
                    data='${record_path}/${record_name}'
                    )
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

    return render(request, 'dialplans/newibroute.html', {'dp_uuid': dp_uuid, 'form': form, 'refresher': 'newibroute'})


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

    other_list = [
                    ('enum', 'enum'), ('freetdm', 'freetdm'),
                    ('transfer:$1 XML ${domain_name}', 'transfer'), ('xmpp', 'xmpp')
                ]

    gws.append((_('Other'), other_list))

    if request.method == 'POST':

        form = NewObRouteForm(request.POST)
        form.fields['gateway1'].choices = gws
        form.fields['gateway2'].choices = gws
        form.fields['gateway3'].choices = gws

        if form.is_valid():

            routename     = form.cleaned_data['routename']     # noqa: E221
            gateway1      = form.cleaned_data['gateway1']      # noqa: E221
            gateway2      = form.cleaned_data['gateway2']      # noqa: E221
            gateway3      = form.cleaned_data['gateway3']      # noqa: E221
            dpexpression  = form.cleaned_data['dpexpression']  # noqa: E221
            prefix        = form.cleaned_data['prefix']        # noqa: E221
            limit         = form.cleaned_data['limit']         # noqa: E221
            accountcode   = form.cleaned_data['accountcode']   # noqa: E221
            tollallow     = form.cleaned_data['tollallow']     # noqa: E221
            pinnumbers    = form.cleaned_data['pinnumbers']    # noqa: E221
            dporder       = form.cleaned_data['dporder']       # noqa: E221
            enabled       = form.cleaned_data['enabled']       # noqa: E221
            description   = form.cleaned_data['description']   # noqa: E221

            dp = SwitchDp().dp_add(
                                    request.session['domain_uuid'], '8c914ec3-9fc0-8ab5-4cda-6c9288bdc9a3',
                                    routename, dpexpression[:31], 'false', request.session['domain_name'],
                                    'Outbound route', 'false', dporder, enabled, description, request.user.username
                                    )

            gateway1_bridge_data = False
            gateway2_bridge_data = False
            gateway3_bridge_data = False

            if gateway1:
                gateway1_type = AccountFunctions().gateway_type(gateway1)
                gateway1_bridge_data = AccountFunctions().gateway_bridge_data(gateway1, gateway1_type, prefix)
            if gateway2:
                gateway2_type = AccountFunctions().gateway_type(gateway2)
                gateway2_bridge_data = AccountFunctions().gateway_bridge_data(gateway2, gateway2_type, prefix)
            else:
                gateway2_type = 'N/A'

            if gateway3:
                gateway3_type = AccountFunctions().gateway_type(gateway3)
                gateway3_bridge_data = AccountFunctions().gateway_bridge_data(gateway3, gateway3_type, prefix)

            dp_uuid = str(dp.id)
            x_root = etree.Element('extension', name=dp.name)
            x_root.set('continue', dp.dp_continue)
            x_root.set('uuid', dp_uuid)
            etree.SubElement(x_root, 'condition', field='${user_exists}', expression='false')
            if tollallow:
                etree.SubElement(x_root, 'condition', field='${toll_allow}', expression='^%s$' % tollallow)
            x_condition = etree.SubElement(x_root, 'condition', field='destination_number', expression=dpexpression)
            etree.SubElement(
                x_condition, 'action', application='export',
                data='call_direction=outbound', inline='true'
                )
            etree.SubElement(x_condition, 'action', application='unset', data='call_timeout')
            if gateway1_type == 'transfer':
                dialplan_detail_type = 'transfer'
            else:
                dialplan_detail_type = 'bridge'
                if accountcode:
                    etree.SubElement(
                        x_condition, 'action', application='set',
                        data='sip_h_X-accountcode=%s' % accountcode
                        )
                else:
                    etree.SubElement(
                        x_condition, 'action', application='set',
                        data='sip_h_X-accountcode=%{accountcode}'
                        )

                etree.SubElement(x_condition, 'action', application='set', data='hangup_after_bridge=true')
                if dpexpression == '(^911$|^933$)' or dpexpression == '(^999$|^112$)':
                    etree.SubElement(
                        x_condition, 'action', application='set',
                        data='effective_caller_id_name=${emergency_caller_id_name}'
                        )
                else:
                    etree.SubElement(
                        x_condition, 'action', application='set',
                        data='effective_caller_id_name=${outbound_caller_id_name}'
                        )

                etree.SubElement(x_condition, 'action', application='set', data='inherit_codec=true')
                etree.SubElement(x_condition, 'action', application='set', data='ignore_display_updates=true')
                etree.SubElement(x_condition, 'action', application='set', data='callee_id_number=$1')
                etree.SubElement(x_condition, 'action', application='set', data='continue_on_fail=true')

            if gateway1_type == 'enum' or gateway2_type == 'enum':
                etree.SubElement(x_condition, 'action', application='enum', data='%s$1 e164.org' % prefix)

            if limit > 0:
                etree.SubElement(
                    x_condition, 'action', application='limit',
                    data='hash ${domain_name} outbound %s !USER_BUSY' % limit
                    )
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

    return render(request, 'dialplans/newobroute.html', {'dp_uuid': dp_uuid, 'form': form, 'refresher': 'newobroute'})


class TimeConditionViewerList(tables.Table):
    class Meta:
        model = Dialplan
        attrs = {"class": "paleblue"}
        fields = ('name', 'number', 'context', 'sequence', 'enabled', 'description')

    def render_name(self, value, record):
        return format_html('<a href=\"/dialplans/timecondition/{}/\">{}</a>', str(record.id), value)


class TimeConditionViewerFilter(filters.FilterSet):
    description = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Dialplan
        fields = ['enabled', 'number', 'description']


@method_decorator(login_required, name='dispatch')
class TimeConditionViewer(tables.SingleTableMixin, FilterView):
    table_class = TimeConditionViewerList
    filterset_class = TimeConditionViewerFilter
    paginator_class = tables.LazyPaginator
    template_name = 'dialplans/timecondition_filter.html'

    table_pagination = {
        "per_page": 25
    }

    def get_queryset(self):
        qs = Dialplan.objects.filter(domain_id=self.request.session['domain_uuid'], category='Time condition')
        return qs


@staff_member_required
def timecondition(request, dpuuid=None):
    xml_list = []
    settings_dict = {}
    if dpuuid:
        tc = Dialplan.objects.get(pk=dpuuid)
        if not tc:
            return HttpResponseNotFound()
    else:
        tc = None
        tc_id = 'New'
        tc_name = _('New Time Condition')
        tc_number = 000
        tc_sequence = 300
        tc_enabled = 'true'
        tc_description = ''
        tc_xml = '''<extension name="New_Time_Condition" continue="true" uuid="5e26f5ff-b9f2-42b5-baf2-3d589adb3659">
    <condition field="destination_number" expression="^XXX$"/>
    <condition none="0" break="never">
        <action application="transfer" data="XXX XML a.b.c"/>
    </condition>
    <condition field="destination_number" expression="^XXX$">
        <action application="transfer" data="XXX XML a.b.c"/>
    </condition>
</extension>
'''

    if request.method == 'POST':
        dp_id = request.POST['dp_id']

        try:
            settings_count = int(request.POST['settings_count'])
        except ValueError:
            settings_count = 0

        setting_condition_count = dict(json.loads(request.POST['setting_condition_count']))
        number = request.POST['number']

        # process each settings section
        last_sequence = 0
        for i in range(1, settings_count):
            cond_add = False
            xml_list.append('    <condition field=\"destination_number\" expression=\"^%s$\"/>' % number)
            cnd = ['    <condition']
            for j in range(1, setting_condition_count[str(i)] + 1):
                c = request.POST['settings_c_%s_%s' % (i, j)]
                if len(c) < 1:
                    continue
                cond_add = True
                r = request.POST['settings_r_%s_%s' % (i, j)]
                if len(r) > 0:
                    v = '%s-%s' % (request.POST['settings_v_%s_%s' % (i, j)], r)
                else:
                    v = request.POST['settings_v_%s_%s' % (i, j)]
                cnd.append('%s=\"%s\"' % (c, v))
            cnd.append('break=\"never\">')
            xml_list.append(' '.join(cnd))
            cnd.clear()
            a = request.POST['settings_a_%s' % i].split(':')
            xml_list.append('        <action application=\"%s\" data=\"%s\"/>' % (a[0], a[1]))
            xml_list.append('    </condition>')
            if cond_add:
                try:
                    last_sequence = int(request.POST['settings_s_%s' % i])
                except ValueError:
                    last_sequence = 500

                settings_dict[last_sequence] = '\n'.join(xml_list)
            xml_list.clear()

        # process the presets section
        default_action = request.POST['default_action'].split(':')
        region = request.POST['tcregion']
        p_dict = {}
        pd_list = PbxSettings().default_settings('time_conditions', 'preset_%s' % region, 'array')
        for pd in pd_list:
            p_dict.update(dict(json.loads(pd)))
        cstr_list = []
        for key, value in request.POST.items():
            if key.startswith('preset_'):
                preset_name = key[7:]
                if preset_name in p_dict:
                    xml_list.append('    <condition field=\"destination_number\" expression=\"^%s$\"/>' % number)
                    preset_data = p_dict[preset_name]
                    for pdkey, pdvalue in preset_data.items():
                        cstr_list.append('%s=\"%s\"' % (pdkey, pdvalue))
                    cstr = ' '.join(cstr_list)
                    cstr_list.clear()
                    xml_list.append('    <condition %s break=\"never\">' % cstr)
                    xml_list.append('        <action application=\"set\" data=\"preset=%s\"/>' % preset_name)
                    xml_list.append('        <action application=\"%s\" data=\"%s\"/>' % (
                                                                        default_action[0], default_action[1]
                                                                        ))
                    xml_list.append('    </condition>')

        settings_dict[last_sequence + 10] = '\n'.join(xml_list)
        xml_list.clear()

        try:
            dp_order = int(request.POST['sequence'])
        except ValueError:
            dp_order = 300
        if not dp_id == 'New':
            tc = Dialplan.objects.get(pk=dp_id)
        if not tc:
            domain = Domain.objects.get(pk=uuid.UUID(request.session['domain_uuid']))
            tc = Dialplan.objects.create(
                domain_id=domain,
                app_id='4b821450-926b-175a-af93-a03c441818b1',
                name=request.POST['name'].replace(' ', '_').lower(),
                number=request.POST['number'],
                destination='false',
                context=request.session['domain_name'],
                category='Time condition',
                dp_continue='true',
                sequence=dp_order,
                enabled=request.POST['enabled'],
                description=request.POST['description'],
                updated_by=request.user.username
            )

        xml_list.append('<extension name=\"%s\" continue=\"true\" uuid=\"%s\">' % (tc.name, str(tc.id)))
        for section in sorted(settings_dict.keys()):
            xml_list.append(settings_dict[section])

        xml_list.append('    <condition field=\"destination_number\" expression=\"^%s$\">' % number)
        xml_list.append('        <action application=\"%s\" data=\"%s\"/>' % (default_action[0], default_action[1]))
        xml_list.append('    </condition>')
        xml_list.append('</extension>')

        tc_xml = '\n'.join(xml_list)
        tc.xml = tc_xml
        tc.save()
        if dp_id == 'New':
            messages.add_message(request, messages.INFO, _('Time Condition added'))
        else:
            messages.add_message(request, messages.INFO, _('Time Condition updated'))

    if tc:
        tc_id = str(tc.id)
        tc_name = tc.name.replace('_', ' ')
        tc_number = tc.number
        tc_xml = tc.xml
        tc_sequence = tc.sequence
        tc_enabled = tc.enabled
        tc_description = tc.description

    parser = etree.XMLParser(remove_comments=True)
    tree = etree.parse(StringIO(tc_xml), parser)
    root = tree.getroot()
    form = TimeConditionForm(
        etreeroot=root,
        domain_uuid=request.session['domain_uuid'],
        initial={
                    'dp_id': tc_id, 'name': tc_name, 'number': tc_number, 'sequence': tc_sequence,
                    'enabled': tc_enabled, 'description': tc_description
                }
        )

    return render(request, 'dialplans/timecondition.html', {
                            'dp_uuid': tc_id, 'form': form, 'refresher': 'timecondition'
                            })


@login_required
def tcvrchoice(request):
    tc = TimeConditions()
    if '=' in request.META['QUERY_STRING']:
        tvc = request.META['QUERY_STRING'].split('=')
        return HttpResponse(tc.get_choices(tvc[0], tvc[1]))

    return HttpResponse('<option value=\"\"></option>')
