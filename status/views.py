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

from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.contrib import messages
from pbx.commonfunctions import shcommand, get_version
from pbx.fseventsocket import EventSocket
from pbx.devicecfgevent import DeviceCfgEvent
from .forms import LogViewerForm
from switch.models import Modules
import re
import sys
import json
import datetime


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


@staff_member_required
def fslogviewer(request):
    form = LogViewerForm()
    form.fields['logtext'].initial = shcommand(['/usr/local/bin/fslogviewer.sh'])
    form.fields['logtext'].label = 'FreeSWITCH Log (/var/log/freeswitch/freeswitch.log)'

    return render(request, 'status/logviewer.html', {'refresher': 'fslogviewer', 'form': form})


@staff_member_required
def djangopbx(request):
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

    es = EventSocket()
    if es.connect(*settings.EVSKT):
        fs_ver = es.send('api version')
        z = re.match('FreeSWITCH Version (\\d+\\.\\d+\\.\\d+(?:\\.\\d+)?).*\\(.*?(\\d+\\w+)\\s*\\)', fs_ver)
        info['Switch Version'] = '%s (%s)' % (z.groups()[0], z.groups()[1])
    info['Python Version'] = sys.version

    return render(request, 'infotable.html', {'refresher': 'djangopbx', 'info': info, 'title': 'DjangoPBX'})


@staff_member_required
def modules(request, moduuid=None, action=None):
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

    es = EventSocket()
    if es.connect(*settings.EVSKT):
        if moduuid:
            m = Modules.objects.get(pk=moduuid)
            m_status = es.send('api %s %s' % (cmd, m.name))
            if '+OK' in m_status:
                messages.add_message(request, messages.INFO, _('Module %s OK' % cmd))
            else:
                messages.add_message(request, messages.WARNING, _('Module %s Failed' % cmd))

        mods = Modules.objects.filter(enabled='true').order_by('category', 'label')
        for m in mods:
            m_status = es.send('api module_exists %s' % m.name)
            if m_status == 'true':
                info[
                    '<a href=\"/admin/switch/modules/%s/change/\">%s</a>' % (str(m.id), m.label)
                    ] = [running, '<a href=\"/status/modules/%s/stop/\">%s</a>' % (str(m.id), stop), m.description]
            else:
                info[
                    '<a href=\"/admin/switch/modules/%s/change/\">%s</a>' % (str(m.id), m.label)
                    ] = [stopped, '<a href=\"/status/modules/%s/start/\">%s</a>' % (str(m.id), start), m.description]

    return render(
        request, 'infotablemulti.html',
        {'refresher': 'modules', 'info': info, 'th': th, 'title': 'Modules Status'}
        )


@staff_member_required
def fsregistrations(request, realm=None):
    if not realm:
        realm = request.session['domain_name']
    es = EventSocket()
    if not es.connect(*settings.EVSKT):
        return render(request, 'error.html', {'back': '/portal/', 'info': {'Message': _('Unable to connect to the FreeSWITCH Event Socket')}, 'title': 'Event Socket Error'})

    if request.method == 'POST':
        actlist = request.POST.getlist('_selected_action')
        if request.POST['action'] == 'unregister':
            for target in actlist:
                data = target.split('|')
                result = es.send('api sofia profile %s flush_inbound_reg %s@%s reboot' % (data[2], data[0], data[1]))

            messages.add_message(request, messages.INFO, _(result))
        else:
            dce = DeviceCfgEvent()
            for target in actlist:
                data = target.split('|')
                regdetail =  es.send('api sofia status profile %s user %s@%s' % (data[2], data[0], data[1]))
                if regdetail:
                    info = parseregdetail(regdetail)
                    if 'Agent' in info:
                        cmd = dce.buildevent(data[0], data[1], data[2], request.POST['action'], info['Agent'].split()[0].lower())
                        es.send(cmd)
            messages.add_message(request, messages.INFO, _('Request: %s Sent' % request.POST['action']))

    rows = []
    info = []
    th = ['User', 'LAN IP', 'Network IP', 'Network Port', 'Network Protocol', 'Hostname', 'Expires (Seconds)', 'profile']
    act = {'unregister': 'Un-Register', 'check_sync': 'Provision', 'reboot': 'Reboot'}

    unixts = int(datetime.datetime.now().timestamp())
    registrations = json.loads(es.send('api show registrations as json'))
    if registrations['row_count'] > 0:    
        for i in registrations['rows']:
            if realm == 'all' or realm == i['realm']:
                sip_profile = i['url'].split('/')[1]
                sip_user = '%s@%s' % (i['reg_user'], i['realm'])
                rows.append('%s|%s|%s' % (i['reg_user'], i['realm'], sip_profile))
                rows.append('<a href="/status/fsregdetail/%s/%s">%s</a>' % (sip_profile, sip_user, sip_user))
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
    return render(request, 'actiontable.html', {'refresher': 'fsregistrations', 'showall': 'fsregistrations', 'info': info, 'th': th, 'act': act, 'title': 'Registrations'})


@staff_member_required
def fsregdetail(request, sip_profile=None, sip_user=None):
    info = {}
    es = EventSocket()
    if es.connect(*settings.EVSKT):
        regdetail = es.send('api sofia status profile %s user %s' % (sip_profile, sip_user))
    if regdetail:
        info = parseregdetail(regdetail)

    return render(request, 'infotable.html', {'back': 'fsregistrations', 'info': info, 'title': 'Registration Detail'})

