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

import uuid
from datetime import datetime
from django.core.cache import cache
from django.views import View
from django.views.generic.edit import UpdateView
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django_tables2 import Table, SingleTableView, LazyPaginator
from django.utils.html import format_html
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from .callcentrefunctions import CcFunctions


from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    CallCentreQueues, CallCentreAgents, CallCentreTiers
)
from .serializers import (
    CallCentreQueuesSerializer, CallCentreAgentsSerializer, CallCentreTiersSerializer
)


class CallCentreQueuesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CallCentreQueues to be viewed or edited.
    """
    queryset = CallCentreQueues.objects.all().order_by('domain_id', 'name', 'extension')
    serializer_class = CallCentreQueuesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'name', 'extension', 'enabled']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    @action(detail=True)
    def generatexml(self, request, pk=None):
        obj = self.get_object()
        objf = CcFunctions(obj, request.user.username)

        dp_id = objf.generate_xml()
        if dp_id:
            obj.dialplan_id = dp_id
            obj.save()
            return Response({'status': 'ok'})
        else:
            return Response({'status': 'err'})


class CallCentreAgentsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CallCentreAgents to be viewed or edited.
    """
    queryset = CallCentreAgents.objects.all().order_by('domain_id', 'user_uuid', 'name')
    serializer_class = CallCentreAgentsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'user_uuid', 'name']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class CallCentreTiersViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CallCentreTiers to be viewed or edited.
    """
    queryset = CallCentreTiers.objects.all().order_by('queue_id', 'agent_id')
    serializer_class = CallCentreTiersSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['queue_id', 'agent_id']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class CcQueueListList(Table):
    class Meta:
        model = CallCentreQueues
        attrs = {"class": "paleblue"}
        fields = (
            'name',
            'extension',
            'description'
            )
        order_by = 'name'

    def render_name(self, value, record):
        return format_html('<a href=\"/callcentres/ccqueueedit/{}/\">{}</a>', record.id, value)


@method_decorator(login_required, name='dispatch')
class CcQueueList(SingleTableView):
    table_class = CcQueueListList
    model = CallCentreQueues
    template_name = "callcentres/queue_list.html"
    paginator_class = LazyPaginator

    table_pagination = {
        "per_page": 25
    }

    def get_queryset(self):
        qs = CallCentreQueues.objects.filter(domain_id=self.request.session['domain_uuid'], enabled='true').order_by('name')
        return qs


class CcQueueEdit(LoginRequiredMixin, UpdateView):
    template_name = "callcentres/queue_edit.html"
    model = CallCentreQueues
    fields = [
            'name',
            'description',
            'wb_wait_warn_level',
            'wb_wait_crit_level',
            'wb_aban_warn_level',
            'wb_aban_crit_level',
            'wb_show_agents',
            'wb_agents_per_row',
            ]
    success_url = '/callcentres/ccqueues/'

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
        context['back'] = '/callcentres/ccqueues/'
        return context


class WbSingleQueueBase(View):
    wb_status = 'wb_status'
    wb_colour = 'wb_colour'
    wb_status_time = 'status_time'
    wb_ccwb_ok = 'ccwb-ok'
    wb_ccwb_warn = 'ccwb-warn'
    wb_ccwb_crit = 'ccwb-crit'
    wb_abandoned_colour = 'abandoned_colour'
    wb_waiting_colour = 'waiting_colour'
    default_q_settings = {'ww': 5, 'wc': 20, 'aw': 5, 'ac': 20, 'sa': 1, 'apr': 6 }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = {}
        self.agents = {}
        self.agent_count = 0;
        self.trying_count = 0
        self.ccq_id = None
        self.token = None

    def get_agents_detail(self):
        ccts = CallCentreTiers.objects.filter(queue_id=self.ccq_id)
        for cct in ccts:
            self.agent_count += 1
            agent_status = cache.get('fs:cc:a:%s:agent-status' % cct.agent_id.id, b'Logged+Out').decode()
            agent_key = '_%s' % str(cct.agent_id.id).replace('-', '_')
            self.agents[agent_key] = {'name': cct.agent_id.name}
            try:
                agent_status_time = int(cache.get('fs:cc:a:%s:agent-status-time' % cct.agent_id.id, b'0').decode())
                agent_status_time /= 1000000
            except ValueError:
                agent_status_time = 0
            if agent_status_time > 0:
                td = int(datetime.utcnow().timestamp()) - int(datetime.utcfromtimestamp(agent_status_time).timestamp())
                if td > 86400:
                    self.agents[agent_key][self.wb_status_time] = _('Over a day')
                else:
                    self.agents[agent_key][self.wb_status_time] = '{:02d}:{:02d}:{:02d}'.format(int(td / 3600), int((td / 60) % 60), (td % 60))
            else:
                self.agents[agent_key][self.wb_status_time] = _('Never')

            if agent_status == 'Available':
                self.agents[agent_key][self.wb_status] = _('Waiting')
                self.agents[agent_key][self.wb_colour] = 'ccwb-info'
                agent_state = cache.get('fs:cc:a:%s:agent-state-change' % cct.agent_id.id, b'None').decode()
                if agent_state == 'Receiving':
                    self.trying_count += 1
                    self.agents[agent_key][self.wb_status] = _('Ringing')
                    self.agents[agent_key][self.wb_colour] = self.wb_ccwb_warn
                elif agent_state == 'In+a+queue+call':
                    self.agents[agent_key][self.wb_status] = _('Answered')
                    self.agents[agent_key][self.wb_colour] = self.wb_ccwb_ok
            elif agent_status == 'Logged+Out':
                self.agents[agent_key][self.wb_status] = _('Logged Out')
                self.agents[agent_key][self.wb_colour] = 'ccwb-logged-out'
            else:
                self.agents[agent_key][self.wb_status] = _('On Break')
                self.agents[agent_key][self.wb_colour] = 'ccwb-on-break'
        cache.set('fs:cc:q:%s:agents-list' % self.ccq_id, self.agents)

    def get_queue_detail(self):
        self.queue['id'] = self.ccq_id
        self.queue['token'] = self.token
        self.queue['name'] = self.queue_name
        self.queue['q_date'] = datetime.now().strftime("%d %b %Y")
        self.queue['agent_count'] = _('%s Agents' % str(self.agent_count))
        self.queue['trying'] = str(self.trying_count)
        q_settings = cache.get('fs:cc:q:%s:settings' % self.ccq_id, self.default_q_settings)
        self.queue['settings'] = q_settings
        try:
            waiting = int(cache.get('fs:cc:q:%s:members-count' % self.ccq_id, b'0').decode())
        except ValueError:
            waiting = 0
        if waiting > q_settings['ww'] and waiting <= q_settings['wc']:
            self.queue[self.wb_waiting_colour] = self.wb_ccwb_warn
        elif waiting > q_settings['wc']:
            self.queue[self.wb_waiting_colour] = self.wb_ccwb_crit
        else:
            self.queue[self.wb_waiting_colour] = self.wb_ccwb_ok
        self.queue['waiting'] = str(waiting)
        self.queue['answered'] = cache.get('fs:cc:q:%s:ctrs:answered' % self.ccq_id, b'0').decode()
        try:
            abandoned = int(cache.get('fs:cc:q:%s:ctrs:BREAK_OUT' % self.ccq_id, b'0').decode())
        except ValueError:
            abandoned = 0
        if abandoned > q_settings['aw'] and abandoned <= q_settings['ac']:
            self.queue[self.wb_abandoned_colour] = self.wb_ccwb_warn
        elif abandoned > q_settings['ac']:
            self.queue[self.wb_abandoned_colour] = self.wb_ccwb_crit
        else:
            self.queue[self.wb_abandoned_colour] = self.wb_ccwb_ok
        self.queue['abandoned'] = str(abandoned)


class WbSingleQueueView(LoginRequiredMixin, WbSingleQueueBase):
    template_name = "callcentres/wb_single_queue.html"

    def dispatch(self, request, *args, **kwargs):
        self.ccq_id = kwargs.get('ccq_id')
        self.q = get_object_or_404(CallCentreQueues, pk=self.ccq_id)
        self.queue_name = self.q.name
        self.token = str(uuid.uuid4())
        q_settings = {}
        q_settings['ww'] = self.q.wb_wait_warn_level
        q_settings['wc'] = self.q.wb_wait_crit_level
        q_settings['aw'] = self.q.wb_aban_warn_level
        q_settings['ac'] = self.q.wb_aban_crit_level
        q_settings['sa'] = (1 if self.q.wb_show_agents == 'true' else 0)
        q_settings['apr'] = self.q.wb_agents_per_row

        #  Set cache expire to None (never expire) for these set calls
        cache.set('fs:cc:q:%s:token' % self.ccq_id, self.token, None)
        cache.set('fs:cc:q:%s:name' % self.ccq_id, self.queue_name, None)
        cache.set('fs:cc:q:%s:settings' % self.ccq_id, q_settings, None)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.get_agents_detail()
        self.get_queue_detail()
        data = {'agents': self.agents, 'queue': self.queue}
        return render(request, self.template_name, {'d': data})


class WbSingleQueueJson(WbSingleQueueBase):
    template_name = None

    def dispatch(self, request, *args, **kwargs):
        self.ccq_id = kwargs.get('ccq_id')
        self.gettoken = kwargs.get('token')
        self.queue_name = cache.get('fs:cc:q:%s:name' % self.ccq_id, 'None')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        token = cache.get('fs:cc:q:%s:token' % self.ccq_id)
        if not token == self.gettoken:
            return HttpResponseNotFound()
        agents = cache.get('fs:cc:q:%s:agents-list' % self.ccq_id)
        if agents:
            self.agents = agents
            for key, value in agents.items():
                agent_key = key.replace('_', '-')[1:]
                self.agent_count += 1
                agent_status = cache.get('fs:cc:a:%s:agent-status' % agent_key, b'Logged+Out').decode()
                try:
                    agent_status_time = int(cache.get('fs:cc:a:%s:agent-status-time' % agent_key, b'0').decode())
                    agent_status_time /= 1000000
                except ValueError:
                    agent_status_time = 0
                if agent_status_time > 0:
                    td = int(datetime.utcnow().timestamp()) - int(datetime.utcfromtimestamp(agent_status_time).timestamp())
                    if td > 86400:
                        self.agents[key][self.wb_status_time] = _('Over a day')
                    else:
                        self.agents[key][self.wb_status_time] = '{:02d}:{:02d}:{:02d}'.format(int(td / 3600), int((td / 60) % 60), (td % 60))
                else:
                    self.agents[key][self.wb_status_time] = _('Never')

                if agent_status == 'Available':
                    self.agents[key][self.wb_status] = _('Waiting')
                    self.agents[key][self.wb_colour] = 'ccwb-info'
                    agent_state = cache.get('fs:cc:a:%s:agent-state-change' % agent_key, b'None').decode()
                    if agent_state == 'Receiving':
                        self.trying_count += 1
                        self.agents[key][self.wb_status] = _('Ringing')
                        self.agents[key][self.wb_colour] = self.wb_ccwb_warn
                    elif agent_state == 'In+a+queue+call':
                        self.agents[key][self.wb_status] = _('Answered')
                        self.agents[key][self.wb_colour] = self.wb_ccwb_ok
                elif agent_status == 'Logged+Out':
                    self.agents[key][self.wb_status] = _('Logged Out')
                    self.agents[key][self.wb_colour] = 'ccwb-logged-out'
                else:
                    self.agents[key][self.wb_status] = _('On Break')
                    self.agents[key][self.wb_colour] = 'ccwb-on-break'
        else:
            self.get_agents_detail()
        self.get_queue_detail()
        data = {'agents': self.agents, 'queue': self.queue}
        return JsonResponse(data)


class WbQueueResetCounters(LoginRequiredMixin, View):
    template_name = None

    def dispatch(self, request, *args, **kwargs):
        self.ccq_id = kwargs.get('ccq_id')
        self.q = get_object_or_404(CallCentreQueues, pk=self.ccq_id)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        #  Set cache expire to None (never expire) for these set calls
        cache.set('fs:cc:q:%s:ctrs:answered' % self.ccq_id, b'0', None)
        cache.set('fs:cc:q:%s:ctrs:BREAK_OUT' % self.ccq_id, b'0', None)
        return HttpResponseRedirect('/callcentres/ccqueues/')
