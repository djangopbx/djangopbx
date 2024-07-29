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
from django.contrib.admin.models import LogEntry
from tenants.models import Domain
from xmlcdr.models import XmlCdr
from pbx.sshconnect import SSHConnection


class Command(BaseCommand):
    help = 'Run Basic Housekeeping'

    def handle(self, *args, **kwargs):
        self.now_time = time.time()
        self.day_sec = 86400
        self.pbxs = PbxSettings()
        self.fs_media = '%s/' % settings.MEDIA_ROOT
        self.use_local_file_storage = settings.PBX_USE_LOCAL_FILE_STORAGE
        if not self.use_local_file_storage:
            self.ssh = SSHConnection()
            self.filestores = settings.PBX_FILESTORES

        if not self.filestores:
            self.filestores = []
        days_keep_call_recordings = self.get_hk_default_setting('days_keep_call_recordings', '30')
        days_keep_voicemail = self.get_hk_default_setting('days_keep_voicemail', '30')
        days_keep_cdrs = self.get_hk_default_setting('days_keep_cdrs', '10')
        days_keep_cdr_json = self.get_hk_default_setting('days_keep_cdr_json', '10', True)
        days_keep_admin_logs = self.get_hk_default_setting('days_keep_admin_logs', '60', True)

        # Set json field empty to save db space
        query_time = timezone.now() - timezone.timedelta(days_keep_cdr_json)
        XmlCdr.objects.filter(start_stamp__lt=query_time).update(json={})

        # Delete Admin log entries
        query_time = timezone.now() - timezone.timedelta(days_keep_admin_logs)
        LogEntry.objects.filter(action_time__lt=query_time).delete()

        qs = Domain.objects.filter(enabled='true')
        for q in qs:
            domain_id = str(q.id)
            domain_days_keep_call_recordings = self.get_hk_domain_setting(domain_id,
                'days_keep_call_recordings', days_keep_call_recordings, True)
            domain_days_keep_voicemail = self.get_hk_domain_setting(domain_id,
                'days_keep_voicemail', days_keep_voicemail, True)
            domain_days_keep_cdrs = self.get_hk_domain_setting(domain_id,
                'days_keep_cdrs', days_keep_cdrs, True)

            # Delete call detail records older x days
            query_time = timezone.now() - timezone.timedelta(domain_days_keep_cdrs)
            XmlCdr.objects.filter(domain_id=q, start_stamp__lt=query_time).delete()

            if self.use_local_file_storage:
                self.hk_delete_files('recordings/%s/archive/*/*/*/*.wav' % q.name, domain_days_keep_call_recordings)
                self.hk_delete_files('recordings/%s/archive/*/*/*/*.mp3' % q.name, domain_days_keep_call_recordings)
                self.hk_delete_files('voicemail/*/%s/*/msg_*.wav' % q.name, domain_days_keep_voicemail)
                self.hk_delete_files('voicemail/*/%s/*/msg_*.mp3' % q.name, domain_days_keep_voicemail)
            else:
                stdin, stdout, stderr = ssh.command(q.name, '/usr/bin/nohup /usr/local/bin/fs-rec-mtce %s voicemailmsg default %s %s &' % (self.fs_media, q.name, domain_days_keep_voicemail))
                for fstr in self.filestores:
                    stdin, stdout, stderr = ssh.command(fstr, '/usr/bin/nohup /usr/local/bin/fs-rec-mtce %s callrecording none %s %s &' % (self.fs_media, q.name, domain_days_keep_call_recordings))

    def hk_delete_files(self, pattern, days):
            files = glob.iglob('%s%s' % (self.fs_media, pattern))
            for f in files:
                if os.stat(f).st_mtime < self.now_time - days * self.day_sec:
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

    def get_hk_domain_setting(self, domain, setting, default, integer=False):
        s = self.pbxs.domain_settings(domain, 'housekeeping',
                setting, 'numeric', default, True)[0]
        if integer:
            try:
                si = int(s)
            except ValueError:
                si = 1000
            return si
        return s
