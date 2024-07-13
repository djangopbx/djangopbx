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

from django.core.cache import cache
from lxml import etree
from .httapihandler import HttApiHandler
from callflows.models import CallFlows
from callflows.callflowfunctions import CfFunctions
from pbx.commonevents import PresenceIn


class CallFlowToggleHandler(HttApiHandler):

    handler_name = 'callflowtoggle'

    def get_variables(self):
        self.var_list = [
        'callflow_uuid',
        'callflow_pin',
        ]
        self.var_list.extend(self.domain_var_list)

    def get_data(self):
        if self.exiting:
            return self.return_data('Ok\n')

        self.get_domain_variables()
        self.hostname = self.qdict.get('hostname')
        call_flow_uuid = self.qdict.get('callflow_uuid')
        try:
            q = CallFlows.objects.get(pk=call_flow_uuid)
        except CallFlows.DoesNotExist:
            self.logger.debug(self.log_header.format('call flow toggle', 'Call Flow UUID not found'))
            return self.return_data(self.error_hangup('D1001'))

        x_root = self.XrootApi()
        etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')
        if 'next_action' in self.session.json[self.handler_name]:
            next_action =  self.session.json[self.handler_name]['next_action']
            if next_action == 'chk-pin':
                pin_number = self.session.json[self.handler_name]['pin_number']
                if pin_number == self.qdict.get('pb_input', ''):
                    etree.SubElement(x_work, 'pause', milliseconds='1000')
                    if q.status == 'true':
                        etree.SubElement(
                            x_work, 'playback',
                            file='ivr/ivr-night_mode.wav'
                            )
                        q.status = 'false'
                    else:
                        etree.SubElement(
                            x_work, 'playback',
                            file='ivr/ivr-day_mode.wav'
                            )
                        q.status = 'true'
                    q.save()
                    cff = CfFunctions(q, self.handler_name)
                    cff.generate_xml()
                    etree.SubElement(x_work, 'pause', milliseconds='1000')
                    etree.SubElement(x_work, 'playback', file='voicemail/vm-goodbye.wav')
                    etree.SubElement(x_work, 'hangup')
                    directory_cache_key = 'dialplan:%s' % self.domain_name
                    cache.delete(directory_cache_key)
                    pe = PresenceIn()
                    pe.send(str(q.id), q.status, q.feature_code, self.domain_name, self.hostname)
                else:
                    etree.SubElement(x_work, 'playback', file='phrase:voicemail_fail_auth:#')
                    etree.SubElement(x_work, 'hangup')

        else:
            pin_number = self.qdict.get('callflow_pin')
            if not pin_number:
                return self.error_hangup('R2001')

            self.session.json[self.handler_name]['pin_number'] = pin_number
            self.session.json[self.handler_name]['next_action'] = 'chk-pin'
            self.session.save()
            x_work.append(self.play_and_get_digits('phrase:voicemail_enter_pass:#'))

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml
