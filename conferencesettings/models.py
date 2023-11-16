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
import random
from django.utils.translation import gettext_lazy as _
from pbx.commonchoices import EnabledTrueFalseChoice

def random_pin():
    return str(random.randint(10000, 99999))

class ConferenceControlDetails(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Conference Control Details'))                                 # noqa: E501, E221
    conf_ctrl_id = models.ForeignKey('ConferenceControls', on_delete=models.CASCADE, verbose_name=_('Conference Control'))                                              # noqa: E501, E221
    digits       = models.CharField(max_length=8, default='0', verbose_name=_('Digits'))                                                                                # noqa: E501, E221
    action       = models.CharField(max_length=64, default='mute', verbose_name=_('Action'))                                                                            # noqa: E501, E221
    data         = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Data'))                                                                      # noqa: E501, E221
    enabled      = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))  # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                            # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                          # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                        # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Conference Control Details'
        db_table = 'pbx_conference_control_details'

    def __str__(self):
        return self.action


class ConferenceControls(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Conference Controls'))                                        # noqa: E501, E221
    name         = models.CharField(max_length=32, default='new', verbose_name=_('Name'))                                                                               # noqa: E501, E221
    enabled      = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))  # noqa: E501, E221
    description  = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('Description'))                                                               # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                            # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                          # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                        # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Conference Controls'
        db_table = 'pbx_conference_controls'

    def __str__(self):
        return self.name


class ConferenceProfileParams(models.Model):
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Conference Profile Params'))                                  # noqa: E501, E221
    conf_profile_id = models.ForeignKey('ConferenceProfiles', on_delete=models.CASCADE, verbose_name=_('Conference Profile'))                                              # noqa: E501, E221
    name            = models.CharField(max_length=64, default='new', verbose_name=_('Name'))                                                                               # noqa: E501, E221
    value           = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Value'))                                                                     # noqa: E501, E221
    enabled         = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))  # noqa: E501, E221
    description     = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))                                                               # noqa: E501, E221
    created         = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                            # noqa: E501, E221
    updated         = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                # noqa: E501, E221
    synchronised    = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                          # noqa: E501, E221
    updated_by      = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                        # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Conference Profile Params'
        db_table = 'pbx_conference_profile_params'

    def __str__(self):
        return self.name


class ConferenceProfiles(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Conference Profiles'))                                        # noqa: E501, E221
    name         = models.CharField(max_length=32, default='default', verbose_name=_('Name'))                                                                           # noqa: E501, E221
    enabled      = models.CharField(max_length=8, blank=True, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))  # noqa: E501, E221
    description  = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Description'))                                                               # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                            # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                          # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                        # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Conference Profiles'
        db_table = 'pbx_conference_profiles'

    def __str__(self):
        return self.name


class ConferenceCentres(models.Model):
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Conference Centre'))                                                 # noqa: E501, E221
    domain_id    = models.ForeignKey('tenants.Domain', db_column='domain_uuid', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('Domain'))                     # noqa: E501, E221
    name         = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Name'), help_text=_('Enter the Conference Centre Name.'))                            # noqa: E501, E221
    extension    = models.CharField(max_length=32, blank=False, null=False, verbose_name=_('Extension'), help_text=_('Enter the extension number for this Conference Centre')) # noqa: E501, E221
    greeting     = models.CharField(max_length=254, blank=True, null=True, verbose_name=_('Greeting'), help_text=_('Greeting to be played before joining.'))                   # noqa: E501, E221
    enabled      = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))                     # noqa: E501, E221
    description  = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Description'))                                                                       # noqa: E501, E221
    dialplan_id  = models.UUIDField(blank=True, null=True, verbose_name=_('Dialplan UUID'))                                                                                    # noqa: E501, E221
    created      = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                                   # noqa: E501, E221
    updated      = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                                       # noqa: E501, E221
    synchronised = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                                 # noqa: E501, E221
    updated_by   = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                               # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Conference Centres'
        db_table = 'pbx_conference_centres'

    def __str__(self):
        return self.name


class ConferenceRooms(models.Model):
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Conference Rooms'))                                         # noqa: E501, E221
    c_centre_id     = models.ForeignKey('ConferenceCentres', on_delete=models.CASCADE, verbose_name=_('Conference Centre'))                                              # noqa: E501, E221
    name            = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Name'), help_text=_('Enter the Conference Room.'))                          # noqa: E501, E221
    moderator_pin   = models.CharField(max_length=16, default=random_pin, verbose_name=_('Moderator PIN'))                                                             # noqa: E501, E221
    participant_pin = models.CharField(max_length=16, default=random_pin, verbose_name=_('Participant PIN'))                                                           # noqa: E501, E221
    c_profile_id    = models.ForeignKey('ConferenceProfiles', on_delete=models.CASCADE, verbose_name=_('Profile'), help_text=_('This is a collection of settings'))      # noqa: E501, E221
    max_members     = models.DecimalField(max_digits=3, decimal_places=0, default=30, verbose_name=_('Max Members'))                                                     # noqa: E501, E221
    start_time      = models.DateTimeField(blank=True, null=True, verbose_name=_('Schedule from'))                                                                       # noqa: E501, E221
    stop_time       = models.DateTimeField(blank=True, null=True, verbose_name=_('to'))                                                                                  # noqa: E501, E221
    record          = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Record'))            # noqa: E501, E221
    wait_mod        = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Wait for Moderator')) # noqa: E501, E221
    announce        = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Announce'))           # noqa: E501, E221
    sounds          = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Sounds'))            # noqa: E501, E221
    mute            = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CFALSE, verbose_name=_('Mute'))              # noqa: E501, E221
    enabled         = models.CharField(max_length=8, choices=EnabledTrueFalseChoice.choices, default=EnabledTrueFalseChoice.CTRUE, verbose_name=_('Enabled'))            # noqa: E501, E221
    description     = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Description'))                                                              # noqa: E501, E221
    created         = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                          # noqa: E501, E221
    updated         = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                              # noqa: E501, E221
    synchronised    = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                        # noqa: E501, E221
    updated_by      = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                      # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Conference Rooms'
        db_table = 'pbx_conference_rooms'
        unique_together = (('c_centre_id', 'moderator_pin'), ('c_centre_id', 'participant_pin'))

    def __str__(self):
        return self.name


class ConferenceRoomUser(models.Model):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('Conference Room User'))                                    # noqa: E501, E221
    c_room_id     = models.ForeignKey('ConferenceRooms', on_delete=models.CASCADE, verbose_name=_('Conference Room'))                                                 # noqa: E501, E221
    user_uuid     = models.ForeignKey('tenants.Profile', models.SET_NULL, to_field='user_uuid', db_column='user_uuid', blank=True, null=True, verbose_name=_('User')) # noqa: E501, E221
    created       = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Created'))                                                         # noqa: E501, E221
    updated       = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name=_('Updated'))                                                             # noqa: E501, E221
    synchronised  = models.DateTimeField(blank=True, null=True, verbose_name=_('Synchronised'))                                                                       # noqa: E501, E221
    updated_by    = models.CharField(max_length=64, verbose_name=_('Updated by'))                                                                                     # noqa: E501, E221

    class Meta:
        verbose_name_plural = 'Conference Room Users'
        db_table = 'pbx_conference_room_users'

    def __str__(self):
        return str(self.id)
