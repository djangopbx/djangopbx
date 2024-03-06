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

import os, time
import glob
from django.conf import settings
from django.utils import timezone
from django.core.management.base import BaseCommand
from tenants.pbxsettings import PbxSettings
from pbx.commonfunctions import shcommand


class Command(BaseCommand):
    help = 'Backup files'

    def handle(self, *args, **kwargs):
        now_time = time.time()
        day_sec = 86400
        now = timezone.now().strftime('%Y%m%d')
        self.pbxs = PbxSettings()
        backup_dir = '/home/django-pbx/pbx-backups/files'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        backup_file = os.path.join(backup_dir, 'djangopbx_files_%s.tgz' % now)
        shcommand(['/usr/bin/tar',
                    '--exclude=/var/lib/freeswitch/recordings/*/archive',
                    '--exclude=/home/django-pbx/media/fs/recordings/*/archive',
                    '--exclude=__pycache__',
                    '--exclude=*.log',
                    '-zvcf',
                    backup_file,
                    '/home/django-pbx/media/fs',
                    '/usr/share/freeswitch/scripts',
                    '/var/lib/freeswitch/storage',
                    '/var/lib/freeswitch/vm_db',
                    '/var/lib/freeswitch/recordings',
                    '/home/django-pbx/pbx',
                    '/home/django-pbx/freeswitch',
                    '/usr/share/freeswitch/sounds/music'
                    ])

        with open(os.path.join(backup_dir, 'djangopbx_files_latest.txt'), 'w') as latest:
            latest.write('%s\n' % backup_file)

        days_keep_file_backups = self.get_hk_default_setting('days_keep_file_backups', '5', True)
        files = glob.iglob('%s/*.tgz' % backup_dir )
        for f in files:
            if os.stat(f).st_mtime < now_time - days_keep_file_backups * day_sec:
                os.remove(f)

    def get_hk_default_setting(self, setting, default, integer=False):
        s = self.pbxs.default_settings('housekeeping',
                setting, 'numeric', default, True)[0]
        if integer:
            try:
                si = int(s)
            except ValueError:
                si = 1000
            return si
        return s
