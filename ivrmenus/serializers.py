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

from rest_framework import serializers
from .models import (
    IvrMenus, IvrMenuOptions,
)


class IvrMenusSerializer(serializers.ModelSerializer):

    gen_xml = serializers.HyperlinkedIdentityField(view_name='ivrmenus-generatexml')
    class Meta:
        model = IvrMenus
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                'url', 'gen_xml',
                'id',
                'domain_id',
                'dialplan_id',
                'name',
                'extension',
                'language',
                'greet_long',
                'greet_short',
                'invalid_sound',
                'exit_sound',
                'confirm_macro',
                'confirm_key',
                'tts_engine',
                'tts_voice',
                'confirm_attempts',
                'timeout',
                'exit_app',
                'exit_data',
                'inter_digit_timeout',
                'max_failiures',
                'max_timeouts',
                'digit_len',
                'direct_dial',
                'ringback',
                'cid_prefix',
                'context',
                'enabled',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]


class IvrMenuOptionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = IvrMenuOptions
        read_only_fields = ['created', 'updated', 'synchronised', 'updated_by']
        fields = [
                'url', 'id',
                'ivr_menu_id',
                'option_digits',
                'option_action',
                'option_param',
                'sequence',
                'description',
                'created',
                'updated',
                'synchronised',
                'updated_by'
                ]
