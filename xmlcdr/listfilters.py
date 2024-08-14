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

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

CALL_DIRECTION = {
    'inbound': 'Inbound',
    'outbound': 'Outbound',
    'loacl': 'Local',
    'None' : 'None'
}

HANGUP_CAUSE = {
    'CALL_REJECTED' : 'CALL_REJECTED',
    'CHAN_NOT_IMPLEMENTED' : 'CHAN_NOT_IMPLEMENTED',
    'DESTINATION_OUT_OF_ORDER' : 'DESTINATION_OUT_OF_ORDER',
    'INVALID_GATEWAY' : 'INVALID_GATEWAY',
    'MANDATORY_IE_MISSING' : 'MANDATORY_IE_MISSING',
    'MEDIA_TIMEOUT' : 'MEDIA_TIMEOUT',
    'NO_ANSWER' : 'NO_ANSWER',
    'NORMAL_CLEARING' : 'NORMAL_CLEARING',
    'NORMAL_UNSPECIFIED' : 'NORMAL_UNSPECIFIED',
    'NO_ROUTE_DESTINATION' : 'NO_ROUTE_DESTINATION',
    'ORIGINATOR_CANCEL' : 'ORIGINATOR_CANCEL',
    'SERVICE_UNAVAILABLE' : 'SERVICE_UNAVAILABLE',
    'UNALLOCATED_NUMBER' : 'UNALLOCATED_NUMBER',
    'USER_BUSY' : 'USER_BUSY',
}

EVENT_NAME = {
    'CHANNEL_CALLSTATE' : 'CHANNEL_CALLSTATE',
    'CHANNEL_HOLD' : 'CHANNEL_HOLD',
    'CHANNEL_UNHOLD' : 'CHANNEL_UNHOLD',
    'CUSTOM' : 'CUSTOM',
    'DTMF' : 'DTMF',
#    'PLAYBACK_START' : 'PLAYBACK_START',
#    'PLAYBACK_STOP' : 'PLAYBACK_STOP',
    'PLAYBACK_STOP' : 'PLAYBACK_STOP',
}

EVENT_SUBCLASS = {
    'callcenter_info' : 'callcenter::info',
    'conference_maintenance' : 'conference::maintenance',
    'vm_maintenance' : 'vm::maintenance',
}


class MosScoreListFilter(admin.SimpleListFilter):
    title = _('MOS Score')
    parameter_name = "mos"

    def lookups(self, request, model_admin):
        return [
            ('40', _('4 or less')),
            ('35', _('3.5 or less')),
            ('30', _('3 or less')),
            ('25', _('2.5 or less')),
            ('20', _('2 or less')),
            ('15', _('1.5 or less')),
            ('10', _('1 or less')),
            ('00', _('Is Zero')),
        ]

    def queryset(self, request, queryset):
        if self.value() == '40':
            return queryset.filter(rtp_audio_in_mos__gt=0, rtp_audio_in_mos__lte=4.0)
        elif self.value() == '35':
            return queryset.filter(rtp_audio_in_mos__gt=0, rtp_audio_in_mos__lte=3.5)
        elif self.value() == '30':
            return queryset.filter(rtp_audio_in_mos__gt=0, rtp_audio_in_mos__lte=3.0)
        elif self.value() == '25':
            return queryset.filter(rtp_audio_in_mos__gt=0, rtp_audio_in_mos__lte=2.5)
        elif self.value() == '20':
            return queryset.filter(rtp_audio_in_mos__gt=0, rtp_audio_in_mos__lte=2.0)
        elif self.value() == '15':
            return queryset.filter(rtp_audio_in_mos__gt=0, rtp_audio_in_mos__lte=1.5)
        elif self.value() == '10':
            return queryset.filter(rtp_audio_in_mos__gt=0, rtp_audio_in_mos__lte=1.0)
        elif self.value() == '00':
            return queryset.filter(rtp_audio_in_mos=0)


class CallDurationListFilter(admin.SimpleListFilter):
    title = _('Call duration')

    parameter_name = 'call_duration'

    def lookups(self, request, model_admin):
        return [
            ('0s', _('Zero s')),
            ('lt2s', _('< 2s')),
            ('lt10s', _('< 10s')),
            ('gt10slt3600s', _('> 10s but < 1h')),
            ('gt3600s', _('> 1h')),
            ('gt7200s', _('> 2h')),
        ]

    def queryset(self, request, queryset):
        if self.value() == '0s':
            return queryset.filter(
                duration=0
            )
        elif self.value() == 'lt2s':
            return queryset.filter(
                duration__lt=2
            )
        elif self.value() == 'lt10s':
            return queryset.filter(
                duration__lt=10
            )
        elif self.value() == 'gt10slt3600s':
            return queryset.filter(
                duration__gt=10,
                duration__lte=3600,
            )
        elif self.value() == 'gt3600s':
            return queryset.filter(
                duration__gt=3600
            )
        elif self.value() == 'gt7200s':
            return queryset.filter(
                duration__gt=7200
            )


class WithRecordingsListFilter(admin.SimpleListFilter):
    title = _('Has recording')

    parameter_name = 'hasrec'

    def lookups(self, request, model_admin):
        return [('yes', _('Yes')), ('no', _('No'))]

    def queryset(self, request, queryset):
        if self.value() == 'no':
            return queryset.filter(
                (Q(record_path__isnull=True) | Q(record_path=''))
            )
        elif self.value() == 'yes':
            return queryset.filter(
                record_path__isnull=False
            ).exclude(record_path='')


class CallDirectionListFilter(admin.SimpleListFilter):
    title = _('Call direction')

    parameter_name = 'direction'

    def lookups(self, request, model_admin):
        return [(k, _(v))for k,v in CALL_DIRECTION.items()]

    def queryset(self, request, queryset):
        if self.value() in CALL_DIRECTION:
            return queryset.filter(
                direction=CALL_DIRECTION[self.value()],
            )


class HangupCauseListFilter(admin.SimpleListFilter):
    title = _('Hangup cause')

    parameter_name = 'hangupc'

    def lookups(self, request, model_admin):
        return [(k, _(v))for k,v in HANGUP_CAUSE.items()]

    def queryset(self, request, queryset):
        if self.value() in HANGUP_CAUSE:
            return queryset.filter(
                hangup_cause=HANGUP_CAUSE[self.value()],
            )


class EventNameListFilter(admin.SimpleListFilter):
    title = _('Event name')

    parameter_name = 'eventname'

    def lookups(self, request, model_admin):
        return [(k, _(v))for k,v in EVENT_NAME.items()]

    def queryset(self, request, queryset):
        if self.value() in EVENT_NAME:
            return queryset.filter(
                event_name=EVENT_NAME[self.value()],
            )


class EventSubclassListFilter(admin.SimpleListFilter):
    title = _('Event subclass')

    parameter_name = 'eventsubclass'

    def lookups(self, request, model_admin):
        return [(k, _(v))for k,v in EVENT_SUBCLASS.items()]

    def queryset(self, request, queryset):
        if self.value() in EVENT_SUBCLASS:
            return queryset.filter(
                event_subclass=EVENT_SUBCLASS[self.value()],
            )

