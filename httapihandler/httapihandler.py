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

import logging
from django.core.cache import cache
from lxml import etree
from .models import HttApiSession
from tenants.pbxsettings import PbxSettings


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

    def __init__(self, qdict, getVar=True, getFile=False, fdict={}):
        self.logger = logging.getLogger(__name__)
        self.debug = False
        self.qdict = qdict
        self.fdict = fdict
        self.getfile = getFile
        self.exiting = False
        self.session = None
        self.first_call = False
        self.session_id = qdict.get('session_id')
        if self.session_id:
            self.get_httapi_session()
        else:
            self.exiting = True
        if qdict.get('exiting', 'false') == 'true':
            self.destroy_httapi_session()
            self.exiting = True

        self.first_call = self.get_first_call()

        if self.debug:
            self.logger.debug(self.log_header.format('request\n', self.qdict))
        self.var_list = []
        self.domain_uuid = None
        self.domain_name = None
        self.extension_uuid = None
        self.default_language = None
        self.default_dialiect = None
        self.default_voice = None
        self.sounds_dir = None
        self.sounds_tuple = None
        self.domain_var_list = [
        'domain_uuid', 
        'domain_name', 
        ]
        self.language_var_list = [
        'default_language',
        'default_dialiect',
        'default_voice',
        ]

        if getVar:
            self.get_variables()

    def get_variables(self):
        pass

    def get_data(self):
        return self.return_data(self.error_hangup('HF0001'))

    def htt_get_variables(self):
        if not self.var_list:
            return False
        x_root = self.XrootApi()
        etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')
        for var in self.var_list:
            etree.SubElement(x_work, 'getVariable', name=var, permanent='1')

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml

    def htt_get_data(self):
        if self.first_call:
            xml = self.htt_get_variables()
            if xml:
                return self.return_data(xml)
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

    def get_allowed_addresses(self):
        cache_key = 'httapihandler:allowed_addresses'
        aa = cache.get(cache_key)
        if aa:
            allowed_addresses = aa.split(',')
        else:
            allowed_addresses = PbxSettings().default_settings('httapihandler', 'allowed_address', 'array')
            aa = ','.join(allowed_addresses)
            cache.set(cache_key, aa)
        return allowed_addresses

    def address_allowed(self, ip_address):
        allowed_addresses = self.get_allowed_addresses()
        if ip_address in allowed_addresses:
            return True
        else:
            return False

    def get_first_call(self):
        if self.handler_name in self.session.json:
            if 'first_call' in self.session.json[self.handler_name]:
                if self.session.json[self.handler_name]['first_call']:
                    self.session.json[self.handler_name]['first_call'] = False
                    self.session.save()
                    return False
            else:
                self.session.json[self.handler_name].update({'first_call': True})
                self.session.save()
                return True
        else:
            self.session.json.update({self.handler_name: {'first_call': True}})
            self.session.save()
        return self.session.json[self.handler_name]['first_call']

    def get_httapi_session(self):
        try:
            self.session = HttApiSession.objects.get(pk=self.session_id)
        except HttApiSession.DoesNotExist:
            s_name = self.qdict.get('url', '/n/None/').rstrip('/').rsplit('/', 1)[1]
            self.session = HttApiSession.objects.create(id=self.session_id, name=s_name, json={self.handler_name: {}})
        return

    def destroy_httapi_session(self):
        try:
            HttApiSession.objects.get(pk=self.session_id).delete()
        except HttApiSession.DoesNotExist:
            pass
        return

    def get_data(self):
        return self.return_data('Ok\n')


    def get_domain_variables(self):
        self.domain_uuid = self.qdict.get('domain_uuid')
        self.domain_name = self.qdict.get('domain_name')
        return

    def get_language_variables(self):
        self.default_language = self.qdict.get('default_language', 'en')
        self.default_dialect = self.qdict.get('default_dialiect', 'us')
        self.default_voice = self.qdict.get('default_voice', 'callie')
        return

    def get_sounds_variables(self):
        self.sounds_dir = self.qdict.get('sounds_dir', '/usr/share/freeswitch/sounds')
        self.recordings_dir = PbxSettings().default_settings('switch', 'recordings', 'dir', '/var/lib/freeswitch/recordings', True)[0]
        return

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

