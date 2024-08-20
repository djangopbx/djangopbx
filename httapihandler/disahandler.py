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
from tenants.models import Domain
from recordings.models import Recording


class DISAHandler(HttApiHandler):

    handler_name = 'disa'

    def get_data(self):
        if self.getfile:
            self.get_uploaded_file()

        if self.exiting:
            return self.return_data('Ok\n')

        self.x_root = self.XrootApi()
        etree.SubElement(self.x_root, 'params')
        self.x_work = etree.SubElement(self.x_root, 'work')

        next_action =  self.get_next_action()
        if next_action:
            if next_action == 'chk-pin':
                self.act_chk_pin()
            elif next_action == 'disa':
                self.act_disa()
        else:
            self.act_get_pin()

        etree.indent(self.x_root)
        xml = str(etree.tostring(self.x_root), "utf-8")
        return xml

    def act_get_pin(self):
        pin_number = self.session_json.get('variable_pin_number')
        if not pin_number:
            return self.error_hangup('R2001')

        self.session_json['pin_number'] = pin_number
        self.session_json[self.next_action_str] = 'chk-pin'
        self.session.save()
        self.x_work.append(self.play_and_get_digits('phrase:voicemail_enter_pass:#'))
        return

    def act_chk_pin(self):
        pin_number = self.session_json['pin_number']
        if pin_number == self.qdict.get('pb_input', ''):
            self.session_json[self.next_action_str] = 'disa'
            self.session.save()
            greeting = self.session_json.get('variable_disa_greeting')
            if greeting:
                etree.SubElement(self.x_work, 'playback', file=greeting)
            predefined_destination = self.session_json.get('variable_predefined_destination')
            if predefined_destination:
                self.act_disa(predefined_destination)
                return
            self.x_work.append(self.play_and_get_digits('ivr/ivr-enter_destination_telephone_number.wav'))
        else:
            etree.SubElement(self.x_work, 'playback', file='phrase:voicemail_fail_auth:#')
            etree.SubElement(self.x_work, 'hangup')
        return

    def act_disa(self, predefined_destination=None):
        if predefined_destination:
            destination_number = predefined_destination
        else:
            destination_number = self.qdict.get('pb_input', '')
        privacy = self.session_json.get('variable_privacy', '')
        if privacy == 'true':
            etree.SubElement(self.x_work, 'execute', application='privacy', data='full')
            etree.SubElement(self.x_work, 'execute', application='set', data='sip_h_Privacy=id')
            etree.SubElement(self.x_work, 'execute', application='set', data='privacy=yes')
        context = self.session_json.get('variable_context', '')
        etree.SubElement(self.x_work, 'execute', application='transfer', data='%s XML %s' % (destination_number, context))
        return
