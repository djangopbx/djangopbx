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

import logging
from django.conf import settings
from lxml import etree
from .models import HttApiSession


class HttApiHandler():

# The session in the HttApiHandlerFunctions class uses a Django JSONField.
#
# You can set a session value with:
#    self.session.json['my_variable'] = 'something'
#    self.session.save()
#
# Read it with:
#    if 'my_variable' in self.session.json:
#        my_var = self.session.json['my_variable']
#

    log_header = 'HttApi Handler: {}: {}'
    handler_name = 'base'
    next_action_str = 'next_action'
    load_vars = (
        # domain variables
        'variable_domain_uuid',
        'variable_domain_name',
        # language variables
        'variable_default_language',
        'variable_default_dialect',
        'variable_default_voice',
        # dialplan call variables
        'variable_extension_uuid',
        'variable_context',
        'variable_originate_disposition',
        'variable_dialed_extension',
        'variable_last_busy_dialed_extension',
        'variable_forward_busy_enabled',
        'variable_forward_busy_destination',
        'variable_forward_no_answer_enabled',
        'variable_forward_no_answer_destination',
        'variable_forward_user_not_registered_enabled',
        'variable_forward_user_not_registered_destination',
        'variable_call_direction',
        'variable_missed_call_app',
        'variable_missed_call_data',
        'variable_caller_id_name',
        'variable_caller_id_number',
        'variable_sip_to_user',
        'variable_dialed_user',
        # djangopbx application uuid variables
        'variable_callflow_uuid',
        'variable_conference_uuid',
        'variable_ring_group_uuid',
        # general dialplan application variables
        'variable_agent_id',
        'variable_agent_authorized',
        'variable_callflow_pin',
        'variable_conference_uuid',
        'variable_pin_number',
        'variable_disa_greeting',
        'variable_predefined_destination',
        'variable_privacy',
        'variable_sounds_dir',
        'variable_recording_prefix',
        'variable_speed_dial',
        'variable_uuid',
        'variable_user_uuid'
    )


    def __init__(self, qdict, getFile=False, fdict={}, **kwargs):
        self.__dict__.update(kwargs)
        self.logger = logging.getLogger(__name__)
        self.debug = False
        self.qdict = qdict
        print(qdict)
        self.fdict = fdict
        self.getfile = getFile
        self.exiting = False
        self.session = None
        self.session_json = None
        self.domain_uuid = None
        self.domain_name = None
        self.hostname = None
        self.session_id = qdict.get('session_id')
        if self.session_id:
            self.get_httapi_session()
        else:
            self.exiting = True
        if qdict.get('exiting', 'false') == 'true':
            self.destroy_httapi_session()
            self.exiting = True
        if self.debug:
            self.logger.debug(self.log_header.format('request\n', self.qdict))
        self.recordings_dir = settings.PBX_HTTAPI_SWITCH_RECORDINGS

    def get_data(self):
        return self.return_data(self.error_hangup('HF0001'))

    def htt_get_data(self):
        return self.return_data(self.get_data())

    def return_data(self, xml):
        if self.debug:
            self.logger.debug(self.log_header.format('response\n', xml))
        return xml

    def XrootApi(self):
        return etree.XML(
            b'<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n'
            b'<document type=\"xml/freeswitch-httapi\"></document>'
            )

    def error_hangup(self, message='Err'):
        x_root = self.XrootApi()
        etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')
        etree.SubElement(x_work, 'playback', file='ivr/ivr-call_cannot_be_completed_as_dialed.wav')
        etree.SubElement(x_work, 'execute', application='sleep', data='1000')
        etree.SubElement(
            x_work, 'execute', application='set',
            data='httapi=httapi:%s message:%s}' % (self.session_id, message)
            )
        etree.SubElement(x_work, 'hangup')
        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml

    def httapi_break(self):
        x_root = self.XrootApi()
        etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')
        etree.SubElement(x_work, 'break')
        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml

    def get_httapi_session(self):
        try:
            self.session = HttApiSession.objects.get(pk=self.session_id)
        except HttApiSession.DoesNotExist:
            s_name = self.qdict.get('url', '/n/None/').rstrip('/').rsplit('/', 1)[1]
            self.session = HttApiSession.objects.create(id=self.session_id, name=s_name, json={self.handler_name: {}})
        if not self.handler_name in self.session.json:
            self.session.json[self.handler_name] = {}
        for v in self.load_vars:
            val = self.qdict.get(v)
            if val:
                self.session.json[self.handler_name][v] = val
        self.session.save()
        self.session_json = self.session.json[self.handler_name]
        self.domain_uuid = self.session_json.get('variable_domain_uuid')
        self.domain_name = self.session_json.get('variable_domain_name')
        return

    def destroy_httapi_session(self):
        try:
            HttApiSession.objects.get(pk=self.session_id).delete()
        except HttApiSession.DoesNotExist:
            pass
        return

    def get_data(self):
        return self.return_data('Ok\n')

    def get_next_action(self):
        try:
            return self.session_json[self.next_action_str]
        except KeyError:
            return None

    def play_and_get_digits(self, file_name, var_name='pb_input', digit_regex='~\\d+#'):
        x_pb = etree.Element('playback')
        x_pb.attrib['name'] = var_name
        x_pb.attrib['error-file'] = 'ivr/ivr-error.wav'
        x_pb.attrib['file'] = file_name
        x_pb.attrib['digit-timeout'] = '5000'
        x_pb.attrib['input-timeout'] = '10000'
        x_pb.attrib['loops'] = '3'
        x_pb_b = etree.SubElement(x_pb, 'bind')
        x_pb_b.attrib['strip'] = '#'
        x_pb_b.text = digit_regex
        return x_pb

    def record_and_get_digits(self, file_name, var_name='rd_input', digit_regex='~\\d+#'):
        x_pb = etree.Element('record')
        x_pb.attrib['name'] = var_name
        x_pb.attrib['error-file'] = 'ivr/ivr-error.wav'
        x_pb.attrib['beep-file'] = 'tone_stream://%(100,0,800)'
        x_pb.attrib['file'] = file_name
        x_pb.attrib['input-timeout'] = '60000'
        x_pb_b = etree.SubElement(x_pb, 'bind')
        x_pb_b.text = digit_regex
        return x_pb

