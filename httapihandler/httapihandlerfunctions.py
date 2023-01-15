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
# from django.db.models import Q
from .models import HttApiSession
# from tenants.models import Domain
from tenants.pbxsettings import PbxSettings
from accounts.models import Extension, FollowMeDestination
from switch.switchfunctions import IpFunctions
from pbx.pbxsendsmtp import PbxTemplateMessage


class HttApiHandlerFunctions():
    log_header = 'HttApi Handler: {}: {}'

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
            self.logger.debug(self.log_header.format('request\n', self.qdict))
        self.domain_uuid = None
        self.domain_name = None
        self.extension_uuid = None
        self.default_language = None
        self.default_dialiect = None
        self.default_voice = None
        self.sounds_dir = None
        self.sounds_tuple = None

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
        etree.SubElement(
            x_work, 'execute', application='set',
            data='api_result=${uuid_display(%s \'%s\')}' % (self.session_id, message)
            )
        etree.SubElement(x_work, 'execute', application='sleep', data='2000')
        etree.SubElement(x_work, 'hangup')
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

    def get_httapi_session(self, name='None'):
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
        self.domain_uuid = self.qdict.get('variable_domain_uuid')
        self.domain_name = self.qdict.get('variable_domain_name')
        self.extension_uuid = self.qdict.get('variable_extension_uuid')
        self.default_language = self.qdict.get('variable_default_language', 'en')
        self.default_dialect = self.qdict.get('variable_default_dialiect', 'us')
        self.default_voice = self.qdict.get('variable_default_voice', 'callie')
        self.sounds_dir = self.qdict.get('sounds_dir', '/usr/share/freeswitch/sounds')
        self.sounds_fullpath = '{}/{}/{}/{}'.format(
            self.sounds_dir, self.default_language, self.default_dialiect, self.default_voice
            )
        return


class TestHandler(HttApiHandlerFunctions):

    def get_data(self):
        if self.exiting:
            return self.return_data('Ok\n')

        # don't need to do this for this simple scenario but it tests the session mechanism
        self.get_httapi_session('Test')

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
        return self.return_data(xml)


class FollowMeToggleHandler(HttApiHandlerFunctions):

    def get_data(self):
        if self.exiting:
            return self.return_data('Ok\n')

        self.get_common_variables()
        try:
            e = Extension.objects.get(pk=self.extension_uuid)
        except Extension.DoesNotExist:
            self.logger.debug(self.log_header.format('follow me toggle', 'Extn UUID not found'))
            return self.return_data(self.error_hangup('E1001'))

        x_root = self.XrootApi()
        etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')
        etree.SubElement(x_work, 'execute', application='sleep', data='2000')
        if e.follow_me_enabled == 'true':
            etree.SubElement(
                x_work, 'playback',
                file='{}/ivr/ivr-call_forwarding_has_been_cancelled.wav'.format(self.sounds_fullpath)
                )
            e.follow_me_enabled = 'false'
        else:
            etree.SubElement(
                x_work, 'playback',
                file='{}/ivr/ivr-call_forwarding_has_been_set.wav'.format(self.sounds_fullpath)
                )
            e.follow_me_enabled = 'true'

        e.save()
        directory_cache_key = 'directory:%s@%s' % (e.extension, self.domain_name)
        cache.delete(directory_cache_key)
        etree.SubElement(x_work, 'hangup')
        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return self.return_data(xml)


class FollowMeHandler(HttApiHandlerFunctions):

    def get_data(self):
        if self.exiting:
            return self.return_data('Ok\n')

        # don't need to do this for this simple scenario but it tests the session mechanism
        self.get_httapi_session('Follow Me')
        self.get_common_variables()
        fmd = FollowMeDestination.objects.select_related('extension_id').filter(extension_id=self.extension_uuid)

        print(fmd)

        x_root = self.XrootApi()
        etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')
        etree.SubElement(x_work, 'execute', application='answer')
        etree.SubElement(
            x_work, 'playback',
            file='/usr/share/freeswitch/sounds/en/us/callie/ivr/8000/ivr-stay_on_line_call_answered_momentarily.wav'
            )
        etree.SubElement(x_work, 'hangup')

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return self.return_data(xml)


class FailureHandler(HttApiHandlerFunctions):

    def get_data(self):
        no_work = True
        if self.exiting:
            return self.return_data('Ok\n')

        self.get_common_variables()
        originate_disposition = self.qdict.get('variable_originate_disposition')
        dialed_extension = self.qdict.get('variable_dialed_extension')
        context = self.qdict.get('Caller-Context')
        if not context:
            context = self.domain_name

        x_root = self.XrootApi()
        etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')

        if originate_disposition == 'USER_BUSY':
            last_busy_dialed_extension = self.qdict.get('variable_last_busy_dialed_extension', '~None~')
            if self.debug:
                self.logger.debug(self.log_header.format(
                    'falurehandler', 'last_busy_dialed_extension %s' % last_busy_dialed_extension
                    ))
            if dialed_extension and last_busy_dialed_extension:
                if not dialed_extension == last_busy_dialed_extension:
                    forward_busy_enabled = self.qdict.get('variable_forward_busy_enabled', 'false')
                    if forward_busy_enabled:
                        if forward_busy_enabled == 'true':
                            forward_busy_destination = self.qdict.get('variable_forward_busy_destination')
                            no_work = False
                            if forward_busy_destination:
                                etree.SubElement(
                                    x_work, 'execute', application='set',
                                    data='last_busy_dialed_extension=%s' % dialed_extension
                                    )
                                x_log = etree.SubElement(x_work, 'log', level='NOTICE')
                                x_log.text = 'forwarding on busy to: %s' % forward_busy_destination
                                etree.SubElement(
                                    x_work, 'execute', application='transfer',
                                    data='%s XML %s' % (forward_busy_destination, context)
                                    )
                            else:
                                x_log = etree.SubElement(x_work, 'log', level='NOTICE')
                                x_log.text = 'forwarding on busy with empty destination: hangup(USER_BUSY)'
                                etree.SubElement(x_work, 'hangup', cause='USER_BUSY')
            if no_work:
                etree.SubElement(x_work, 'hangup', cause='USER_BUSY')

        elif originate_disposition == 'NO_ANSWER':
            forward_no_answer_enabled = self.qdict.get('variable_forward_no_answer_enabled')
            if forward_no_answer_enabled:
                if forward_no_answer_enabled == 'true':
                    forward_no_answer_destination = self.qdict.get('variable_forward_no_answer_destination')
                    no_work = False
                    if forward_no_answer_destination:
                        x_log = etree.SubElement(x_work, 'log', level='NOTICE')
                        x_log.text = 'forwarding on no answer to: %s' % forward_no_answer_destination
                        etree.SubElement(
                            x_work, 'execute', application='transfer',
                            data='%s XML %s' % (forward_no_answer_destination, context)
                            )
                    else:
                        x_log = etree.SubElement(x_work, 'log', level='NOTICE')
                        x_log.text = 'forwarding on no answer with empty destination: hangup(NO_ANSWER)'
                        etree.SubElement(x_work, 'hangup', cause='NO_ANSWER')
            if no_work:
                etree.SubElement(x_work, 'hangup', cause='NO_ANSWER')

        elif originate_disposition == 'USER_NOT_REGISTERED':
            forward_user_not_registered_enabled = self.qdict.get('variable_forward_user_not_registered_enabled')
            if forward_user_not_registered_enabled:
                if forward_user_not_registered_enabled == 'true':
                    forward_user_not_registered_destination = self.qdict.get(
                        'variable_forward_user_not_registered_destination'
                        )
                    no_work = False
                    if forward_user_not_registered_destination:
                        x_log = etree.SubElement(x_work, 'log', level='NOTICE')
                        x_log.text = 'forwarding on not registerd to: %s' % forward_user_not_registered_destination
                        etree.SubElement(
                            x_work, 'execute', application='transfer',
                            data='%s XML %s' % (forward_user_not_registered_destination, context)
                            )
                    else:
                        x_log = etree.SubElement(x_work, 'log', level='NOTICE')
                        x_log.text = 'forwarding on user not registered with empty destination: hangup(NO_ANSWER)'
                        etree.SubElement(x_work, 'hangup', cause='NO_ANSWER')
            if no_work:
                etree.SubElement(x_work, 'hangup', cause='NO_ANSWER')

        elif originate_disposition == 'SUBSCRIBER_ABSENT':
            no_work = False
            x_log = etree.SubElement(x_work, 'log', level='NOTICE')
            x_log.text = 'subscriber absent: %s' % dialed_extension
            etree.SubElement(x_work, 'hangup', cause='UNALLOCATED_NUMBER')

        elif originate_disposition == 'CALL_REJECTED':
            no_work = False
            x_log = etree.SubElement(x_work, 'log', level='NOTICE')
            x_log.text = 'call rejected'
            etree.SubElement(x_work, 'hangup')

        if no_work:
            etree.SubElement(x_work, 'hangup')

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return self.return_data(xml)


class HangupHandler(HttApiHandlerFunctions):

    def get_data(self):

        self.get_common_variables()

        missed_call_app  = self.qdict.get('missed_call_app')        # noqa: E221
        missed_call_data = self.qdict.get('missed_call_data')       # noqa: E221
        caller_id_name   = self.qdict.get('caller_id_name', ' ')    # noqa: E221
        caller_id_number = self.qdict.get('caller_id_number', ' ')  # noqa: E221
        sip_to_user      = self.qdict.get('sip_to_user', ' ')       # noqa: E221
        dialed_user      = self.qdict.get('dialed_user', ' ')       # noqa: E221

        if not missed_call_app:
            return self.return_data('Ok\n')
        if not missed_call_app == 'email':
            return self.return_data('Ok\n')
        if not missed_call_data:
            return self.return_data('Ok\n')

        m = PbxTemplateMessage()
        template = m.GetTemplate(
            self.domain_uuid, '%s-%s' % (self.default_language, self.default_dialect),
            'missed', 'default'
            )
        if not template[0]:
            self.logger.warn(self.log_header.format('hangup', 'Email Template mising'))
            return self.return_data('Ok\n')

        subject = template[0].format(
                caller_id_name=caller_id_name, caller_id_number=caller_id_number,
                sip_to_user=sip_to_user, dialed_user=dialed_user
                )
        body = template[1].format(
                caller_id_name=caller_id_name, caller_id_number=caller_id_number,
                sip_to_user=sip_to_user, dialed_user=dialed_user
                )
        out = m.Send(missed_call_data, subject, body, template[2])
        if self.debug or not out[0]:
            self.logger.warn(self.log_header.format('hangup', out[1]))

        return self.return_data('Ok\n')


class RegisterHandler(HttApiHandlerFunctions):

    def get_data(self):
        ip_address = self.qdict.get('network-ip', '192.168.42.1')
        status = self.qdict.get('status', 'N/A')
        if status.startswith('Registered'):
            IpFunctions().update_ip(ip_address)
        return self.return_data('Ok\n')
