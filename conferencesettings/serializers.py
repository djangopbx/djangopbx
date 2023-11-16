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

from rest_framework import serializers
from .models import (
    ConferenceControls, ConferenceControlDetails, ConferenceProfiles, ConferenceProfileParams,
    ConferenceRoomUser, ConferenceRooms, ConferenceCentres,
)


class ConferenceControlsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConferenceControls
        fields = [
                    'url', 'id', 'name', 'enabled', 'description',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class ConferenceControlDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConferenceControlDetails
        fields = [
                    'url', 'id', 'conf_ctrl_id', 'digits', 'action', 'data', 'enabled',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class ConferenceProfilesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConferenceProfiles
        fields = [
                    'url', 'id', 'name', 'enabled', 'description',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class ConferenceProfileParamsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConferenceProfileParams
        fields = [
                    'url', 'id', 'conf_profile_id', 'name', 'value', 'enabled', 'description',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class ConferenceCentresSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConferenceCentres
        fields = [
                    'url', 'id', 'domain_id', 'name', 'extension', 'greeting',
                    'enabled', 'description', 'dialplan_id',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class ConferenceRoomsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConferenceRooms
        fields = [
                    'url', 'id', 'c_centre_id', 'name', 'c_profile_id', 
                    'moderator_pin', 'participant_pin',
                    'max_members', 'start_time', 'stop_time',
                    'record', 'wait_mod', 'announce', 'sounds', 'mute',
                    'enabled', 'description',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class ConferenceRoomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConferenceRoomUser
        fields = [
                    'url', 'id', 'c_room_id', 'user_uuid',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]
