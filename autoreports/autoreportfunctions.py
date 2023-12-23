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

from django.utils.translation import gettext_lazy as _
from django.template import loader
from django.db import connections
from .models import AutoReports
from pbx.pbxsendsmtp import PbxTemplateMessage


class ArFunctions():

    def __init__(self, rep_freq=None, rep_uuid=None):
        self.rep_freq = rep_freq
        self.rep_uuid = rep_uuid
        if rep_freq:
            self.reps = AutoReports.objects.filter(frequency=self.rep_freq, enabled='true')
        else:
            if rep_uuid:
                try:
                    self.rep = AutoReports.objects.get(pk=rep_uuid)
                except:
                    self.rep = False
            else:
                self.rep = False
        self.connection = connections['default']

    def process_reports(self):
        m = PbxTemplateMessage()
        for self.rep in self.reps:
            data = self.gen_report()
            tpl = loader.get_template('autoreports/viewreport.html')
            html = tpl.render({'d': data})
            if data['error']:
                out = (False, 'Probable SQL Error')
            else:
                out = m.Send(','.join(self.rep.recipients.splitlines()), 'Report: %s' % self.rep.title, html, 'html')
            if not out[0]:
                print(out[1])

    def gen_report(self):
        data = {'error': False}
        if not self.rep:
            return data
        data['title'] = self.rep.title
        data['message'] = self.rep.message
        data['footer'] = self.rep.footer
        data['sections'] = {}

        sects = self.rep.autoreportsections_set.filter(enabled='true').order_by('sequence')
        for sect in sects:
            data['sections'][str(sect.id)] = {}
            data['sections'][str(sect.id)]['title'] = sect.title
            data['sections'][str(sect.id)]['message'] = sect.message
            if 'set '.casefold() in sect.sql.casefold():
                data['error'] = True
                data['errmsg'] = 'SET keyword no allowed'
                data['errsec'] = sect.title
                return data
            with self.connection.cursor() as section_cursor:
                section_cursor.execute('SET default_transaction_read_only = true;')
                try:
                    section_cursor.execute(sect.sql)
                except Exception as e:
                    data['error'] = True
                    data['errmsg'] = e
                    data['errsec'] = sect.title
                    return data

                columns = [col[0].replace('_', ' ') for col in section_cursor.description]
                fetched = section_cursor.fetchall()
            data['sections'][str(sect.id)]['columns'] = columns
            data['sections'][str(sect.id)]['rows'] = fetched
        return data
