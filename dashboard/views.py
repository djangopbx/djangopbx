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
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaulttags import register

from datetime import timedelta
import platform
import distro
import os
import multiprocessing
import psutil
from psutil._common import bytes2human
import time

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
            #i = 1
            #for cpu in cpu_all:
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
                uptime_time = str(timedelta(seconds=uptime_seconds))
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
            tot_before = psutil.net_io_counters()
            pnic_before = psutil.net_io_counters(pernic=True)
            # sleep some time
            time.sleep(1)
            tot_after = psutil.net_io_counters()
            pnic_after = psutil.net_io_counters(pernic=True)

            self.nettotalbytessent = bytes2human(tot_after.bytes_sent)
            self.nettotalbytesrecv = bytes2human(tot_after.bytes_recv)
            self.nettotalpacketssent = intcomma(tot_after.packets_sent)
            self.nettotalpacketsrecv = intcomma(tot_after.packets_recv)
            nic_names = list(pnic_after.keys())
            nic_names.sort(key=lambda x: sum(pnic_after[x]), reverse=True)
            for name in nic_names:
                stats_before = pnic_before[name]
                stats_after = pnic_after[name]
                self.nic[name] = {'bytessent': bytes2human(stats_after.bytes_sent),
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

                self.disks[part.device] = {'total': bytes2human(usage.total),
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
            self.diskio = {'Read Count': intcomma(disk_io.read_count),
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


@staff_member_required
def osdashboard(request):

    #uptime = get_uptime()
    dash = OsDashboard()
    #print(dash.get_cpus())
    return render(request, 'dashboard/osdashboard.html', {'d': dash})
