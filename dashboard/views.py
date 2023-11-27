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

from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaulttags import register
from django.conf import settings
from django.utils import timezone

import datetime
import platform
import distro
import os
import multiprocessing
import psutil
from psutil._common import bytes2human
import time
from pbx.fseventsocket import EventSocket
from pbx.commonvalidators import clean_uuid4_list

from tenants.models import Domain, Profile
from provision.models import Devices
from accounts.models import Extension, Gateway
from dialplans.models import Dialplan
from callcentres.models import CallCentreQueues
from ivrmenus.models import IvrMenus
from ringgroups.models import RingGroup
from voicemail.models import Voicemail
from xmlcdr.models import XmlCdr


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_item_humanize(dictionary, key):
    return intcomma(dictionary.get(key))


class OsDashboard():
    hostname = ''
    osname = ''
    kernel = ''
    cpucount = ''
    cpus = 0
    cpuusage = ''
    cpuall = ''
    cputype = ''
    load1 = ''
    load5 = ''
    load15 = ''
    mem = {}
    nettotalbytessent = ''
    nettotalbytesrecv = ''
    nettotalpacketssent = ''
    nettotalpacketsrecv = ''
    nic = {}
    disks = {}
    diskio = {}

#    hostname = ''

    def __init__(self):
        self.get_cpus()
        self.get_cpu_usage()
        self.uptime = self.get_uptime()
        self.cpus = self.get_cpus()
        self.get_platform()
        self.get_mem()
        self.get_traffic()
        self.get_disks()
        self.get_diskio()

    def get_cpus(self):
        try:
            pipe = os.popen("cat /proc/cpuinfo |" + "grep 'model name'")
            data = pipe.read().strip().split(':')[-1]
            pipe.close()

            if not data:
                pipe = os.popen("cat /proc/cpuinfo |" + "grep 'Processor'")
                data = pipe.read().strip().split(':')[-1]
                pipe.close()

            cpus = multiprocessing.cpu_count()
            self.cpucount = str(cpus)
            self.cpus = cpus
            self.cputype = data
            data = {'cpus': cpus, 'type': data}

        except Exception as err:
            data = str(err)
        return data

    def get_cpu_usage(self):
        try:
            # Getting load over5 minutes
            load1, load5, load15 = psutil.getloadavg()
            cpu_usage = (load5/os.cpu_count()) * 100
            load1, load5, load15 = [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]
            self.load1 = str(round(load1, 2))
            self.load5 = str(round(load5, 2))
            self.load15 = str(round(load15, 2))

            self.cpuall = psutil.cpu_percent(interval=0.5, percpu=True)
            # i = 1
            # for cpu in cpu_all:
            #    self.cpuall += '<>'str(i) + ': ' + str(cpu) + ' '
            #    i += 1
            self.cpuusage = str(round(cpu_usage, 2))
            data = {'used': cpu_usage}

        except Exception as err:
            data = str(err)
        return data

    def get_platform(self):
        try:
            osname = ''
            for item in distro.linux_distribution(full_distribution_name=False):
                osname += item + ' '
            self.osname = osname
            uname = platform.uname()
            self.hostname = uname[1]
            self.kernel = uname[2]

            data = {'osname': osname, 'hostname': uname[1], 'kernel': uname[2]}

        except Exception as err:
            data = str(err)
        return data

    def get_uptime(self):
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                uptime_time = str(datetime.timedelta(seconds=uptime_seconds))
                data = uptime_time.split('.', 1)[0]

        except Exception as err:
            data = str(err)
        return data

    def get_mem(self):
        try:
            nt = psutil.virtual_memory()
            for name in nt._fields:
                value = getattr(nt, name)
                if name != 'percent':
                    value = bytes2human(value)
                self.mem[name.capitalize()] = value

            data = self.mem

        except Exception as err:
            data = str(err)
        return data

    def get_traffic(self):
        try:
            pnic_before = psutil.net_io_counters(pernic=True)
            # sleep some time
            time.sleep(1)
            tot_all = psutil.net_io_counters()
            pnic_after = psutil.net_io_counters(pernic=True)

            self.nettotalbytessent = bytes2human(tot_all.bytes_sent)
            self.nettotalbytesrecv = bytes2human(tot_all.bytes_recv)
            self.nettotalpacketssent = intcomma(tot_all.packets_sent)
            self.nettotalpacketsrecv = intcomma(tot_all.packets_recv)
            nic_names = list(pnic_after.keys())
            nic_names.sort(key=lambda x: sum(pnic_after[x]), reverse=True)
            for name in nic_names:
                stats_before = pnic_before[name]
                stats_after = pnic_after[name]
                self.nic[name] = {
                                'bytessent': bytes2human(stats_after.bytes_sent),
                                'bytesrecv': bytes2human(stats_after.bytes_recv),
                                'bytesendrate': bytes2human(stats_after.bytes_sent - stats_before.bytes_sent),
                                'byterecvrate': bytes2human(stats_after.bytes_recv - stats_before.bytes_recv),
                                'packetssent': bytes2human(stats_after.packets_sent),
                                'packetsrecv': bytes2human(stats_after.packets_recv),
                                'packetsendrate': bytes2human(stats_after.packets_sent - stats_before.packets_sent),
                                'packetrecvrate': bytes2human(stats_after.packets_recv - stats_before.packets_recv),
                                }

            data = self.nic
        except Exception as err:
            data = str(err)
        return data

    def get_disks(self):
        try:
            for part in psutil.disk_partitions(all=False):
                usage = psutil.disk_usage(part.mountpoint)

                self.disks[part.device] = {
                            'total': bytes2human(usage.total),
                            'used': bytes2human(usage.used),
                            'free': bytes2human(usage.free),
                            'use': usage.percent,
                            'type': part.fstype,
                            'mount': part.mountpoint
                            }

            data = self.disks
        except Exception as err:
            data = str(err)
        return data

    def get_diskio(self):
        try:
            disk_io = psutil.disk_io_counters()
            self.diskio = {
                            'Read Count': intcomma(disk_io.read_count),
                            'Write Count': intcomma(disk_io.write_count),
                            'Read Bytes': bytes2human(disk_io.read_bytes),
                            'Write Bytes': bytes2human(disk_io.write_bytes),
                            'Read Time': intcomma(disk_io.read_time),
                            'Write Time': intcomma(disk_io.write_time),
                            'Read Merged Count': intcomma(disk_io.read_merged_count),
                            'Write Merged Count': intcomma(disk_io.write_merged_count),
                            'Busy Time': intcomma(disk_io.busy_time)
                        }

            data = self.diskio
        except Exception as err:
            data = str(err)
        return data

class SwDashboard():
    s = 0.001
    esconnected = False
    sw_counts = {}
    sw_live = {}
    sw_status = []
    sw_status_title = ''

    def __init__(self):
        self.es = EventSocket()
        if self.es.connect(*settings.EVSKT):
            self.esconnected = True
        self.get_config_counts()
        self.get_sw_status()
        self.get_live_counts()

    def get_live_counts(self):
        if not self.esconnected:
            return
        result = self.es.send('api show calls count')
        time.sleep(self.s)
        if result:
            self.sw_live['Calls'] = {'c': result.replace(' total.', '')}
        result = self.es.send('api show channels count')
        time.sleep(self.s)
        if result:
            self.sw_live['Channels'] = {'c': result.replace(' total.', '')}
        result = self.es.send('api show registrations count')
        time.sleep(self.s)
        if result:
            self.sw_live['Registrations'] = {'c': result.replace(' total.', '')}


    def get_config_counts(self):
        self.sw_counts['Destinations'] = {}
        self.sw_counts['Destinations']['t'] = Dialplan.objects.filter(category='Inbound route').count()
        self.sw_counts['Destinations']['e'] = Dialplan.objects.filter(category='Inbound route', enabled='true').count()
        self.sw_counts['Devices'] = {}
        self.sw_counts['Devices']['t'] = Devices.objects.all().count()
        self.sw_counts['Devices']['e'] = Devices.objects.filter(enabled='true').count()
        self.sw_counts['Domains'] = {}
        self.sw_counts['Domains']['t'] = Domain.objects.all().count()
        self.sw_counts['Domains']['e'] = Domain.objects.filter(enabled='true').count()
        self.sw_counts['Extensions'] = {}
        self.sw_counts['Extensions']['t'] = Extension.objects.all().count()
        self.sw_counts['Extensions']['e'] = Extension.objects.filter(enabled='true').count()
        self.sw_counts['Gateways'] = {}
        self.sw_counts['Gateways']['t'] = Gateway.objects.all().count()
        self.sw_counts['Gateways']['e'] = Gateway.objects.filter(enabled='true').count()
        self.sw_counts['Users'] = {}
        self.sw_counts['Users']['t'] = Profile.objects.all().count()
        self.sw_counts['Users']['e'] = Profile.objects.filter(enabled='true').count()
        self.sw_counts['CC Queues'] = {}
        self.sw_counts['CC Queues']['t'] = CallCentreQueues.objects.all().count()
        self.sw_counts['CC Queues']['e'] = CallCentreQueues.objects.filter(enabled='true').count()
        self.sw_counts['IVR Menus'] = {}
        self.sw_counts['IVR Menus']['t'] = IvrMenus.objects.all().count()
        self.sw_counts['IVR Menus']['e'] = IvrMenus.objects.filter(enabled='true').count()
        self.sw_counts['Ring Groups'] = {}
        self.sw_counts['Ring Groups']['t'] = RingGroup.objects.all().count()
        self.sw_counts['Ring Groups']['e'] = RingGroup.objects.filter(enabled='true').count()
        self.sw_counts['Voicemails'] = {}
        self.sw_counts['Voicemails']['t'] = Voicemail.objects.all().count()
        self.sw_counts['Voicemails']['e'] = Voicemail.objects.filter(enabled='true').count()

    def get_sw_status(self):
        self.sw_status = []
        if self.esconnected:
            result = self.es.send('api show status')
            time.sleep(self.s)
        if result:
            lines = result.splitlines()
            for line in lines:
                if 'UP' in line:
                    pts = line.split(',')
                    self.sw_status.append('%s, %s, %s, %s, %s' % (pts[0].replace(' years', 'y'),
                            pts[1].replace(' days', 'd'), pts[2].replace(' hours', 'h'),
                            pts[3].replace(' minutes', 'm'), pts[4].replace(' seconds', 's')))
                    self.sw_status_title = '%s:%s:%s:%s' % (pts[0].replace(' years', '').replace('UP ', ''),
                            pts[1].replace(' days', ''), pts[2].replace(' hours', ''),
                            pts[3].replace(' minutes', ''))
                    self.sw_status_title = self.sw_status_title.replace(' ', '')
                else:
                    self.sw_status.append(line)


class UsrDashboard():
    s = 0.001
    esconnected = False
    c_dict = {}
    c_count = 0
    missed = {}
    missed_count = 0
    recent = {}
    recent_count = 0
    vm = {}
    vm_count = 0
    callrouting = {}
    ringgroup = {}
    callrouting_visible = False
    ringgroup_visible = False

    call_dir = {
                'inbound': '<i class=\"fa fa-arrow-circle-down\"></i>',
                'outbound': '<i class=\"fa fa-arrow-circle-up\"></i>',
                'local': '<i class=\"fa fa-arrow-circle-right\"></i>'
                }

    cr_flags = {
                'true': '<i class=\"fa fa-check\"></i>',
                'false': '<i class=\"fa fa-times\"></i>',
                }

    def __init__(self, request):
        self.request = request
        self.es = EventSocket()
        self.extnuuids = self.request.session['extension_list_uuid'].split(',')
        clean_uuid4_list(self.extnuuids)
        self.extns = self.request.session['extension_list'].split(',')
        self.time_24_hours_ago = timezone.now() - timezone.timedelta(1)
        if self.es.connect(*settings.EVSKT):
            self.esconnected = True
        self.get_recent_calls()
        self.get_missed_calls()
        self.get_voicemails()
        self.get_call_routing()
        self.get_ring_group()
        self.groupList = list(request.user.groups.values_list('name', flat=True))

    def get_recent_calls(self):
        qs = XmlCdr.objects.filter(domain_id=self.request.session['domain_uuid'],
            extension_id__in=self.extnuuids, end_stamp__gte=self.time_24_hours_ago,
            hangup_cause='NORMAL_CLEARING').order_by('-start_stamp', 'extension_id')
        self.get_calls(qs)
        self.recent_count = self.c_count
        self.recent = self.c_dict

    def get_missed_calls(self):
        qs = XmlCdr.objects.filter(domain_id=self.request.session['domain_uuid'],
            extension_id__in=self.extnuuids, end_stamp__gte=self.time_24_hours_ago).exclude(
            hangup_cause='NORMAL_CLEARING').exclude(direction='outbound').order_by('-start_stamp', 'extension_id')
        self.get_calls(qs)
        self.missed_count = self.c_count
        self.missed = self.c_dict

    def get_calls(self, qs):
        self.c_dict = {}
        count = 0
        for q in qs:
            count += 1
            if count > 24:
                continue
            self.c_dict[str(q.id)] = {}
            self.c_dict[str(q.id)]['dir'] = self.call_dir[q.direction]
            self.c_dict[str(q.id)]['dest'] = q.caller_destination
            self.c_dict[str(q.id)]['time'] = q.start_stamp.strftime('%m/%d %H:%M')
        self.c_count = count

    def get_voicemails(self):
        info = {}
        count = 0
        for e in self.extns:
            info[e] = {}
            info[e]['count'] = 0
            vmstr = self.es.send('api vm_list %s@%s' % (e, self.request.session['domain_name']))
            if '-ERR no reply' in vmstr:
                info[e]['msg'] = _('No Voicemail Messages')
            else:
                vmlist = vmstr.split('\n')
                for vm in vmlist:
                    count += 1
                    parts = vm.split(':')
                    info[e]['count'] += 1
        self.vm = info
        self.vm_count = count

    def get_call_routing(self):
        self.callrouting = {}
        extension_list = self.request.session['extension_list_uuid'].split(',')
        clean_uuid4_list(extension_list)
        if self.request.user.is_superuser:
            self.callrouting_visible = True
            qs = Extension.objects.filter(domain_id=self.request.session['domain_uuid']).order_by('extension')[:10]
        else:
            qs = Extension.objects.filter(domain_id=self.request.session['domain_uuid'],
                    extension_id__in=extension_list).order_by('extension')[:10]
            if 'call_routing' in self.groupList:
                self.callrouting_visible = True
        for q in qs:
            self.callrouting[q.extension] = {}
            self.callrouting[q.extension]['id'] = str(q.id)
            self.callrouting[q.extension]['cf'] = self.cr_flags[q.forward_all_enabled]
            self.callrouting[q.extension]['fm'] = self.cr_flags[q.follow_me_enabled]
            self.callrouting[q.extension]['dnd'] = self.cr_flags[q.do_not_disturb]
            self.callrouting[q.extension]['desc'] = q.description

    def get_ring_group(self):
        self.ringgroup = {}
        if self.request.user.is_superuser:
            self.ringgroup_visible = True
            qs = RingGroup.objects.filter(domain_id=self.request.session['domain_uuid']).order_by('extension')[:10]
        else:
            qs = RingGroup.objects.filter(domain_id=self.request.session['domain_uuid'],
                        ringgroupuser__user_uuid=self.request.session['user_uuid']).order_by('extension')[:10]
            if 'ringgroup_fwd' in self.groupList:
                self.ringgroup_visible = True
        for q in qs:
            self.ringgroup[q.extension] = {}
            self.ringgroup[q.extension]['id'] = str(q.id)
            self.ringgroup[q.extension]['name'] = q.name
            self.ringgroup[q.extension]['fwd'] = self.cr_flags[q.forward_enabled]
            self.ringgroup[q.extension]['dest'] = (q.forward_destination if q.forward_destination else '')


@staff_member_required
def osdashboard(request):
    dash = OsDashboard()
    return render(request, 'dashboard/osdashboard.html', {'d': dash})


@staff_member_required
def swdashboard(request):
    dash = SwDashboard()
    if dash.esconnected:
        return render(request, 'dashboard/swdashboard.html', {'d': dash})
    else:
        return render(request, 'error.html', {'back': '/portal/', 'info': {'Message': _('Unable to connect to the FreeSWITCH Event Socket')}, 'title': 'Event Socket Error'})


@login_required
def usrdashboard(request):
    dash = UsrDashboard(request)
    if dash.esconnected:
        return render(request, 'dashboard/usrdashboard.html', {'d': dash})
    else:
        return render(request, 'error.html', {'back': '/portal/', 'info': {'Message': _('Unable to connect to the Event Socket')}, 'title': 'Event Socket Error'})
