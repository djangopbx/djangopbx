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

from datetime import datetime
from django.core.cache import cache
from django.views import View
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django_tables2 import Table, SingleTableView, LazyPaginator
from django.utils.html import format_html
from django.shortcuts import get_object_or_404

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


class WbSingleQueueView(View):
    template_name = "callcentres/wb_single_queue.html"

    def dispatch(self, request, *args, **kwargs):
        self.cache_key = 'callcentres:agents'
        self.queue = get_object_or_404(CallCentreQueues, pk=kwargs['ccq_id'])
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        agents = {}
        data = {'agents': agents, 'queue': {}}
        ccts = CallCentreTiers.objects.filter(queue_id=self.queue.id)
        agent_count = 0;
        for cct in ccts:
            agent_count += 1
            agents[str(cct.agent_id.id)] = {'name': cct.agent_id.name}
            agents[str(cct.agent_id.id)]['status'] = cache.get('fs:cc:a:%s:agent-status' % cct.agent_id.id, 'logged out')
            agents[str(cct.agent_id.id)]['status-time'] = cache.get('fs:cc:a:%s:agent-status-time' % cct.agent_id.id, 0)

        cache.set(self.cache_key, agents)
        data['queue']['name'] = self.queue.name
        data['queue']['q_date'] = datetime.now().strftime("%d %b %Y")
        data['queue']['agent_count'] = str(agent_count)
        data['queue']['members-count'] = cache.get('fs:cc:q:%s:members-count' % self.queue.id, b'0').decode()
        data['queue']['answered'] = cache.get('fs:cc:q:%s:ctrs:answered' % self.queue.id, b'0').decode()
        data['queue']['abandoned'] = cache.get('fs:cc:q:%s:ctrs:BREAK_OUT' % self.queue.id, b'0').decode()

        print(data)
        return render(request, self.template_name, {'d': data})


class WbSingleQueueJson(View):

    def dispatch(self, request, *args, **kwargs):
        self.cache_key = 'callcentres:agents'
        self.ccq_id = kwargs['ccq_id']

    def get(self, request, *args, **kwargs):
        agents = cache.get(cache_key)
        if not agents:
            ccts = CallCentreTiers.objects.filter(queue_id=self.ccq_id)
            for cct in ccts:
                agents[str(cct.agent_id.id)] = cct.agent_id.name
            cache.set(self.cache_key, agents)

        data = {}
        return HttpResponse(data, mimetype='application/json')
