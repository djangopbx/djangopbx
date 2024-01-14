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

import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps


class Command(BaseCommand):
    help = 'Load default menu'

    def add_arguments(self, parser):
        parser.add_argument('-r', '--remove', help=_('Remove existing default menu (--remove true)'))

    def handle(self, *args, **kwargs):
        menu_remove = False
        r = kwargs['remove']
        if not r:
            r = 'false'

        if r == 'true':
            menu_remove = True

        if menu_remove:
            pass
            # remove not yet implemented

        portal_path = apps.get_app_config('portal').path

        defaults_file = '%s/fixtures/defaultmenu.json' % portal_path
        loaded_file = '%s/fixtures/defaultmenu.loaded' % portal_path
        if not os.path.exists(loaded_file):
            if os.path.exists(defaults_file):
                print('Loading Menu for: %s' % defaults_file)
                call_command('loaddata', defaults_file, verbosity=0)
                Path(loaded_file).touch()

        defaults_file = '%s/fixtures/defaultmenudata.json' % portal_path
        loaded_file = '%s/fixtures/defaultmenudata.loaded' % portal_path
        if not os.path.exists(loaded_file):
            if os.path.exists(defaults_file):
                print('Loading Menu for: %s' % defaults_file)
                call_command('loaddata', defaults_file, verbosity=0)
                Path(loaded_file).touch()

        defaults_file = '%s/fixtures/defaultmenuitemgroup.json' % portal_path
        loaded_file = '%s/fixtures/defaultmenuitemgroup.loaded' % portal_path
        if not os.path.exists(loaded_file):
            if os.path.exists(defaults_file):
                print('Loading Menu for: %s' % defaults_file)
                call_command('loaddata', defaults_file, verbosity=0)
                Path(loaded_file).touch()

        for acnf in apps.get_app_configs():
            if acnf.name == 'portal':
                continue
            if not hasattr(acnf, 'pbx_uuid'):
                continue

            defaults_file = '%s/fixtures/%s/defaultmenudata.json' % (acnf.path, acnf.name)
            loaded_file = '%s/fixtures/%s/defaultmenudata.loaded' % (acnf.path, acnf.name)
            if os.path.exists(loaded_file):
                continue
            if os.path.exists(defaults_file):
                print('Loading Menu for: %s' % defaults_file)
                call_command('loaddata', defaults_file, verbosity=0)
                Path(loaded_file).touch()
