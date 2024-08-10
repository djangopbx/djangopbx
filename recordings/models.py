#
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

from django.conf import settings
from django.core.files.storage import storages
from django.db import models

from django.utils.translation import gettext_lazy as _
import uuid
from pbx.commonwidgets import PbxFileField


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/fs/recordings/<domain name>/<filename>
    return 'fs/recordings/{0}/{1}'.format(instance.domain_id.name, filename)

def call_recording_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/fs/recordings/<domain name>/<filename>
    return 'fs/recordings/{0}/archive/{1}/{2}/{3}/{4}'.format(instance.domain_id.name,
                    instance.year, instance.month, instance.day, filename)

def select_storage():
    return storages['default'] if settings.PBX_USE_LOCAL_FILE_STORAGE else storages['sftp']

def default_filestore():
    return settings.PBX_FILESTORES[settings.PBX_DEFAULT_FILESTORE]

class Recording(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Recording'))                                      # noqa: E501, E221
    domain_id    = models.ForeignKey('tenants.Domain', db_column='domain_uuid', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))  # noqa: E501, E221
    filename     = PbxFileField(storage=select_storage, upload_to=user_directory_path, verbose_name=_('File Name'))                                         # noqa: E501, E221
    name         = models.CharField(max_length=64, verbose_name=_('Name'))                                                                                  # noqa: E501, E221
    description  = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Description'))                                                   # noqa: E501, E221
    filestore    = models.CharField(max_length=128, default=default_filestore, verbose_name=_('Filestore'))                                                 # noqa: E501, E221
    base64       = models.TextField(blank=True, null=True, verbose_name=_('Base64'))                                                                        # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                    # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                              # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                            # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Recordings'
        db_table = 'pbx_recordings'
        permissions = (
            ("can_download_recording", "can_download_recording"),
            ("can_upload_recording", "can_upload_recording"),
            ("can_play_recording", "can_play_recording")
            )

    def __str__(self):
        return self.name


class CallRecording(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Call Recording'))                                 # noqa: E501, E221
    domain_id    = models.ForeignKey('tenants.Domain', db_column='domain_uuid', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))  # noqa: E501, E221
    filename     = PbxFileField(storage=select_storage, upload_to=call_recording_directory_path, verbose_name=_('File Name'))                               # noqa: E501, E221
    name         = models.CharField(max_length=64, verbose_name=_('Name'))                                                                                  # noqa: E501, E221
    year         = models.CharField(max_length=8, verbose_name=_('Year'))                                                                                   # noqa: E501, E221
    month        = models.CharField(max_length=8, verbose_name=_('Month'))                                                                                  # noqa: E501, E221
    day          = models.CharField(max_length=8, verbose_name=_('Day'))                                                                                    # noqa: E501, E221
    description  = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Description'))                                                   # noqa: E501, E221
    filestore    = models.CharField(max_length=128, default=default_filestore, verbose_name=_('Filestore'))                                                 # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                    # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                              # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                            # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Call Recordings'
        db_table = 'pbx_call_recordings'
        permissions = (
            ("can_download_call_recording", "can_download_call_recording"),
            ("can_upload_call_recording", "can_upload_call_recording"),
            ("can_play_call_recording", "can_play_call_recording")
            )

    def __str__(self):
        return self.name
