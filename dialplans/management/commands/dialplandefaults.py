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


from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand

from tenants.pbxsettings import PbxSettings
from dialplans.dialplanfunctions import SwitchDp

class Command(BaseCommand):
    help = 'Load default dialplans'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--domain', help=_('Domain name (--domain domain1.djangopbx.uk)'))
        parser.add_argument('-r', '--remove', help=_('Remove existing dialplans (--remove true)'))

    def handle(self, *args, **kwargs):
        dp_remove = False
        d = kwargs['domain']
        if not d:
            d = ''

        r = kwargs['remove']
        if not r:
            r = 'false'

        if r == 'true':
            dp_remove = True

        if len(d) == 0:
            domains_dict = PbxSettings().get_domains()
            for domain in domains_dict:
                for key in domain:
                    SwitchDp().import_xml(key, dp_remove)
        else:
            SwitchDp().import_xml(d, dp_remove)

