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


F_YEARS = {
    '2024' : '2024',
    '2025' : '2025',
    '2026' : '2026',
    '2027' : '2027',
    '2028' : '2028',
    '2029' : '2029',
}

F_MONTHS = {
    '01' : 'Jan',
    '02' : 'Feb',
    '03' : 'Mar',
    '04' : 'Apr',
    '05' : 'May',
    '06' : 'Jun',
    '07' : 'Jul',
    '08' : 'Aug',
    '09' : 'Sep',
    '10' : 'Oct',
    '11' : 'Nov',
    '12' : 'Dec',
}

F_DAYS = {
    '01' : '01',
    '02' : '02',
    '03' : '03',
    '04' : '04',
    '05' : '05',
    '06' : '06',
    '07' : '07',
    '08' : '08',
    '09' : '09',
    '10' : '10',
    '11' : '11',
    '12' : '12',
    '13' : '13',
    '14' : '14',
    '15' : '15',
    '16' : '16',
    '17' : '17',
    '18' : '18',
    '19' : '19',
    '20' : '20',
    '21' : '21',
    '22' : '22',
    '23' : '23',
    '24' : '24',
    '25' : '25',
    '26' : '26',
    '27' : '27',
    '28' : '28',
    '29' : '29',
    '30' : '30',
    '31' : '31',
}


class YearsListFilter(admin.SimpleListFilter):
    title = _('Year')

    parameter_name = 'year'

    def lookups(self, request, model_admin):
        return [(k, _(v))for k,v in F_YEARS.items()]

    def queryset(self, request, queryset):
        if self.value() in F_YEARS:
            return queryset.filter(
                year=F_YEARS[self.value()],
            )


class MonthsListFilter(admin.SimpleListFilter):
    title = _('Month')

    parameter_name = 'month'

    def lookups(self, request, model_admin):
        return [(k, _(v))for k,v in F_MONTHS.items()]

    def queryset(self, request, queryset):
        if self.value() in F_MONTHS:
            return queryset.filter(
                month=F_MONTHS[self.value()],
            )


class DaysListFilter(admin.SimpleListFilter):
    title = _('Day')

    parameter_name = 'day'

    def lookups(self, request, model_admin):
        return [(k, _(v))for k,v in F_DAYS.items()]

    def queryset(self, request, queryset):
        if self.value() in F_DAYS:
            return queryset.filter(
                day=F_DAYS[self.value()],
            )
