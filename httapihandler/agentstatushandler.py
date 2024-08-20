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
from pbx.commonevents import PresenceIn
from .httapihandler import HttApiHandler
from callcentres.models import CallCentreAgents


class AgentStatusHandler(HttApiHandler):

    handler_name = 'agentstatus'

    def get_data(self):
        if self.exiting:
            return self.return_data('Ok\n')

        self.hostname = self.session_json.get('hostname')
        self.uuid = self.session_json.get('variable_uuid')
        agent_id = self.session_json.get('variable_agent_id')
        agent_authorised = self.session_json.get('variable_agent_authorized')
        try:
            self.cca = CallCentreAgents.objects.select_related('user_uuid').filter(
                        domain_id=self.domain_uuid, agent_id=agent_id).first()
        except:
            self.logger.debug(self.log_header.format('agents status', 'CallCentreAgent not found'))
            return self.return_data(self.error_hangup('C1011'))

        self.pe = PresenceIn()

        self.x_root = self.XrootApi()
        etree.SubElement(self.x_root, 'params')
        self.x_work = etree.SubElement(self.x_root, 'work')

        if not self.cca:
            etree.SubElement(self.x_work, 'pause', milliseconds='1000')
            etree.SubElement(self.x_work, 'playback',
                        file='ivr/ivr-unallocated_number.wav')
            etree.SubElement(self.x_work, 'hangup')
            return self.get_xml()

        etree.SubElement(self.x_work, 'execute', application='answer', data='')

        if agent_authorised == 'true':
            self.loginout()

        next_action =  self.get_next_action()
        if next_action:
            if next_action == 'chk-pin':
                if self.cca.agent_pin == self.qdict.get('pb_input', ''):
                    self.loginout()
                else:
                    etree.SubElement(self.x_work, 'playback', file='phrase:voicemail_fail_auth:#')
                    etree.SubElement(self.x_work, 'hangup')
        else:
            self.act_get_pin()
        return self.get_xml()

    def get_xml(self):
        etree.indent(self.x_root)
        xml = str(etree.tostring(self.x_root), "utf-8")
        return xml

    def act_get_pin(self):
        self.session_json[self.next_action_str] = 'chk-pin'
        self.session.save()
        self.x_work.append(self.play_and_get_digits('phrase:voicemail_enter_pass:#'))
        return

    def loginout(self):
        etree.SubElement(self.x_work, 'pause', milliseconds='1000')
        if self.cca.user_uuid.status == 'Available':
            self.cca.user_uuid.status = 'Logged Out'
            self.pe.send(str(self.cca.id), 'true', self.cca.name.replace(' ', '-'), self.domain_name, self.hostname)
            action = 'logout'
            blf_status = 'true'
            etree.SubElement(self.x_work, 'playback',
                        file='ivr/ivr-you_are_now_logged_out.wav')

        else:
            self.cca.user_uuid.status = 'Available'
            self.pe.send(str(self.cca.id), 'false', self.cca.name.replace(' ', '-'), self.domain_name, self.hostname)
            action = 'login'
            blf_status = 'false'
            etree.SubElement(self.x_work, 'playback',
                        file='ivr/ivr-you_are_now_logged_in.wav')
        self.cca.user_uuid.save()
        if not 'agent+' in self.cca.name:
            self.pe.send(str(self.cca.id), blf_status, 'agent+%s' % self.cca.name.replace(' ', '-'), self.domain_name, self.hostname)

        etree.SubElement(self.x_work, 'pause', milliseconds='2000')
        self.pe.es.send('api callcenter_config agent set status %s \'%s\'' % (str(self.cca.id), self.cca.user_uuid.status))
        self.pe.es.send('api uuid_display %s %s' % (self.uuid, self.cca.user_uuid.status))
        etree.SubElement(self.x_work, 'hangup')
        self.pe.disconnect()
        return




