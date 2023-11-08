#
#    DjangoPBX
#
#    MIT License
#
#    Copyright (c) 2016 - 2023 Adrian Fretwell <adrian@djangopbx.com>
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

from django.utils.translation import gettext_lazy as _
from pbx.commonchoices import EnabledTrueFalseChoice


class IvrMenus(models.Model):
    id                  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('IVR Menu'))                                                                                                 # noqa: E501, E221
    domain_id           = models.ForeignKey('tenants.Domain', db_column='domain_uuid', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))                                                            # noqa: E501, E221
    dialplan_id         = models.UUIDField(blank=True, null=True, verbose_name=_('Dialplan UUID'))                                                                                                                           # noqa: E501, E221
    name                = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Name'), help_text=_('Enter a name'))                                                                                        # noqa: E501, E221
    extension           = models.CharField(max_length=32, blank=False, null=False, verbose_name=_('Extension'), help_text=_('Enter the extension number for this menu'))                                                     # noqa: E501, E221
    language            = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Language'))                                                                                                                 # noqa: E501, E221
    greet_long          = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Greeting Long'), help_text=_('The long greeting is played when entering the menu'))                                        # noqa: E501, E221
    greet_short         = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Greeting Short'), help_text=_('The short greeting is played when returning to the menu'))                                  # noqa: E501, E221
    invalid_sound       = models.CharField(max_length=254, blank=True, null=True, default='ivr/ivr-that_was_an_invalid_entry.wav', verbose_name=_('Invalid Sound'), help_text=_('Played when and invalid option is chosen')) # noqa: E501, E221
    exit_sound          = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Exit Sound'))                                                                                                              # noqa: E501, E221
    confirm_macro       = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Confirm Macro'), help_text=_('Enter the confirm macro'))                                                                   # noqa: E501, E221
    confirm_key         = models.CharField(max_length=8, blank=True, null=True, verbose_name=_('Confirm Key'), help_text=_('Enter the confirm key'))                                                                         # noqa: E501, E221
    tts_engine          = models.CharField(max_length=64, blank=True, null=True, default='flite', verbose_name=_('TTS Engine'), help_text=_('Text to speech engine'))                                                        # noqa: E501, E221
    tts_voice           = models.CharField(max_length=254, blank=True, null=True, default='rms', verbose_name=_('TTS Voice'), help_text=_('Text to speech voice'))                                                           # noqa: E501, E221
    confirm_attempts    = models.DecimalField(max_digits=2, decimal_places=0, default=1, verbose_name=_('Confirm Attempts'), help_text=_('The maximum number of confirm attempts allowed'))                                  # noqa: E501, E221
    timeout             = models.DecimalField(max_digits=5, decimal_places=0, default=3000, verbose_name=_('Timeout'), help_text=_('The number of milliseconds to wait after playing the greeting or the confirm macro'))    # noqa: E501, E221
    exit_app            = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('Exit App.'))                                                                                                                # noqa: E501, E221
    exit_data           = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Exit Action'), help_text=_('Select the exit action to be performed if the IVR exits.'))                                    # noqa: E501, E221
    inter_digit_timeout = models.DecimalField(max_digits=5, decimal_places=0, default=2000, verbose_name=_('Inter-Digit Timeout'), help_text=_('The number of milliseconds to wait between digits'))                         # noqa: E501, E221
    max_failiures       = models.DecimalField(max_digits=2, decimal_places=0, default=1, verbose_name=_('Max Failiures'), help_text=_('Maximum number of retries before exit'))                                              # noqa: E501, E221
    max_timeouts        = models.DecimalField(max_digits=2, decimal_places=0, default=1, verbose_name=_('Max Timeouts'), help_text=_('Maximum number of timeouts before exit'))                                              # noqa: E501, E221
    digit_len           = models.DecimalField(max_digits=2, decimal_places=0, default=5, verbose_name=_('Digit Length'), help_text=_('Maximum number of digits allowed'))                                                    # noqa: E501, E221
    direct_dial         = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Drect Dial'))                                                        # noqa: E501, E221
    ringback            = models.CharField(max_length=128, blank=True, null=True, verbose_name=_('Ring Back'), help_text=_('Defines what the caller will hear while the destination is being called'))                       # noqa: E501, E221
    cid_prefix          = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('CID Name Prefix'), help_text=_('Set a prefix on the caller ID name'))                                                       # noqa: E501, E221
    context             = models.CharField(max_length=128, db_index=True, blank=True, null=True, verbose_name=_('Context'), help_text=_('Enter the context'))                                                                # noqa: E501, E221
    enabled             = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))                                                            # noqa: E501, E221
    description         = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Description'))                                                                                                              # noqa: E501, E221
    created             = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                                                          # noqa: E501, E221
    updated             = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                                                              # noqa: E501, E221
    synchronised        = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                                                        # noqa: E501, E221
    updated_by          = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                                                                      # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'IVR Menus'
        db_table = 'pbx_ivr_menus'

    def __str__(self):
        return f'{self.extension}->{self.name}'


class IvrMenuOptions(models.Model):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('IVR Menu Option'))        # noqa: E501, E221
    ivr_menu_id   = models.ForeignKey('IvrMenus', on_delete=models.CASCADE, verbose_name=_('IVR Menu'))                              # noqa: E501, E221
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
        verbose_name_plural = 'IVR Menu Options'
        db_table = 'pbx_ivr_menu_options'

    def __str__(self):
        return str(self.id)
