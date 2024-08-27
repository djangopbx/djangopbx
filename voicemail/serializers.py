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
    Voicemail, VoicemailGreeting, VoicemailMessages, VoicemailOptions,
    VoicemailDestinations
)


class VoicemailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Voicemail
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'url', 'id', 'extension_id', 'password', 'greeting_id', 'alternate_greeting_id',
                    'mail_to', 'sms_to', 'cc', 'attach_file', 'local_after_email', 'enabled', 'description',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class VoicemailGreetingSerializer(serializers.ModelSerializer):

    class Meta:
        model = VoicemailGreeting
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'url', 'id', 'voicemail_id', 'filename', 'name', 'description', 'filestore',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class VoicemailMessagesSerializer(serializers.ModelSerializer):

    class Meta:
        model = VoicemailMessages
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'url', 'id', 'voicemail_id', 'filename', 'name', 'filestore',
                    'caller_id_name', 'caller_id_number', 'duration', 'status',
                    'read', 'transcription', 'base64',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class VoicemailOptionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = VoicemailOptions
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'url', 'id', 'voicemail_id', 'option_digits', 'option_action',
                    'option_param', 'sequence', 'description',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]


class VoicemailDestinationsSerializer(serializers.ModelSerializer):

    class Meta:
        model = VoicemailDestinations
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                    'url', 'id', 'voicemail_id', 'voicemail_dest',
                    'created', 'updated', 'synchronised', 'updated_by'
                ]

