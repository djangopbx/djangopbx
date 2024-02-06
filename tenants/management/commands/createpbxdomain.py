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


import sys
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand

from tenants.models import Domain, DomainSetting, Profile
from dialplans.dialplanfunctions import SwitchDp


class Command(BaseCommand):
    help = 'Create a Domain'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--domain', help=_('Domain name (--domain domain1.djangopbx.uk)'))
        parser.add_argument('-u', '--user', help=_('Assign domain to user (--user 1001)'))

    def handle(self, *args, **kwargs):
        d = kwargs.get('domain', '')
        if not d:
            print(_('No domain specified'))
            sys.exit(1)

        u = kwargs.get('user', '')
        if u:
            try:
                u = int(u)
            except ValueError:
                u = False
        else:
            u = False

        if Domain.objects.filter(name=d).exists():
            print(_('Domain: %s exists' % d))
            sys.exit(2)
        dom = Domain.objects.create(
            name=d,
            enabled='true',
            updated_by='system'
            )
        SwitchDp().import_xml(dom.name, False, dom.id)  # Create dialplans
        DomainSetting.objects.create(
            domain_id=dom,   # Create default menu setting
            category='domain',
            subcategory='menu',
            value_type='text',
            value='Default',
            sequence=10,
            updated_by='system'
            )

        if u:
            try:
                p = Profile.objects.get(user_id=u)
            except Profile.DoesNotExist:
                p = None

            if p:
                p.domain_id = dom
                p.save()
