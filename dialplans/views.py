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

import uuid
import re
import json
from lxml import etree
from io import StringIO
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils.html import format_html
import django_tables2 as tables
from django_filters.views import FilterView
import django_filters as filters
from utilities.clearcache import ClearCache
from .timeconditions import TimeConditions

from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    Dialplan, DialplanDetail,
)
from .serializers import (
    DialplanSerializer, DialplanDetailSerializer, InboundRouteSerializer,
    OutboundRouteSerializer, TimeConditionSerializer,
)

from .forms import NewIbRouteForm, NewObRouteForm, TimeConditionForm
from .dialplanfunctions import SwitchDp
from pbx.commonfunctions import DomainUtils
from pbx.commondestination import CommonDestAction
from accounts.accountfunctions import AccountFunctions
from tenants.pbxsettings import PbxSettings
from tenants.models import Domain
from django.db.models import Value
from .inboundroute import InboundRoute
from .outboundroute import OutboundRoute
from .timecondition import TimeCondition


class DialplanInboundRoute(viewsets.ViewSet):
    serializer_class = InboundRouteSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def list(self, request):
        queryset = Dialplan.objects.filter(category='Inbound route').annotate(
            prefix=Value(''),
            caller_id_name_prefix=Value(''),
            application=Value('transfer'),
            data=Value('201 XML djangopbx.com'),
            record=Value('N/A'),
            account_code=Value('')
            ).order_by('sequence', 'name')
        serializer = InboundRouteSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        query = Dialplan.objects.filter(pk=pk).annotate(
            prefix=Value(''),
            application=Value('transfer'),
            data=Value('201 XML djangopbx.com'),
            caller_id_name_prefix=Value(''),
            record=Value('N/A'),
            account_code=Value('')
            ).first()
        serializer = InboundRouteSerializer(instance=query, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        serializer = InboundRouteSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            ibr = serializer.save()
            d = DomainUtils().domain_from_name(ibr.domain_id)
            if d:
                dp = Dialplan.objects.create(
                    domain_id=d,
                    app_id='c03b422e-13a8-bd1b-e42b-b6b9b4d27ce4',
                    name=ibr.number,
                    number=ibr.number,
                    destination='false',
                    context=ibr.context,
                    category='Inbound route',
                    dp_continue='false',
                    sequence=100,
                    enabled=ibr.enabled,
                    description=ibr.description,
                    updated_by=request.user.username
                )
                dp.xml = ibr.generate_xml(dp)
                dp.save()
                data = serializer.data
                data['id'] = str(dp.id)
                data['url'] = request.build_absolute_uri('/api/dialplan_ib_route/%s/' % str(dp.id))
                return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Commented out because we don't want an update form, an inbound route is a dialplan record
#  so it can be updated there.  Thsi class just generates new inbound routes and
#  allows existing ones to be deleted.
#
#    def update(self, request, pk=None):
#        pass

#    def partial_update(self, request, pk=None):
#        pass

    def destroy(self, request, pk=None):
        try:
            Dialplan.objects.get(pk=pk).delete()
        except Dialplan.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DialplanOutboundRoute(viewsets.ViewSet):
    serializer_class = OutboundRouteSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def list(self, request):
        queryset = Dialplan.objects.filter(category='Outbound route').annotate(
            gateway_1=Value(''),
            gateway_2=Value(''),
            gateway_3=Value(''),
            prefix=Value(''),
            limit=Value(0),
            account_code=Value(''),
            toll_allow=Value(''),
            pin_numbers=Value('')
            ).order_by('sequence', 'name')
        serializer = OutboundRouteSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        query = Dialplan.objects.filter(pk=pk).annotate(
            gateway_1=Value(''),
            gateway_2=Value(''),
            gateway_3=Value(''),
            prefix=Value(''),
            limit=Value(0),
            account_code=Value(''),
            toll_allow=Value(''),
            pin_numbers=Value('')
            ).first()
        serializer = OutboundRouteSerializer(instance=query, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        serializer = OutboundRouteSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            obr = serializer.save()
            d = DomainUtils().domain_from_name(obr.domain_id)
            if d:
                context = d.name
                dp = Dialplan.objects.create(
                    domain_id=d,
                    app_id='8c914ec3-9fc0-8ab5-4cda-6c9288bdc9a3',
                    name=obr.name,
                    number=obr.number[:31],
                    destination='false',
                    context=context,
                    category='Outbound route',
                    dp_continue='false',
                    sequence=obr.sequence,
                    enabled=obr.enabled,
                    description=obr.description,
                    updated_by=request.user.username
                )
                dp.xml = obr.generate_xml(dp)
                dp.save()
                data = serializer.data
                data['id'] = str(dp.id)
                data['url'] = request.build_absolute_uri('/api/dialplan_ob_route/%s/' % str(dp.id))
                return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            Dialplan.objects.get(pk=pk).delete()
        except Dialplan.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DialplanTimeCondition(viewsets.ViewSet):
    serializer_class = TimeConditionSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def list(self, request):
        queryset = Dialplan.objects.filter(category='Time condition').annotate(
            settings=Value(''),
            alternate_destination=Value(''),
            ).order_by('sequence', 'name')
        serializer = TimeConditionSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        query = Dialplan.objects.filter(pk=pk).annotate(
            settings=Value(''),
            alternate_destination=Value(''),
            ).first()
        if query.xml:
            settings = re.search('<extension[^>]*>\n?(.*)\n\n*</extension>.*', query.xml, re.DOTALL)
            if settings:
                slist = settings.group(1).replace('  ', ' ').replace('  ', ' ').split('\n')
                query.settings = '<settings>\n%s\n</settings>' % ('\n'.join(slist[:-3]))
                query.alternate_destination = '\n'.join(slist[-3:])
        serializer = TimeConditionSerializer(instance=query, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        serializer = TimeConditionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            tcnd = serializer.save()
            d = DomainUtils().domain_from_name(tcnd.domain_id)
            if d:
                dp = Dialplan.objects.create(
                    domain_id=d,
                    app_id='4b821450-926b-175a-af93-a03c441818b1',
                    name=tcnd.name,
                    number=tcnd.number,
                    destination='false',
                    context=tcnd.context,
                    category='Time condition',
                    dp_continue='false',
                    sequence=tcnd.sequence,
                    enabled=tcnd.enabled,
                    description=tcnd.description,
                    updated_by=request.user.username
                )
                dp.xml = tcnd.generate_xml(dp)
                dp.save()
                data = serializer.data
                data['id'] = str(dp.id)
                data['url'] = request.build_absolute_uri('/api/dialplan_time_condition/%s/' % str(dp.id))
                return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        serializer = TimeConditionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            tcnd = serializer.save()
            d = DomainUtils().domain_from_name(tcnd.domain_id)
            if d:
                try:
                    dp = Dialplan.objects.get(pk=pk)
                except Dialplan.DoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND)

                dp.domain_id=d
                dp.name=tcnd.name
                dp.number=tcnd.number
                dp.context=tcnd.context
                dp.sequence=tcnd.sequence
                dp.enabled=tcnd.enabled
                dp.description=tcnd.description
                dp.updated_by=request.user.username
                dp.xml = tcnd.generate_xml(dp)
                dp.save()
                data = serializer.data
                data['id'] = str(dp.id)
                data['url'] = request.build_absolute_uri('/api/dialplan_time_condition/%s/' % str(dp.id))
                return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            Dialplan.objects.get(pk=pk).delete()
        except Dialplan.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DialplanViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Dialplans to be viewed or edited.
    """
    queryset = Dialplan.objects.all().order_by('sequence', 'name')
    serializer_class = DialplanSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'name', 'category']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    @action(detail=False)
    def flush_cache_all_dialplans(self, request):
        ClearCache().dialplan()
        return Response({'status': 'dialplan cache flushed'})

    @action(detail=True)
    def flush_cache_dialplan(self, request, pk=None):
        obj = self.get_object()
        if obj.domain_id:
            ClearCache().dialplan(obj.domain_id.name)
        else:
            ClearCache().dialplan(obj.context)
        return Response({'status': 'dialplan cache flushed'})


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

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


@staff_member_required
def newibroute(request):
    dp_uuid = False
    if request.method == 'POST':
        form = NewIbRouteForm(request.POST)
        form.fields['action'].choices = CommonDestAction(request.session['domain_name'], request.session['domain_uuid']).get_action_choices()
        if form.is_valid():
            ibr = InboundRoute()
            ibr.prefix                = form.cleaned_data['prefix']              # noqa: E221
            ibr.number                = form.cleaned_data['destination']         # noqa: E221
            ibr.context               = form.cleaned_data['context']             # noqa: E221
            action                    = form.cleaned_data['action']              # noqa: E221
            ibr.caller_id_name_prefix = form.cleaned_data['calleridnameprefix']  # noqa: E221
            ibr.record                = form.cleaned_data['record']              # noqa: E221
            ibr.accountcode           = form.cleaned_data['accountcode']         # noqa: E221
            ibr.enabled               = form.cleaned_data['enabled']             # noqa: E221
            ibr.description           = form.cleaned_data['description']         # noqa: E221
            if ':' in action:
                parts = action.split(':', 1)
                ibr.application = parts[0]
                ibr.data=parts[1]
            else:
                ibr.application=action
                ibr.data=''
            ibr.domain_id = request.session['domain_name']
            dp = SwitchDp().dp_add(
                                    request.session['domain_uuid'], 'c03b422e-13a8-bd1b-e42b-b6b9b4d27ce4',
                                    ibr.number, ibr.number, 'false', ibr.context, 'Inbound route', 'false',
                                    100, ibr.enabled, ibr.description, request.user.username
                                    )
            dp.xml = ibr.generate_xml(dp)
            dp.save()
            messages.add_message(request, messages.INFO, _('Inbound route added'))
        else:
            messages.add_message(request, messages.INFO, _('Supplied data is invalid'))
    else:
        form = NewIbRouteForm()
        form.fields['action'].choices = CommonDestAction(request.session['domain_name'], request.session['domain_uuid']).get_action_choices()
    return render(request, 'dialplans/newibroute.html', {'dp_uuid': dp_uuid, 'form': form, 'refresher': 'newibroute'})


@staff_member_required
def newobroute(request):
    af = AccountFunctions()
    dp_uuid = False
    gws = []
    gw_list = [('', '')]
    gw_list.extend(af.list_gateways(None, True))
    if len(gw_list) > 0:
        gws.append((_('Global Gateways'), gw_list))
    gw_list = []
    gw_list.extend(af.list_gateways(request.session['domain_uuid']))
    if len(gw_list) > 0:
        gws.append((_('Gateways'), gw_list))

    bg_list = []
    bg_list.extend(af.list_bridges(request.session['domain_uuid']))
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
            obr = OutboundRoute()
            obr.name          = form.cleaned_data['routename']     # noqa: E221
            obr.gateway_1     = form.cleaned_data['gateway1']      # noqa: E221
            obr.gateway_2     = form.cleaned_data['gateway2']      # noqa: E221
            obr.gateway_3     = form.cleaned_data['gateway3']      # noqa: E221
            obr.number        = form.cleaned_data['dpexpression']  # noqa: E221
            obr.prefix        = form.cleaned_data['prefix']        # noqa: E221
            obr.limit         = form.cleaned_data['limit']         # noqa: E221
            obr.account_code  = form.cleaned_data['accountcode']   # noqa: E221
            obr.toll_allow    = form.cleaned_data['tollallow']     # noqa: E221
            obr.pin_numbers   = form.cleaned_data['pinnumbers']    # noqa: E221
            obr.sequence      = form.cleaned_data['dporder']       # noqa: E221
            obr.enabled       = form.cleaned_data['enabled']       # noqa: E221
            obr.description   = form.cleaned_data['description']   # noqa: E221
            dp = SwitchDp().dp_add(
                                    request.session['domain_uuid'], '8c914ec3-9fc0-8ab5-4cda-6c9288bdc9a3',
                                    obr.name, obr.number[:31], 'false', request.session['domain_name'],
                                    'Outbound route', 'false', obr.sequence, obr.enabled, obr.description, request.user.username
                                    )
            dp.xml = obr.generate_xml(dp)
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
                    if c == 'date-time':
                        v = '%s~%s' % (request.POST['settings_v_%s_%s' % (i, j)], r)
                    else:
                        v = '%s-%s' % (request.POST['settings_v_%s_%s' % (i, j)], r)
                else:
                    v = request.POST['settings_v_%s_%s' % (i, j)]
                cnd.append('%s=\"%s\"' % (c, v))
            cnd.append('break=\"never\">')
            xml_list.append(' '.join(cnd))
            cnd.clear()
            a = request.POST['settings_a_%s' % i].split(':')
            if len(a) > 1:
                xml_list.append('        <action application=\"%s\" data=\"%s\"/>' % (a[0], a[1]))
            else:
                xml_list.append('        <action application=\"%s\" data=\"\"/>' % (a[0]))
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
        pd_list = PbxSettings().default_settings('time_conditions', 'preset_%s' % region, 'array', [], True)
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
        domain_name=request.session['domain_name'],
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
