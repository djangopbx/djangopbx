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
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.validators import MinValueValidator
from pbx.commonwidgets import PbxFileField
from pbx.commonchoices import EnabledTrueFalseChoice


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/fs/voicemail/<domain name>/<id>/<filename>
    return 'fs/voicemail/default/{0}/{1}/{2}'.format(instance.voicemail_id.extension_id.domain_id.name, instance.voicemail_id.extension_id.extension, filename)


class Voicemail(models.Model):
    id                    = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Voicemail'))
    extension_id           = models.ForeignKey('accounts.Extension', related_name='voicemail', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Extension'))
    password              = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Password'))
    greeting_id           = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True, default=1, verbose_name=_('Greeting ID'), validators=[MinValueValidator(1)])
    alternate_greeting_id = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True, verbose_name=_('Alternate Greeting ID'), validators=[MinValueValidator(1)])
    mail_to               = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Mail to'))
    sms_to                = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('SMS to'))
    cc                    = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('CC'))
    attach_file           = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Attach file'))
    local_after_email     = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Keep Local'))
    enabled               = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))
    description           = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Description'))
    created               = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated               = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised          = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by            = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        db_table = 'pbx_voicemails'

    def __str__(self):
        return str(self.extension_id)


class VoicemailGreeting(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Recording'))
    voicemail_id = models.ForeignKey('Voicemail', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Voicemail'))
    filename     = PbxFileField(upload_to=user_directory_path, verbose_name=_('File Name'))
    name         = models.CharField(max_length=64, verbose_name=_('Name'))
    description  = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Description'))
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))

    class Meta:
        db_table = 'pbx_voicemail_greetings'
        permissions = (("can_download_greeting", "can_download_greeting"), ("can_upload_greeting", "can_upload_greeting"), ("can_play_greeting", "can_play_greeting"))

    def __str__(self):
        return self.name

