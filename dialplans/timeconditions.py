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

from datetime import datetime
from django.utils.translation import gettext_lazy as _


class TimeConditions():

    vr_choice = [('', '')]
    vr_dict = {}

    def __init__(self):
        self.dt_stamp = datetime.now().strftime('%Y-%m-%d %H:%M')

    def get_choices(self, idtag, choice):
        ibidtag = idtag.replace('_c_', '_v_')
        oobidtag = idtag.replace('_c_', '_r_')
        cl = ''
        if choice == 'year':
            cl = ''.join(self.tag_wrapped_choice(self.get_years()))
        elif choice == 'mon':
            cl = ''.join(self.tag_wrapped_choice(self.get_months()))
        elif choice == 'mday':
            cl = ''.join(self.tag_wrapped_choice(self.get_daysofmonth()))
        elif choice == 'wday':
            cl = ''.join(self.tag_wrapped_choice(self.get_daysofweek()))
        elif choice == 'week':
            cl = ''.join(self.tag_wrapped_choice(self.get_weeksofyear()))
        elif choice == 'mweek':
            cl = ''.join(self.tag_wrapped_choice(self.get_weeksofmonth()))
        elif choice == 'hour':
            cl = ''.join(self.tag_wrapped_choice(self.get_hoursofday()))
        elif choice == 'minute-of-day':
            cl = ''.join(self.tag_wrapped_choice(self.get_timeofday()))

        if choice == 'date-time':
            return '<div id=\"id_%s\" hx-swap-oob=\"outerHTML\">'\
                '<input onClick=\"dt_click(this.id)\" type=\"text\" name=\"%s\" value=\"%s\" id=\"id_%s\"></div>'\
                '<input onClick=\"dt_click(this.id)\" type=\"text\" name=\"%s\" value=\"%s\" id=\"id_%s\">' % (oobidtag,
                                                oobidtag, self.dt_stamp, oobidtag, ibidtag, self.dt_stamp, ibidtag)

        return '<div id=\"id_%s\" hx-swap-oob=\"outerHTML\">'\
                '<select name=\"%s\" class="custom-select custom-select-sm" id=\"id_%s\">'\
                '<option value=\"\"></option>%s</select></div>'\
                '<select name=\"%s\" class="custom-select custom-select-sm" id=\"id_%s\">%s'\
                '</select>' % (oobidtag, oobidtag, oobidtag, cl, ibidtag, ibidtag, cl)

    def tag_wrapped_choice(self, c):
        return ['<option value=\"%s\">%s</option>' % (x[0], x[1]) for x in c]

    def get_condition_list(self, cnd_only=False):
        tuplelist = [
                ('', ''),
                ('year',          _('Year')),
                ('mon',           _('Month')),
                ('mday',          _('Day of Month')),
                ('wday',          _('Day of Week')),
                ('week',          _('Week of Year')),
                ('mweek',         _('Week of Month')),
                ('hour',          _('Hour of Day')),
                ('minute-of-day', _('Time of Day')),
                ('date-time',     _('Date & Time'))
                ]

        if cnd_only:
            return [c[0] for c in tuplelist]

        return tuplelist

    def get_months(self):
        tuplelist = [
                ('1',  _('January')),
                ('2',  _('February')),
                ('3',  _('March')),
                ('4',  _('April')),
                ('5',  _('May')),
                ('6',  _('June')),
                ('7',  _('July')),
                ('8',  _('August')),
                ('9',  _('September')),
                ('10', _('October')),
                ('11', _('November')),
                ('12', _('December'))
                ]
        return tuplelist

    def get_daysofweek(self):
        tuplelist = [
                ('1', _('Sunday')),
                ('2', _('Monday')),
                ('3', _('Tuesday')),
                ('4', _('Wednesday')),
                ('5', _('Thursday')),
                ('6', _('Friday')),
                ('7', _('Saturday'))
                ]
        return tuplelist

    def get_years(self):
        return [(str(x), str(x)) for x in range(2022, 2036)]

    def get_weeksofyear(self):
        return [(str(x), str(x)) for x in range(1, 53)]

    def get_weeksofmonth(self):
        return [(str(x), str(x)) for x in range(1, 6)]

    def get_daysofmonth(self):
        return [(str(x), str(x)) for x in range(1, 32)]

    def get_hoursofday(self):
        return [(str(x), str(x)) for x in range(0, 24)]

    def get_timeofday(self):
        t = []
        for h in range(0, 24):
            for m in range(0, 60):
                t.append((str((h * 60) + m), f'{h:d}:{m:02d}'))
        return t

    def build_vr_choice(self):
        self.vr_choice.append([_('Day of Week'),   self.get_daysofweek()])
        self.vr_choice.append([_('Day of Month'),  self.get_daysofmonth()])
        self.vr_choice.append([_('Month'),         self.get_months()])
        self.vr_choice.append([_('Week of Month'), self.get_weeksofmonth()])
        self.vr_choice.append([_('Week of Year'),  self.get_weeksofyear()])
        self.vr_choice.append([_('Year'),          self.get_years()])
        self.vr_choice.append([_('Hour of Day'),   self.get_hoursofday()])
        self.vr_choice.append([_('Time of Day'),   self.get_timeofday()])

    def build_vr_dict(self):
        self.vr_dict['wday']          = self.get_daysofweek()    # noqa: E221
        self.vr_dict['mday']          = self.get_daysofmonth()   # noqa: E221
        self.vr_dict['mon']           = self.get_months()        # noqa: E221
        self.vr_dict['mweek']         = self.get_weeksofmonth()  # noqa: E221
        self.vr_dict['week']          = self.get_weeksofyear()   # noqa: E221
        self.vr_dict['year']          = self.get_years()         # noqa: E221
        self.vr_dict['hour']          = self.get_hoursofday()    # noqa: E221
        self.vr_dict['minute-of-day'] = self.get_timeofday()     # noqa: E221
