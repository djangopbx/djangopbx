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

import os
from django.conf import settings
from pbx.sshconnect import SFTPConnection
from .models import Voicemail, VoicemailGreeting


class VoicemailFunctions():
    sftp = None
    voicemail_path = 'fs/voicemail/default'

    def create_vm_record(self, extobj, updated_by):
        try:
            v = Voicemail.objects.create(
                extension_id=extobj,
                enabled='false',
                updated_by=updated_by
            )
        except:
            return None
        return v


    def init_sftp(self):
        if not self.sftp:
            self.sftp = SFTPConnection()

    def sync_greetings(self, domain_uuid):
        qs = Voicemail.objects.filter(enabled='true', extension_id__domain_id_id=domain_uuid)
        if qs:
            q = qs[0]
            home_switch = q.extension_id.domain_id.home_switch
            domain_name = q.extension_id.domain_id.name
        if settings.PBX_FREESWITCH_LOCAL:
            for q in qs:
                self.sync_greetings_with_local_fs(q, domain_name)
        else:
            self.init_sftp()
            try:
                 self.sftp.exists(home_switch, settings.MEDIA_ROOT) # Tests if host is reachable, abort otherwise.
            except:
                return False
            for q in qs:
                self.sync_greetings_with_remote_fs(q, domain_name, home_switch)
        return True

    def sync_greetings_with_local_fs(self, vm, domain_name):
        grtg = vm.voicemailgreeting_set.all()
        for q in grtg:
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, q.filename.name.lstrip('/'))):
                q.delete()
        path = os.path.join(settings.MEDIA_ROOT, self.voicemail_path, domain_name, vm.extension_id.extension)
        storage_path = os.path.join(self.voicemail_path, domain_name, vm.extension_id.extension)
        if os.path.exists(path):
            with os.scandir(path) as it:
                for f in it:
                    if f.is_file():
                        if f.name.startswith('greeting_'):
                            vmg, created = VoicemailGreeting.objects.get_or_create(
                                voicemail_id=vm,
                                filename=os.path.join(storage_path, f.name),
                                defaults={'name': f.name, 'updated_by': 'Voicemail Directory Scan'}
                                )

    def sync_greetings_with_remote_fs(self, vm, domain_name, home_switch):
        grtg = vm.voicemailgreeting_set.all()
        for q in grtg:
            if not self.sftp.exists(home_switch, os.path.join(settings.MEDIA_ROOT, q.filename.name.lstrip('/'))):
                q.delete()
        path = os.path.join(settings.MEDIA_ROOT, self.voicemail_path, domain_name, vm.extension_id.extension)
        storage_path = os.path.join(self.voicemail_path, domain_name, vm.extension_id.extension)
        if self.sftp.exists(home_switch, path):
            dirs, files = self.sftp.listdir(home_switch, path)
            for f in files:
                if f.startswith('greeting_'):
                    vmg, created = VoicemailGreeting.objects.get_or_create(
                        voicemail_id=vm,
                        filename=os.path.join(storage_path, f),
                        defaults={'name': f, 'updated_by': 'Voicemail Remote Directory Scan'}
                        )
