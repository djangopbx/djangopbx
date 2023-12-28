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

from django.utils import timezone
from .models import IpRegister
from pbx.commonfunctions import shcommand


class IpRegisterFunctions():

    def process_data(self, qs, cmd):
        i = 0
        ips = []
        for q in qs:
            i += 1
            if i > 99:
                shcommand([cmd, ','.join(ips)])
                ips.clear()
            ips.append(q.address)
        shcommand([cmd, ','.join(ips)])

    def reinstate_fw_sip_customer_list(self):
        qs = IpRegister.objects.raw('select id, address from pbx_ip_register where status=1 and family(address)=4 order by address')
        if qs:
            self.process_data(qs, '/usr/local/bin/fw-add-ipv4-sip-customer-list.sh')
        qs = IpRegister.objects.raw('select id, address from pbx_ip_register where status=1 and family(address)=6 order by address')
        if qs:
            self.process_data(qs, '/usr/local/bin/fw-add-ipv6-sip-customer-list.sh')

    def obsolete_old_ip_addresses(self):
        time_24_hours_ago = timezone.now() - timezone.timedelta(1)
        IpRegister.objects.filter(status=1, updated__lte=time_24_hours_ago).update(status=0)

