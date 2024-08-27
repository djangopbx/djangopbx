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
from django.conf import settings
from django.core.files.storage import storages
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.validators import MinValueValidator
from pbx.commonwidgets import PbxFileField
from pbx.commonchoices import EnabledTrueFalseChoice


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/fs/voicemail/default/<domain name>/<id>/<filename>
    return 'fs/voicemail/default/{0}/{1}/{2}'.format(
            instance.voicemail_id.extension_id.domain_id.name,
            instance.voicemail_id.extension_id.extension,
            filename
            )

def select_storage():
    return storages['default'] if settings.PBX_USE_LOCAL_FILE_STORAGE else storages['sftp']

def default_filestore():
    return settings.PBX_FILESTORES[settings.PBX_DEFAULT_FILESTORE]

class VmAttachFileChoice(models.TextChoices):
    CFALSE = 'false', _('None')                  # noqa: E221
    CTRUE  = 'true',  _('Audio file attachment') # noqa: E221
    CLINK  = 'link',  _('Download link')         # noqa: E221


class Voicemail(models.Model):
    id                    = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Voicemail'))                                                      # noqa: E501, E221
    extension_id          = models.ForeignKey('accounts.Extension', related_name='voicemail', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Extension'))          # noqa: E501, E221
    password              = models.CharField(max_length=16, blank=True, null=True, verbose_name=_('Password'))                                                                       # noqa: E501, E221
    greeting_id           = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True, default=1, verbose_name=_('Greeting ID'), validators=[MinValueValidator(1)])  # noqa: E501, E221
    alternate_greeting_id = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True, verbose_name=_('Alternate Greeting ID'), validators=[MinValueValidator(1)])   # noqa: E501, E221
    mail_to               = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Mail to'))                                                                       # noqa: E501, E221
    sms_to                = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('SMS to'))                                                                         # noqa: E501, E221
    cc                    = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('CC'))                                                                             # noqa: E501, E221
    attach_file           = models.CharField(max_length=8, blank=True, choices=VmAttachFileChoice.choices, default=VmAttachFileChoice.CTRUE, verbose_name=_('Attach file'))          # noqa: E501, E221
    local_after_email     = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Keep Local'))   # noqa: E501, E221
    enabled               = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))      # noqa: E501, E221
    description           = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Description'))                                                                   # noqa: E501, E221
    created               = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                # noqa: E501, E221
    updated               = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                    # noqa: E501, E221
    synchronised          = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                              # noqa: E501, E221
    updated_by            = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                            # noqa: E501, E221

    class Meta:
        db_table = 'pbx_voicemails'

    def __str__(self):
        return str(self.extension_id)


class VoicemailGreeting(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Recording'))           # noqa: E501, E221
    voicemail_id = models.ForeignKey('Voicemail', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Voicemail'))  # noqa: E501, E221
    filename     = PbxFileField(storage=select_storage, upload_to=user_directory_path, verbose_name=_('File Name'))              # noqa: E501, E221
    name         = models.CharField(max_length=64, verbose_name=_('Name'))                                                       # noqa: E501, E221
    description  = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Description'))                        # noqa: E501, E221
    filestore    = models.CharField(max_length=128, default=default_filestore, verbose_name=_('Filestore'))                      # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                     # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                         # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                   # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                 # noqa: E501, E221

    class Meta:
        db_table = 'pbx_voicemail_greetings'
        permissions = (
            ("can_download_greeting", "can_download_greeting"),
            ("can_upload_greeting", "can_upload_greeting"),
            ("can_play_greeting", "can_play_greeting")
            )

    def __str__(self):
        return self.name

class VoicemailMessages(models.Model):
    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Message'))             # noqa: E501, E221
    voicemail_id     = models.ForeignKey('Voicemail', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Voicemail'))  # noqa: E501, E221
    filename         = PbxFileField(storage=select_storage, upload_to=user_directory_path, verbose_name=_('File Name'))              # noqa: E501, E221
    name             = models.CharField(max_length=64, verbose_name=_('Name'))                                                       # noqa: E501, E221
    filestore        = models.CharField(max_length=128, default=default_filestore, verbose_name=_('Filestore'))                      # noqa: E501, E221
    caller_id_name   = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Caller ID Name'))                      # noqa: E501, E221
    caller_id_number = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Caller ID Number'))                    # noqa: E501, E221
    duration         = models.DecimalField(max_digits=32, decimal_places=0, default=0, verbose_name=_('Duration'))                   # noqa: E501, E221
    status           = models.CharField(max_length=64, default='new', verbose_name=_('Status'))                                      # noqa: E501, E221
    read             = models.DateTimeField(blank=True, null=True, verbose_name=_('Read Date'))                                      # noqa: E501, E221
    transcription    = models.TextField(blank=True, null=True, verbose_name=_('Transcription'))                                      # noqa: E501, E221
    base64           = models.TextField(blank=True, null=True, verbose_name=_('Base64'))                                             # noqa: E501, E221
    created          = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                     # noqa: E501, E221
    updated          = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                         # noqa: E501, E221
    synchronised     = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                   # noqa: E501, E221
    updated_by       = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                 # noqa: E501, E221

    class Meta:
        db_table = 'pbx_voicemail_messages'
        permissions = (
            ("can_download_message", "can_download_message"),
            ("can_upload_message", "can_upload_message"),
            ("can_play_message", "can_play_message")
            )

    def __str__(self):
        return self.name

class VoicemailOptions(models.Model):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Voicemail Option'))       # noqa: E501, E221
    voicemail_id  = models.ForeignKey('Voicemail', on_delete=models.CASCADE, verbose_name=_('Voicemail'))                            # noqa: E501, E221
    option_digits = models.CharField(max_length=8, blank=True, null=True, default='1', verbose_name=_('Option'))                     # noqa: E501, E221
    option_action = models.CharField(max_length=64, blank=True, null=True, default='menu-exec-app', verbose_name=_('Option Action')) # noqa: E501, E221
    option_param  = models.CharField(max_length=128, blank=False, null=False, verbose_name=_('Destination'))                         # noqa: E501, E221
    sequence      = models.DecimalField(max_digits=3, decimal_places=0, default=0, verbose_name=_('Order'))                          # noqa: E501, E221
    description   = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Description'))                            # noqa: E501, E221
    created       = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                        # noqa: E501, E221
    updated       = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                            # noqa: E501, E221
    synchronised  = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                      # noqa: E501, E221
    updated_by    = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                    # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Voicemail Options'
        db_table = 'pbx_voicemail_options'

    def __str__(self):
        return str(self.id)

class VoicemailDestinations(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Recording')) # noqa: E501, E221
    voicemail_id   = models.ForeignKey('Voicemail', on_delete=models.CASCADE, verbose_name=_('Voicemail'))               # noqa: E501, E221
    voicemail_dest = models.UUIDField(blank=True, null=True, verbose_name=_('Destination'))                              # noqa: E501, E221
    created        = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))           # noqa: E501, E221
    updated        = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))               # noqa: E501, E221
    synchronised   = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                         # noqa: E501, E221
    updated_by     = models.CharField(max_length=64, verbose_name=_('Updated by'))                                       # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Voicemail Destinations'
        db_table = 'pbx_voicemail_destinations'
