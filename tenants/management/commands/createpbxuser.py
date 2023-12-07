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

from tenants.models import Domain, Profile
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = 'Create a User'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--domain', help=_('Domain name (--domain domain1.djangopbx.com)'))
        parser.add_argument('-u', '--username', help=_('User name (eg. 201@djangopbx.com)'))
        parser.add_argument('-p', '--password', help=_('Password'))
        parser.add_argument('-f', '--firstname', help=_('First Name'))
        parser.add_argument('-l', '--lastname', help=_('First Name'))
        parser.add_argument('-e', '--email', help=_('Email'))

    def handle(self, *args, **kwargs):
        d = kwargs.get('domain', '')
        if not d:
            print(_('No domain specified'))
            sys.exit(1)

        u = kwargs.get('username', '')
        if not u:
            print(_('No username specified'))
            sys.exit(1)

        p = kwargs.get('password', '')
        if not d:
            print(_('No password specified'))
            sys.exit(1)

        f = kwargs.get('firstname', '')
        l = kwargs.get('lastname', '')
        e = kwargs.get('email', '')

        try:
            dom = Domain.objects.filter(name=d).first()
        except Domain.DoesNotExist:
            print(_('Domain doesnot exist'))
            sys.exit(1)

        if User.objects.filter(username=u).exists():
            print(_('User already exists'))
            sys.exit(1)
        else:
            user = User.objects.create_user(u, e, p)
            user.first_name = f
            user.last_name = l
            user.save()
            user_group = Group.objects.get(name='user')
            if user_group:
                user_group.user_set.add(user)
            user.profile.domain_id = dom
            user.profile.username = u
            user.profile.enabled = 'true'
            user.profile.updated_by = 'system'
            user.profile.save()
