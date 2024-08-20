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

from lxml import etree
from .httapihandler import HttApiHandler


class TestHandler(HttApiHandler):

    handler_name = 'test'

    def get_data(self):
        if self.exiting:
            return self.return_data('Ok\n')


        try:
            fred = self.session_json['fred']
        except KeyError:
            fred = 'B'
        if fred == 'B':
            x_root = self.XrootApi()
            etree.SubElement(x_root, 'params')
            x_work = etree.SubElement(x_root, 'work')
            etree.SubElement(x_work, 'playback', file='/usr/share/freeswitch/sounds/en/us/callie/ivr/8000/ivr-id_number.wav')
            etree.SubElement(x_work, 'break')
            self.session_json['fred'] = 'A'
            self.session.save()
            etree.indent(x_root)
            xml = str(etree.tostring(x_root), "utf-8")
            return xml

        x_root = self.XrootApi()
        etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')
        etree.SubElement(x_work, 'execute', application='answer')
        x_log = etree.SubElement(x_work, 'log', level='NOTICE')
        x_log.text = 'Hello World'
        etree.SubElement(
            x_work,
            'playback',
            file='/usr/share/freeswitch/sounds/en/us/callie/ivr/8000/ivr-stay_on_line_call_answered_momentarily.wav'
            )
        etree.SubElement(x_work, 'hangup')

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml
