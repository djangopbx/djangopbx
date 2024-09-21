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

import os
import uuid
import logging
from lxml import etree
from django.conf import settings
from pbx.pbxsendsmtp import PbxTemplateMessage
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
        'variable_originate_disposition',
        'variable_dialed_extension',
        'variable_destination_number',
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
        'variable_effective_caller_id_number',
        'variable_sip_to_user',
        'variable_sip_from_user',
        'variable_sip_number_alias',
        'variable_dialed_user',
        'variable_record_seconds',
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
        'variable_user_uuid',
        # voicemail application variables
        'variable_voicemail_greeting_number',
        'variable_skip_instructions',
        'variable_skip_greeting',
        'variable_vm_say_caller_id_number',
        'variable_vm_say_date_time',
        'variable_voicemail_authorized'
    )


    def __init__(self, qdict, getFile=False, fdict={}, **kwargs):
        self.__dict__.update(kwargs)
        self.logger = logging.getLogger(__name__)
        self.debug = False
        self.qdict = qdict
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
            self.exit_handler()
        if self.debug:
            self.logger.debug(self.log_header.format('request\n', self.qdict))
        self.recordings_dir = settings.PBX_HTTAPI_SWITCH_RECORDINGS

    def exit_handler(self):
        if settings.PBX_HTTAPI_HANGUP_HANDLER:
            self.hangup_handler()
        if self.destroy_session_ok():
            self.destroy_session()
        self.exiting = True
        return

    def destroy_session_ok(self):
        #  Handler classes can override this function if they wish to destroy the session themselves.
        return True

    def destroy_session(self):
        self.delete_all_temporary_files(False)
        self.destroy_httapi_session()

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
            try:
                s_name = self.qdict.get('url', 'http://localhost:8080/httapihandler/none/args').split('/')[4]
            except IndexError:
                s_name = 'none'
            self.session = HttApiSession.objects.create(id=self.session_id, name=s_name, json={self.handler_name: {'tmpfiles': {}}})
        if not self.handler_name in self.session.json:
            self.session.json[self.handler_name] = {}
            self.session.json[self.handler_name]['tmpfiles'] = {}
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

    def create_temporary_file(self, ext='.tmp'):
        name = '%s%s' % (uuid.uuid4(), ext)
        fullname = '/tmp/%s' % name
        # creates the temporary file and closes it Immediately.
        with open(fullname, 'w') as fp:
            pass
        self.session.json[self.handler_name]['tmpfiles'][name] = fullname
        self.session.save()
        return name

    def delete_temporary_file(self, name):
        try:
            fullname = self.session.json[self.handler_name]['tmpfiles'][name]
        except KeyError:
            return False
        try:
            os.remove(fullname)
        except OSError:
            pass
        del self.session.json[self.handler_name]['tmpfiles'][name]
        self.session.save()
        return True

    def delete_all_temporary_files(self, save=True):
        tempfiles = self.session.json[self.handler_name]['tmpfiles']
        for k, v in tempfiles.items():
            try:
                os.remove(v)
            except OSError:
                pass
        self.session.json[self.handler_name]['tmpfiles'] = {}
        if save:
            self.session.save()
        return True

    def str2int(self, tmpstr):
        try:
            return int(tmpstr)
        except (TypeError, ValueError):
            return 0

    def get_data(self):
        return self.return_data('Ok\n')

    def get_next_action(self):
        try:
            return self.session_json[self.next_action_str]
        except KeyError:
            return None

    def play_and_get_digits(self, file_name, **kwargs):
        var_name = kwargs.get('var_name', 'pb_input')
        digit_regex = kwargs.get('digit_regex', '~\\d+#')
        digit_timeout = kwargs.get('digit_timeout', '5000')
        input_timeout = kwargs.get('input_timeout', '10000')
        loops = kwargs.get('loops', '2')
        x_pb = etree.Element('playback')
        x_pb.attrib['name'] = var_name
        x_pb.attrib['error-file'] = 'ivr/ivr-error.wav'
        x_pb.attrib['file'] = file_name
        x_pb.attrib['digit-timeout'] = digit_timeout
        x_pb.attrib['input-timeout'] = input_timeout
        x_pb.attrib['loops'] = loops
        x_pb_b = etree.SubElement(x_pb, 'bind')
        x_pb_b.attrib['strip'] = '#'
        x_pb_b.text = digit_regex
        return x_pb

    def record_and_get_digits(self, file_name, **kwargs):
        var_name = kwargs.get('var_name', 'rd_input')
        digit_regex = kwargs.get('digit_regex', '~[0-9#\*]')
        digit_timeout = kwargs.get('digit_timeout', '50000')
        terminators = kwargs.get('terminators', '')
        limit = kwargs.get('limit', '60')
        x_pb = etree.Element('record')
        x_pb.attrib['name'] = var_name
        x_pb.attrib['error-file'] = 'ivr/ivr-error.wav'
        x_pb.attrib['beep-file'] = 'tone_stream://%(100,0,800)'
        x_pb.attrib['file'] = file_name
        x_pb.attrib['limit'] = limit
        x_pb.attrib['terminators'] = terminators
        x_pb.attrib['digit-timeout'] = digit_timeout
        x_pb_b = etree.SubElement(x_pb, 'bind')
        x_pb_b.text = digit_regex
        return x_pb

    def hangup_handler(self):
        if self.session_json.get('hangup_handler_set', 'no') == 'no':
            return False
        missed_call_app  = self.session_json.get('variable_missed_call_app')            # noqa: E221
        missed_call_data = self.session_json.get('variable_missed_call_data')           # noqa: E221
        caller_id_name   = self.session_json.get('variable_caller_id_name', ' ')        # noqa: E221
        caller_id_number = self.session_json.get('variable_caller_id_number', ' ')      # noqa: E221
        sip_to_user      = self.session_json.get('variable_sip_to_user', ' ')           # noqa: E221
        dialed_user      = self.session_json.get('variable_dialed_user', ' ')           # noqa: E221
        default_language = self.session_json.get('variable_default_language', 'en')     # noqa: E221
        default_dialect  = self.session_json.get('variable_default_dialect', 'us')      # noqa: E221
        orig_disposition = self.session_json.get('variable_originate_disposition', ' ') # noqa: E221

        if not orig_disposition == 'ORIGINATOR_CANCEL':
            return False
        if not missed_call_app:
            return False
        if not missed_call_app == 'email':
            return False
        if not missed_call_data:
            return False

        m = PbxTemplateMessage()
        tp_subject, tp_body, tp_type = m.GetTemplate(
            self.domain_uuid, '%s-%s' % (default_language, default_dialect),
            'missed', 'default'
            )
        if not tp_subject:
            self.logger.warn(self.log_header.format('hangup', 'Email Template mising'))
            return False

        try:
            subject = tp_subject.format(
                caller_id_name=caller_id_name, caller_id_number=caller_id_number,
                sip_to_user=sip_to_user, dialed_user=dialed_user
                )
            body = tp_body.format(
                caller_id_name=caller_id_name, caller_id_number=caller_id_number,
                sip_to_user=sip_to_user, dialed_user=dialed_user
                )
        except:
            self.logger.warn(self.log_header.format('hangup', 'Template format Exception'))
            return False

        try:
            out = m.Send(missed_call_data, subject, body, tp_type)
        except:
            self.logger.warn(self.log_header.format('hangup', 'SMTP Exception'))
            return False

        if self.debug or not out[0]:
            self.logger.warn(self.log_header.format('hangup', out[1]))
        return True
