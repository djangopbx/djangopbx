#
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

import uuid
from django.db import models
from django.conf import settings
from django.core.files.storage import storages
from django.utils.translation import gettext_lazy as _
from pbx.commonwidgets import PbxFileField


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/fs/music/<moh name>/<rate>/<filename>
    return 'fs/music/{0}/{1}/{2}'.format(instance.moh_id, instance.moh_id.rate, filename)

def select_storage():
    return storages['default'] if settings.PBX_USE_LOCAL_FILE_STORAGE else storages[settings.PBX_REMOTE_FILE_STORAGE_TYPE] # noqa: E501

def default_filestore():
    return settings.PBX_FILESTORES[settings.PBX_DEFAULT_FILESTORE]


class MusicOnHold(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Music On Hold'))                                 # noqa: E501, E221
    domain_id    = models.ForeignKey('tenants.Domain', db_column='domain_uuid', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain')) # noqa: E501, E221
    name         = models.CharField(max_length=32, default='default', verbose_name=_('Name'))                                                              # noqa: E501, E221
    path         = models.CharField(max_length=256, default='$${sounds_dir}/music/default/', verbose_name=_('Path'))                                       # noqa: E501, E221
    rate         = models.DecimalField(max_digits=11, decimal_places=0, default=8000, verbose_name=_('Rate'))                                              # noqa: E501, E221
    shuffle      = models.CharField(max_length=8, default='true', verbose_name=_('Shuffle'))                                                               # noqa: E501, E221
    channels     = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True, verbose_name=_('Channels'))                                 # noqa: E501, E221
    interval     = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True, verbose_name=_('Interval'))                                 # noqa: E501, E221
    timer_name   = models.CharField(max_length=32, default='soft', verbose_name=_('Timer Name'))                                                           # noqa: E501, E221
    chime_list   = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Chime List'))                                                    # noqa: E501, E221
    chime_freq   = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True, verbose_name=_('Chime Frequency'))                          # noqa: E501, E221
    chime_max    = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True, verbose_name=_('Chime Max.'))                               # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                               # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                   # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                             # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                           # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Music On Hold'
        db_table = 'pbx_music_on_hold'

    def __str__(self):
        return self.name


class MohFile(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Recording')) # noqa: E501, E221
    moh_id       = models.ForeignKey('MusicOnHold', on_delete=models.CASCADE, verbose_name=_('Hold Music'))            # noqa: E501, E221
    filename     = PbxFileField(storage=select_storage, upload_to=user_directory_path, verbose_name=_('File Name'))    # noqa: E501, E221
    file_name    = models.CharField(max_length=256, verbose_name=_('Name'))                                            # noqa: E501, E221
    filestore    = models.CharField(max_length=128, default=default_filestore, verbose_name=_('Filestore'))            # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))           # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))               # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                         # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                       # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'MOH Files'
        db_table = 'pbx_music_on_hold_files'
        permissions = (
            ("can_download_file", "can_download_file"),
            ("can_upload_file", "can_upload_file"),
            ("can_play_file", "can_play_file")
            )

    def __str__(self):
        return str(self.id)
