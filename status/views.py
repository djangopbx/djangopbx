#    DjangoPBX
#
#    MIT License
#
#    Copyright (c) 2016 - 2024 Adrian Fretwell <adrian@djangopbx.com>
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
import sys
import json
import datetime
from django.utils.http import urlsafe_base64_decode
from rest_framework import viewsets
from rest_framework import views
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.decorators import action
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.contrib import messages
from pbx.commonfunctions import shcommand, get_version
from pbx.devicecfgevent import DeviceCfgEvent
from pbx.fscmdabslayer import FsCmdAbsLayer
from pbx.restpermissions import (
    AdminApiAccessPermission
)
from switch.models import Modules
from .forms import LogViewerForm
from .serializers import (
    FsRegistrationsSerializer, FsActiveCallsSerializer
)
from accounts.models import Gateway


def parseregdetail(regdetail):
    lines = regdetail.splitlines()
    i = 1
    info = {}
    for line in lines:
        if i > 3 and i < 17:
            if ':' in line:
                data = line.split(':', 1)
                info[data[0]] = data[1].strip()
        i += 1
    return info

def regaction(request, es, action=None, actlist=None):
    if action:
        postaction = action
        if actlist:
            postactlist = [actlist]
        else:
            postactlist = []
    else:
        postaction = request.POST['action']
        postactlist = request.POST.getlist('_selected_action')
    es.clear_responses()
    if postaction == 'unregister':
        for target in postactlist:
            data = target.split('|')
            es.send('api sofia profile %s flush_inbound_reg %s@%s reboot' % (data[2], data[0], data[1]), data[3])
        es.process_events()
        es.get_responses()
        if not action:
            messages.add_message(request, messages.INFO, _('\n'.join(es.responses)))
    else:
        dce = DeviceCfgEvent()
        for target in postactlist:
            data = target.split('|')
            es.send('api sofia status profile %s user %s@%s' % (data[2], data[0], data[1]), data[3])
            es.process_events()
            es.get_responses()
            regdetail = next(iter(es.responses or []), None)
            if regdetail:
                info = parseregdetail(regdetail)
                if 'Agent' in info:
                    cmd = dce.buildevent(data[0], data[1], data[2], postaction, info['Agent'].split()[0].lower())
                    es.send(cmd, data[3])
                    es.process_events()
        if not action:
            messages.add_message(request, messages.INFO, _('Request: %s Sent' % request.POST['action']))
    return

def acaction(request, es, action=None, actlist=None):
    if action:
        postaction = action
        if actlist:
            postactlist = [actlist]
        else:
            postactlist = []
    else:
        postaction = request.POST['action']
        postactlist = request.POST.getlist('_selected_action')
    if not action and len(postactlist) == 0:
        messages.add_message(request, messages.WARNING, _('No records selected.'))
        return
    es.clear_responses()
    if postaction == 'hangup':
        for target in postactlist:
            es.send('api uuid_kill %s' % target)
        es.process_events()
        es.get_responses()
        if not action:
            messages.add_message(request, messages.INFO, _('Hangup %s request sent.' % target))
    return

@staff_member_required
def fslogviewer(request):
    form = LogViewerForm()
    form.fields['logtext'].initial = shcommand(['/usr/local/bin/fslogviewer.sh'])
    form.fields['logtext'].label = 'FreeSWITCH Log (/var/log/freeswitch/freeswitch.log)'
    return render(request, 'status/logviewer.html', {'refresher': 'fslogviewer', 'form': form})


@staff_member_required
def djangopbx(request, host=None):
    links = {}
    info = {}
    info['Version<br>&nbsp;'] = get_version('pbx')
    info['Git Branch'] = shcommand(
        ['/usr/bin/git', '--git-dir=%s/.git' % settings.BASE_DIR, 'name-rev', '--name-only', 'HEAD']
        )
    info['Git Commit'] = shcommand(
        ['/usr/bin/git', '--git-dir=%s/.git' % settings.BASE_DIR, 'rev-parse', 'HEAD']
        )
    git_origin = shcommand(
        ['/usr/bin/git', '--git-dir=%s/.git' % settings.BASE_DIR, 'config', '--get', 'remote.origin.url']
        ).replace('.git', '')
    if '@' in git_origin:
        git_origin = 'https://' + git_origin.split('@')[1]
    info['Git Origin<br>&nbsp;'] = git_origin
    info['Project Path'] = settings.BASE_DIR

    es = FsCmdAbsLayer()
    for ln in es.freeswitches:
        links[ln] = '/status/djangopbx/%s/' % ln
    if not host:
        host = es.freeswitches[0]
    if es.connect():
        es.clear_responses()
        es.send('api version', host)
        es.process_events()
        es.get_responses()
        fs_ver = next(iter(es.responses or []), 'false')
        es.disconnect()
        z = re.match('FreeSWITCH Version (\\d+\\.\\d+\\.\\d+(?:\\.\\d+)?).*\\(.*?(\\d+\\w+)\\s*\\)', fs_ver)
        if z:
            info['Switch Version'] = '%s (%s)' % (z.groups()[0], z.groups()[1])
    info['Python Version'] = sys.version
    return render(request, 'infotable.html', {'refresher': '/status/djangopbx/%s/' % host, 'info': info,
             'title': 'DjangoPBX - %s' % host, 'linkstitle': _('Switches List'), 'links': links})


@staff_member_required
def modules(request, moduuid=None, action=None, host=None):
    links = {}
    info = {}
    th = [_('Module Name'), _('Status'), _('Action'), _('Description')]
    running = _('Running')
    stopped = _('Stopped')
    start = _('Start')
    stop = _('Stop')
    if action == 'stop':
        cmd = 'unload'
    else:
        cmd = 'load'

    es = FsCmdAbsLayer()
    for ln in es.freeswitches:
        links[ln] = '/status/modules/%s/' % ln
    if not host:
        host = es.freeswitches[0]

    if es.connect():
        if moduuid:
            m = Modules.objects.get(pk=moduuid)
            es.clear_responses()
            es.send('api %s %s' % (cmd, m.name), host)
            es.process_events()
            es.get_responses()
            m_status = next(iter(es.responses or []), '-ERR')

            if '+OK' in m_status:
                messages.add_message(request, messages.INFO, _('Module %s OK' % cmd))
            else:
                messages.add_message(request, messages.WARNING, _('Module %s Failed' % cmd))

        mods = Modules.objects.filter(default_enabled='true').order_by('category', 'label')
        for m in mods:
            es.clear_responses()
            es.send('api module_exists %s' % m.name, host)
            es.process_events()
            es.get_responses()
            m_status = next(iter(es.responses or []), 'false')

            if m_status == 'true':
                info[
                    '<a href=\"/admin/switch/modules/%s/change/\">%s</a>' % (str(m.id), m.label)
                    ] = [running, '<a href=\"/status/modules/%s/%s/stop/\">%s</a>' % (str(m.id), host, stop), m.description]
            else:
                info[
                    '<a href=\"/admin/switch/modules/%s/change/\">%s</a>' % (str(m.id), m.label)
                    ] = [stopped, '<a href=\"/status/modules/%s/%s/start/\">%s</a>' % (str(m.id), host, start), m.description]
        es.disconnect()

    return render(
        request, 'infotablemulti.html',
        {'refresher': '/status/modules/%s/' % host, 'info': info, 'th': th,
                'title': 'Modules Status - %s' % host, 'linkstitle': _('Switches List'), 'links': links}
        )


@staff_member_required
def fsregistrations(request, realm=None):
    if not realm:
        realm = request.session['domain_name']
    es = FsCmdAbsLayer()
    if not es.connect():
        return render(request, 'error.html', {'back': '/portal/',
            'info': {'Message': _('Unable to connect to the FreeSWITCH')}, 'title': 'Broker/Socket Error'})

    rows = []
    info = []
    th = ['User', 'LAN IP', 'Network IP', 'Network Port', 'Network Protocol', 'Hostname', 'Expires (Seconds)', 'profile']
    act = {'unregister': 'Un-Register', 'check_sync': 'Provision', 'reboot': 'Reboot'}
    if request.method == 'POST':
        regaction(request, es)
        es.disconnect()
        act = {}
        #  Show empty list to give time for registrations to settle on all freswitches after an action.
        return render(request, 'actiontable.html', {'refresher': 'fsregistrations', 'showall': 'fsregistrations',
                    'info': info, 'th': th, 'act': act, 'title': 'Registrations'})

    unixts = int(datetime.datetime.now().timestamp())
    es.clear_responses()
    es.send('api show registrations as json')
    es.process_events()
    es.get_responses()
    es.disconnect()
    for resp in es.responses:
        try:
            registrations = json.loads(resp)
        except:
            registrations = {'row_count': 0}
        if registrations['row_count'] > 0:
            for i in registrations['rows']:
                if realm == 'all' or realm == i['realm']:
                    sip_profile = i['url'].split('/')[1]
                    sip_user = '%s@%s' % (i['reg_user'], i['realm'])
                    rows.append('%s|%s|%s|%s' % (i['reg_user'], i['realm'], sip_profile, i['hostname']))
                    rows.append('<a href="/status/fsregdetail/%s/%s/%s">%s</a>' % (sip_profile, sip_user, i['hostname'], sip_user))
                    if 'token' in i and '@' in i['token']:
                        rows.append(i['token'].split('@')[1])
                    else:
                        rows.append('')
                    rows.append(i['network_ip'])
                    rows.append(i['network_port'])
                    rows.append(i['network_proto'])
                    rows.append(i['hostname'])
                    rows.append(str(int(i['expires']) - unixts))
                    rows.append(sip_profile)
                    info.append(rows)
                    rows = []
    return render(request, 'actiontable.html', {'refresher': 'fsregistrations', 'showall': 'fsregistrations',
                    'info': info, 'th': th, 'act': act, 'title': 'Registrations'})

@staff_member_required
def fsregdetail(request, sip_profile='internal', sip_user='none@none', host=None):
    info = {}
    es = FsCmdAbsLayer()
    if es.connect():
        es.clear_responses()
        es.send('api sofia status profile %s user %s' % (sip_profile, sip_user), host)
        es.process_events()
        es.get_responses()
        es.disconnect()
        regdetail = next(iter(es.responses or []), None)
        if regdetail:
            info = parseregdetail(regdetail)

    return render(request, 'infotable.html', {'back': 'fsregistrations', 'info': info, 'title': 'Registration Detail'})

def process_active_calls_responses(api, realm, responses):
    nonestr = 'none'
    emptystr = ''
    row = {}
    rows = []
    info = []
    for resp in responses:
        try:
            channels = json.loads(resp)
        except:
            channels = {'row_count': 0}
        if channels['row_count'] > 0:
            for i in channels['rows']:
                context = i.get('context', nonestr)
                presence_id = i.get('presence_id', emptystr)
                if len(context) > 0 and not context == 'public':
                    if '@' in context:
                        context_list = context.split('@')
                        i['domain_name'] = context_list[1]
                    else:
                        i['domain_name'] = context
                elif '@' in presence_id:
                    presence_id_list = presence_id.split('@')
                    i['domain_name'] = presence_id_list[1]
                if realm == 'all' or realm == i.get('domain_name', nonestr):

                    application_data = i.get('application_data', emptystr)
                    if 'gateway' in application_data:
                        application_data_list = application_data.split('/')
                        adll = len(application_data_list)
                        if adll > 1:
                            gateway_uuid = application_data_list[adll - 2]
                            try:
                                gw = Gateway.objects.get(pk=gateway_uuid)
                                gateway_name = gw.gateway
                            except Gateway.DoesNotExist:
                                gateway_name = gateway_uuid

                        application_data = application_data.replace(gateway_uuid, gateway_name)
                    name_list = i.get('name', emptystr).split('/')
                    sip_profile = name_list[1]
                    tmp_number = name_list[2].split('@')[0].replace('sip:', emptystr)
                    cid_num = i.get('cid_num', '').replace('+', emptystr)
                    rows.append(i.get('uuid', emptystr))
                    rows.append(sip_profile)
                    rows.append(i.get('created', emptystr))
                    rows.append(tmp_number)
                    rows.append(i.get('cid_name', emptystr))
                    rows.append(cid_num)
                    rows.append(i.get('dest', emptystr))
                    rows.append('%s:%s' % (i.get('application', emptystr), application_data[:512]))
                    rows.append('%s:%s / %s:%s' % (i.get('read_codec', emptystr), i.get('read_rate',
                                    emptystr), i.get('write_codec', emptystr), i.get('write_rate', emptystr)))
                    rows.append(i.get('secure', emptystr))
                    if api:
                        row['call_uuid'] = rows[0]
                        row['profile'] = rows[1]
                        row['created'] = rows[2]
                        row['number'] = rows[3]
                        row['cid_name'] = rows[4]
                        row['cid_number'] = rows[5]
                        row['dest'] = rows[6]
                        row['application'] = rows[7]
                        row['read_write_codec'] = rows[8]
                        row['secure'] = rows[9]
                        info.append(row)
                        row = {}
                    else:
                        info.append(rows)
                    rows = []
    return info

@staff_member_required
def fsactivecalls(request, realm=None):
    if not realm:
        realm = request.session['domain_name']
    es = FsCmdAbsLayer()
    if not es.connect():
        return render(request, 'error.html', {'back': '/portal/',
            'info': {'Message': _('Unable to connect to the FreeSWITCH')}, 'title': 'Broker/Socket Error'})

    th = ['Profile', 'Created', 'Number', 'CID Name', 'CID Number', 'Dest', 'Application', 'Read / Write Codec', 'Secure']
    act = {'hangup': 'Hangup'}
    if request.method == 'POST':
        acaction(request, es)
        es.disconnect()
        act = {}
        #  Show empty list to give time for data to settle on all freswitches after an action.
        return render(request, 'actiontable.html', {'refresher': 'fsactivecalls', 'showall': 'fsactivecalls',
                    'info': [], 'th': th, 'act': act, 'title': 'Active Calls'})

    es.clear_responses()
    es.send('api show channels as json')
    es.process_events()
    es.get_responses()
    es.disconnect()
    info = process_active_calls_responses(False, realm, es.responses)
    return render(request, 'actiontable.html', {'refresher': 'fsactivecalls', 'showall': 'fsactivecalls',
                    'info': info, 'th': th, 'act': act, 'title': 'Active Calls'})


class FsRegistrationsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Switch Registrations to be viewed.
    """
    action_lookup = {'unregister': 'unregister', 'provision': 'check_sync' , 'reboot': 'reboot'}
    serializer_class = FsRegistrationsSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def get_queryset(self):
        pass

    def list(self, request):
        reg_data = []
        reg_count = 0
        es = FsCmdAbsLayer()
        if not es.connect():
            return Response({'status': 'err', 'message': 'Broker/Socket Error'})
        es.clear_responses()
        es.send('api show registrations as json')
        es.process_events()
        es.get_responses()
        es.disconnect()
        for resp in es.responses:
            try:
                registrations = json.loads(resp)
            except:
                registrations = {'row_count': 0}
            if registrations['row_count'] > 0:
                reg_count += registrations.get('row_count', 0)
                for i in registrations['rows']:
                    if 'registration_uuid' not in i:
                        i['registration_uuid'] = str(uuid.uuid4())
                    reg_data.append(i)
        results = self.serializer_class(reg_data, many=True, context={'request': request}).data
        return Response({'count': reg_count, 'results': results})

    def retrieve(self, request, pk=None):
        if not pk:
            return Response({'status': 'err', 'message': 'pk not found'})
        user, realm, sip_profile, host = urlsafe_base64_decode(pk).decode().split('|')
        sip_user = '%s@%s' % (user, realm)
        es = FsCmdAbsLayer()
        if not es.connect():
            return Response({'status': 'err', 'message': 'Broker/Socket Error'})
        es.clear_responses()
        es.send('api sofia status profile %s user %s' % (sip_profile, sip_user), host)
        es.process_events()
        es.get_responses()
        es.disconnect()
        regdetail = next(iter(es.responses or []), None)
        if regdetail:
            info = parseregdetail(regdetail)
        return Response(info)

    def processregaction(self, request, pk, action=None):
        if not pk:
            return Response({'status': 'err', 'message': 'pk not found'})
        user, realm, sip_profile, host = urlsafe_base64_decode(pk).decode().split('|')
        sip_user = '%s@%s' % (user, realm)
        es = FsCmdAbsLayer()
        if not es.connect():
            return Response({'status': 'err', 'message': 'Broker/Socket Error'})
        regaction(request, es, self.action_lookup[action], urlsafe_base64_decode(pk).decode())
        es.disconnect()
        return Response({'status': '%s %s' % (sip_user, _('%sed' % action.title()))})

    @action(detail=True)
    def reboot(self, request, pk=None):
        return self.processregaction(request, pk, 'reboot')

    @action(detail=True)
    def unregister(self, request, pk=None):
        return self.processregaction(request, pk, 'unregister')

    @action(detail=True)
    def provision(self, request, pk=None):
        return self.processregaction(request, pk, 'provision')


class FsActiveCallsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Switch Active Calls to be viewed.
    """
    serializer_class = FsActiveCallsSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def get_queryset(self):
        pass

    def list(self, request):
        es = FsCmdAbsLayer()
        if not es.connect():
            return Response({'status': 'err', 'message': 'Broker/Socket Error'})
        es.clear_responses()
        es.send('api show channels as json')
        es.process_events()
        es.get_responses()
        channel_data = process_active_calls_responses(True, 'all', es.responses)
        es.disconnect()

        results = self.serializer_class(channel_data, many=True, context={'request': request}).data
        return Response({'count': len(channel_data), 'results': results})

    def retrieve(self, request, pk=None):
        if not pk:
            return Response({'status': 'err', 'message': 'pk not found'})
        return Response({'id': pk, 'call_id': pk})

    @action(detail=True)
    def hangup(self, request, pk=None):
        es = FsCmdAbsLayer()
        if not es.connect():
            return Response({'status': 'err', 'message': 'Broker/Socket Error'})
        acaction(request, es, 'hangup', pk)
        es.disconnect()
        return Response({'status': _('Hangup request sent for call uuid %s' % pk)})
