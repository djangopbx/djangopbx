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

from django.db.models import Q
from lxml import etree
from .httapihandler import HttApiHandler
from callblock.models import CallBlock


class CallBlockHandler(HttApiHandler):

    handler_name = 'callblock'

    def get_data(self):
        if self.exiting:
            return self.return_data('Ok\n')

        caller_id_name = self.qdict.get('Caller-Orig-Caller-ID-Name', 'None')
        caller_id_number = self.qdict.get('Caller-Orig-Caller-ID-Number', 'None')

        x_root = self.XrootApi()
        etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')

        if not 'run' in self.session_json:
            self.session_json['run'] = False
            self.session.save()

            qs = CallBlock.objects.filter(
                ((Q(name=caller_id_name) | Q(name__isnull=True)) |
                (Q(number=caller_id_number) | Q(number__isnull=True)) |
                (Q(name=caller_id_name) & Q(number=caller_id_number))),
                domain_id=self.domain_uuid, enabled='true')
            if not qs:
                self.logger.debug(self.log_header.format('call block', 'No Call Block records found'))
            else:
                act = qs[0].data.split(':')
                etree.SubElement(x_work, 'execute', application=act[0], data=act[1])

        etree.SubElement(x_work, 'break')
        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml
