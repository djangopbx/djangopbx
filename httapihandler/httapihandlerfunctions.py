#
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

import logging
from django.core.cache import cache
from lxml import etree
from django.db.models import Q
from .models import HttApiSession
from tenants.models import Domain
from tenants.pbxsettings import PbxSettings


class HttApiHandlerFunctions():

    def __init__(self, qdict):
        self.logger = logging.getLogger(__name__)
        self.debug = True
        self.qdict = qdict
        self.exiting = False
        self.session = None
        self.session_id = qdict.get('session_id')
        if not self.session_id:
            self.exiting = True
        if qdict.get('exiting', 'false') == 'true':
            self.destroy_httapi_session()
            self.exiting = True
        if self.debug:
            self.logger.info('HttApi Handler request:\n{}\n'.format(self.qdict))
        self.dialplan_uuid    = None
        self.dialplan_name    = None
        self.extension_uuid   = None
        self.default_language = None
        self.default_dialiect = None
        self.default_voice    = None
        self.sounds_dir       = None


    def return_data(self, xml):
        if self.debug:
            self.logger.info('HttApi Handler response:\n{}\n'.format(xml))
        return xml


    def XrootApi(self):
        return etree.XML(b'<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n<document type=\"xml/freeswitch-httapi\"></document>')


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


    def get_httapi_session(self, name = 'None'):
        new = False
        try:
            self.session = HttApiSession.objects.get(pk=self.session_id)
        except HttApiSession.DoesNotExist:
            self.session = HttApiSession.objects.create(id=self.session_id, name=name)
            new = True
        return new


    def destroy_httapi_session(self):
        try:
            HttApiSession.objects.get(pk=self.session_id).delete()
        except HttApiSession.DoesNotExist:
            pass
        return


    def get_data(self):
        return self.return_data('Ok\n')

    def get_common_variables(self):
        self.dialplan_uuid = self.qdict.get('variable_dialplan_uuid')
        self.dialplan_name = self.qdict.get('variable_dialplan_name')
        self.extension_uuid = self.qdict.get('variable_extension_uuid')
        self.default_language = self.qdict.get('variable_default_language', 'en')
        self.default_dialiect = self.qdict.get('variable_default_dialiect', 'us')
        self.default_voice = self.qdict.get('variable_default_voice', 'callie')
        self.sounds_dir = self.qdict.get('sounds_dir', '/usr/share/freeswitch/sounds')
        return


class TestHandler(HttApiHandlerFunctions):

    def get_data(self):
        if self.exiting:
            return self.return_data('Ok\n')

        # don't need to do this for this simple scenario but it tests the session mechanism
        self.get_httapi_session('Test')

        x_root = self.XrootApi()
        x_params = etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')
        etree.SubElement(x_work, 'execute', application='answer')
        x_playback = etree.SubElement(x_work, 'playback', file='/usr/share/freeswitch/sounds/en/us/callie/ivr/8000/ivr-stay_on_line_call_answered_momentarily.wav')
        etree.SubElement(x_work, 'hangup')

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return self.return_data(xml)


class FollowMeHandler(HttApiHandlerFunctions):

    def get_data(self):
        if self.exiting:
            return self.return_data('Ok\n')

        #print(self.qdict)
        # don't need to do this for this simple scenario but it tests the session mechanism
        self.get_httapi_session('Follow Me')
        self.get_common_variables()
        print(self.extension_uuid)
        print(self.default_voice)

        x_root = self.XrootApi()
        x_params = etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')
        etree.SubElement(x_work, 'execute', application='answer')
        x_playback = etree.SubElement(x_work, 'playback', file='/usr/share/freeswitch/sounds/en/us/callie/ivr/8000/ivr-stay_on_line_call_answered_momentarily.wav')
        etree.SubElement(x_work, 'hangup')

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return self.return_data(xml)
