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
from django.http import HttpResponse, HttpResponseNotFound
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from django_tables2 import Table, SingleTableView, LazyPaginator
from django.utils.html import format_html
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _


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
        return format_html('<a href=\"/callcentres/wbsinglequeue/{}/\">{}</a>', record.id, value)



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


class WbSingleQueueBase(View):
    wb_status = 'wb_status'
    wb_colour = 'wb_colour'
    wb_status_time = 'status_time'
    wb_ccwb_ok = 'ccwb-ok'
    wb_ccwb_warn = 'ccwb-warn'
    wb_ccwb_crit = 'ccwb-crit'
    wb_abandoned_colour = 'abandoned_colour'
    wb_waiting_colour = 'waiting_colour'

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
        try:
            waiting = int(cache.get('fs:cc:q:%s:members-count' % self.ccq_id, b'0').decode())
        except ValueError:
            waiting = 0
        if waiting > 5:
            self.queue[self.wb_waiting_colour] = self.wb_ccwb_warn
        elif waiting > 10:
            self.queue[self.wb_waiting_colour] = self.wb_ccwb_crit
        else:
            self.queue[self.wb_waiting_colour] = self.wb_ccwb_ok
        self.queue['waiting'] = str(waiting)
        self.queue['answered'] = cache.get('fs:cc:q:%s:ctrs:answered' % self.ccq_id, b'0').decode()
        try:
            abandoned = int(cache.get('fs:cc:q:%s:ctrs:BREAK_OUT' % self.ccq_id, b'0').decode())
        except ValueError:
            abandoned = 0
        if abandoned > 5:
            self.queue[self.wb_abandoned_colour] = self.wb_ccwb_warn
        elif abandoned > 10:
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
        #  Set cache expire to None (never expire) for these set calls
        cache.set('fs:cc:q:%s:token' % self.ccq_id, self.token, None)
        cache.set('fs:cc:q:%s:name' % self.ccq_id, self.queue_name, None)
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
