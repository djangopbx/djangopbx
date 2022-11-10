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

from django.db import models

import uuid
from django.utils.translation import gettext_lazy as _
from pbx.commonwidgets import PbxFileField


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/fs/music/<moh name>/<rate>/<filename>
    return 'fs/music/{0}/{1}/{2}'.format(instance.moh_id, instance.moh_id.rate, filename)


class MusicOnHold(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Music On Hold'))
    domain_id  = models.ForeignKey('tenants.Domain', db_column='domain_uuid', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))
    name       = models.CharField(max_length=32, default='default', verbose_name=_('Name'))
    path       = models.CharField(max_length=256, default='$${sounds_dir}/music/default/', verbose_name=_('Path'))
    rate       = models.DecimalField(max_digits=11, decimal_places=0, default=8000, verbose_name=_('Rate'))
    shuffle    = models.CharField(max_length=8, default='true', verbose_name=_('Shuffle'))
    channels   = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True, verbose_name=_('Channels'))
    interval   = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True, verbose_name=_('Interval'))
    timer_name = models.CharField(max_length=32, default='soft', verbose_name=_('Timer Name'))
    chime_list = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Chime List'))
    chime_freq = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True, verbose_name=_('Chime Frequency'))
    chime_max  = models.DecimalField(max_digits=11, decimal_places=0, blank=True, null=True, verbose_name=_('Chime Max.'))
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        verbose_name_plural = 'Music On Hold'
        db_table = 'pbx_music_on_hold'

    def __str__(self):
        return self.name


class MohFile(models.Model):
    id        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Recording'))
    moh_id    = models.ForeignKey('MusicOnHold', on_delete=models.CASCADE, verbose_name=_('Hold Music'))
    filename  = PbxFileField(upload_to=user_directory_path, verbose_name=_('File Name'))
    file_name = models.CharField(max_length=256, verbose_name=_('Name'))
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        verbose_name_plural = 'MOH Files'
        db_table = 'pbx_music_on_hold_files'
        permissions = (("can_download_file", "can_download_file"), ("can_upload_file", "can_upload_file"), ("can_play_file", "can_play_file"))

    def __str__(self):
        return str(self.id)
