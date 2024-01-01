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
        if self.value() == '35':
            return queryset.filter(rtp_audio_in_mos__gt=0, rtp_audio_in_mos__lte=3.5)
        if self.value() == '30':
            return queryset.filter(rtp_audio_in_mos__gt=0, rtp_audio_in_mos__lte=3.0)
        if self.value() == '25':
            return queryset.filter(rtp_audio_in_mos__gt=0, rtp_audio_in_mos__lte=2.5)
        if self.value() == '20':
            return queryset.filter(rtp_audio_in_mos__gt=0, rtp_audio_in_mos__lte=2.0)
        if self.value() == '15':
            return queryset.filter(rtp_audio_in_mos__gt=0, rtp_audio_in_mos__lte=1.5)
        if self.value() == '10':
            return queryset.filter(rtp_audio_in_mos__gt=0, rtp_audio_in_mos__lte=1.0)
        if self.value() == '00':
            return queryset.filter(rtp_audio_in_mos=0)
