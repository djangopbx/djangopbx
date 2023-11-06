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

from python_ipware import IpWare
from django.core.cache import cache
from tenants.pbxsettings import PbxSettings
from portal.models import Failed_logins
from .commonfunctions import shcommand


class IpFunctions():

    def __init__(self):
        self.ipw = IpWare()
        self.ipw = IpWare(precedence=(
            "X_FORWARDED_FOR",  # Load balancers or proxies such as AWS ELB (default client is `left-most` [`<client>, <proxy1>, <proxy2>`])
            "HTTP_FORWARDED_FOR",  # RFC 7239
            "HTTP_FORWARDED",  # RFC 7239
            "X-REAL-IP",  # NGINX
            "FORWARDED_FOR",  # RFC 7239
            "FORWARDED",  # RFC 7239
            "REMOTE_ADDR",  # Default
        ))
        self.pbxsettings = PbxSettings()

    def get_portal_ignore_fail_address(self):
        cache_key = 'portal:ignore_fail_address'
        ia = cache.get(cache_key)
        if ia:
            ignore_addresses = ia.split(',')
        else:
            ignore_addresses = self.pbxsettings.default_settings('portal', 'ignore_fail_address', 'array')
            ia = ','.join(ignore_addresses)
            cache.set(cache_key, ia)
        return ignore_addresses

    def get_portal_fail_attempts(self):
        max_fail_attempts = 5
        cache_key = 'portal:fail_attempts'
        fa = cache.get(cache_key)
        if not fa:
            fa = self.pbxsettings.default_settings('portal', 'max_fail_attempts', 'numeric', '5', True)[0]
            cache.set(cache_key, fa)
        try:
            max_fail_attempts = int(fa)
        except ValueError:
            max_fail_attempts = 5

        return max_fail_attempts

    def update_web_fail_ip(self, ip_address, username):
        ignore_addresses = self.get_portal_ignore_fail_address()
        if ip_address in ignore_addresses:
            return

        ip, created = Failed_logins.objects.update_or_create(address=ip_address)
        ip.username = username[:250]
        if not created:
            max_fail_attempts = self.get_portal_fail_attempts()
            i = ip.attempts + 1
            ip.attempts = i
            if i > max_fail_attempts:
                if ':' in ip.address:
                    shcommand(["/usr/local/bin/fw-add-ipv6-web-block-list.sh", ip.address])
                else:
                    shcommand(["/usr/local/bin/fw-add-ipv4-web-block-list.sh", ip.address])
        ip.save()
        return

    def get_client_ip(self, meta):
        ip, trusted_route = self.ipw.get_client_ip(meta)
        if ip:
            return(format(ip))
        return False
