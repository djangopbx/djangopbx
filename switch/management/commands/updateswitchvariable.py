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


import sys
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from switch.models import SwitchVariable


class Command(BaseCommand):
    help = 'Update a Switch Variable'

    def add_arguments(self, parser):
        parser.add_argument('--category', help=_('Variable Category'))
        parser.add_argument('--name', help=_('Variable Name'))
        parser.add_argument('--value', help=_('The value for the Variable'))

    def handle(self, *args, **kwargs):
        cat = kwargs.get('category')
        if not cat:
            print(_('No category specified'))
            sys.exit(1)

        name = kwargs.get('name')
        if not name:
            print(_('No variable name specified'))
            sys.exit(1)

        value = kwargs.get('value')
        if not value:
            print(_('No value specified'))
            sys.exit(1)

        try:
            v = SwitchVariable.objects.get(enabled='true', category=cat, name=name)
        except SwitchVariable.DoesNotExist:
                print(_('Variable does not exist, or is not enabled'))
                sys.exit(1)

        v.value = value
        v.save()
