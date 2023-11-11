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
from tenants.models import Domain
from tenants.pbxsettings import PbxSettings
from accounts.models import Extension, FollowMeDestination
from switch.models import IpRegister
from pbx.pbxsendsmtp import PbxTemplateMessage
from pbx.commonfunctions import shcommand
from ringgroups.ringgroupfunctions import RgFunctions
from accounts.extensionfunctions import ExtFunctions
from recordings.models import Recording


class TestHandler(HttApiHandler):

    def get_data(self):
        if self.exiting:
            return self.return_data('Ok\n')

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


class FollowMeToggleHandler(HttApiHandler):

    def get_variables(self):
        self.var_list = [
        'extension_uuid'
        ]
        self.var_list.extend(self.domain_var_list)

    def get_data(self):
        if self.exiting:
            return self.return_data('Ok\n')

        self.get_domain_variables()
        extension_uuid = self.qdict.get('extension_uuid')
        try:
            e = Extension.objects.get(pk=extension_uuid)
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
                file='ivr/ivr-call_forwarding_has_been_cancelled.wav'
                )
            e.follow_me_enabled = 'false'
        else:
            etree.SubElement(
                x_work, 'playback',
                file='ivr/ivr-call_forwarding_has_been_set.wav'
                )
            e.follow_me_enabled = 'true'

        e.save()
        directory_cache_key = 'directory:%s@%s' % (e.extension, self.domain_name)
        cache.delete(directory_cache_key)
        etree.SubElement(x_work, 'hangup')
        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml


class FollowMeHandler(HttApiHandler):

    def get_variables(self):
        self.var_list = [
        'call_direction',
        'extension_uuid'
        ]
        self.var_list.extend(self.domain_var_list)

    def get_data(self):
        if self.exiting:
            return self.return_data('Ok\n')

        self.get_domain_variables()
        call_direction = self.qdict.get('call_direction', 'local')
        extension_uuid = self.qdict.get('extension_uuid')
        if extension_uuid:
            extf = ExtFunctions(self.domain_uuid, self.domain_name, call_direction, extension_uuid)

        x_root = self.XrootApi()
        etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')
        etree.SubElement(x_work, 'execute', application='set', data='hangup_after_bridge=true')
        etree.SubElement(x_work, 'execute', application='bridge', data=extf.generate_bridge())
        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml


class FailureHandler(HttApiHandler):

    def get_variables(self):
        self.var_list = [
        'originate_disposition',
        'dialed_extension',
        'last_busy_dialed_extension',
        'forward_busy_enabled',
        'forward_busy_destination',
        'forward_busy_destination',
        'forward_no_answer_enabled',
        'forward_no_answer_destination',
        'forward_user_not_registered_enabled',
        'forward_user_not_registered_destination'
        ]
        self.var_list.extend(self.domain_var_list)

    def get_data(self):
        no_work = True
        if self.exiting:
            return self.return_data('Ok\n')

        self.get_domain_variables()
        originate_disposition = self.qdict.get('originate_disposition')
        dialed_extension = self.qdict.get('dialed_extension')
        context = self.qdict.get('Caller-Context')
        if not context:
            context = self.domain_name

        x_root = self.XrootApi()
        etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')

        if originate_disposition == 'USER_BUSY':
            last_busy_dialed_extension = self.qdict.get('last_busy_dialed_extension', '~None~')
            if self.debug:
                self.logger.debug(self.log_header.format(
                    'falurehandler', 'last_busy_dialed_extension %s' % last_busy_dialed_extension
                    ))
            if dialed_extension and last_busy_dialed_extension:
                if not dialed_extension == last_busy_dialed_extension:
                    forward_busy_enabled = self.qdict.get('forward_busy_enabled', 'false')
                    if forward_busy_enabled:
                        if forward_busy_enabled == 'true':
                            forward_busy_destination = self.qdict.get('forward_busy_destination')
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
            forward_no_answer_enabled = self.qdict.get('forward_no_answer_enabled')
            if forward_no_answer_enabled:
                if forward_no_answer_enabled == 'true':
                    forward_no_answer_destination = self.qdict.get('forward_no_answer_destination')
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
            forward_user_not_registered_enabled = self.qdict.get('forward_user_not_registered_enabled')
            if forward_user_not_registered_enabled:
                if forward_user_not_registered_enabled == 'true':
                    forward_user_not_registered_destination = self.qdict.get(
                        'forward_user_not_registered_destination'
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
        return xml


class HangupHandler(HttApiHandler):

    def get_data(self):

        self.get_domain_variables()
        self.get_language_variables()

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


class RegisterHandler(HttApiHandler):

    def get_data(self):
        ip_address = self.qdict.get('network-ip', '192.168.42.1')
        status = self.qdict.get('status', 'N/A')
        if status.startswith('Registered'):
            ip, created = IpRegister.objects.update_or_create(address=ip_address)
            if created:
                if ':' in ip.address:
                    shcommand(["/usr/local/bin/fw-add-ipv6-sip-customer-list.sh", ip.address])
                else:
                    shcommand(["/usr/local/bin/fw-add-ipv4-sip-customer-list.sh", ip.address])

        return self.return_data('Ok\n')


class RingGroupHandler(HttApiHandler):

    def get_variables(self):
        self.var_list = ['ring_group_uuid']
        self.var_list.extend(self.domain_var_list)

    def get_data(self):
        if self.exiting:
            return self.return_data('Ok\n')

        self.get_domain_variables()

        ringgroup_uuid = self.qdict.get('ring_group_uuid')
        try:
            rgf = RgFunctions(self.domain_uuid, self.domain_name, ringgroup_uuid)
        except:
            return self.return_data(self.error_hangup('R1001'))

        x_root = self.XrootApi()
        etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')
        etree.SubElement(x_work, 'execute', application='bridge', data=rgf.generate_bridge())
        toa = rgf.generate_timeout_action()
        if toa[0] == 'hangup':
            etree.SubElement(x_work, toa[0])
        else:
            etree.SubElement(x_work, 'execute', application=toa[0], data=toa[1])

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml


class RecordingsHandler(HttApiHandler):

    def get_variables(self):
        self.var_list = ['pin_number', 'recording_prefix']
        self.var_list.extend(self.domain_var_list)

    def get_data(self):
        self.get_domain_variables()
        if self.getfile:
            rec_file_exists = True
            # workaround since freeswitch 10 httapi record prepends a UUID to the filename
            # this strips it on the known part of the name 'recording'
            received_file_name = 'recording%s' % self.fdict['rd_input'].name.rsplit('recording', 1)[1]
            try:
                rec = Recording.objects.get(name=received_file_name)
            except Recording.DoesNotExist:
                rec_file_exists = False
                d = Domain.objects.get(pk=self.domain_uuid)
                rec = Recording.objects.create(name=received_file_name, domain_id=d, 
                        description='via recordings (%s)' % self.qdict.get('Caller-Destination-Number', ''))

            if rec_file_exists:
                rec.filename.delete(save=False)
            rec.filename.save(received_file_name, self.fdict['rd_input'])

        if self.exiting:
            return self.return_data('Ok\n')

        x_root = self.XrootApi()
        etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')

        if 'next_action' in self.session.json:
            next_action =  self.session.json['next_action']
            if next_action == 'chk-pin':
                pin_number = self.session.json['pin_number']
                if pin_number == self.qdict.get('pb_input', ''):

                    self.session.json['next_action'] = 'record'
                    self.session.save()
                    x_work.append(self.play_and_get_digits('ivr/ivr-id_number.wav'))
                else:
                    etree.SubElement(x_work, 'playback', file='phrase:voicemail_fail_auth:#')
                    etree.SubElement(x_work, 'hangup')

            elif next_action == 'record':
                rec_no = self.qdict.get('pb_input', '')
                rec_prefix = self.qdict.get('recording_prefix', 'recording')
                self.get_sounds_variables()
                rec_file = '%s%s.wav' % (rec_prefix, rec_no)

                self.session.json['rec_file'] = '%s/%s/%s' % (self.recordings_dir, self.domain_name, rec_file)
                self.session.json['next_action'] = 'review'
                self.session.save()
                etree.SubElement(x_work, 'playback', file='ivr/ivr-recording_started.wav')
                x_work.append(self.record_and_get_digits(rec_file))

            elif next_action == 'review':
                rec_file = self.session.json['rec_file']
                self.session.json['next_action'] = 'rerecord'
                self.session.save()
                etree.SubElement(x_work, 'pause', milliseconds='1000')
                etree.SubElement(x_work, 'playback', file=rec_file)
                etree.SubElement(x_work, 'pause', milliseconds='500')
                etree.SubElement(x_work, 'playback', file='voicemail/vm-press.wav')
                etree.SubElement(x_work, 'playback', file='digits/1.wav')
                x_work.append(self.play_and_get_digits('voicemail/vm-rerecord.wav', 'pb_input', '~\\d{1}'))

            elif next_action == 'rerecord':
                re_rec = self.qdict.get('pb_input', '')
                if re_rec == '1':
                    rec_file = self.session.json['rec_file']
                    self.session.json['next_action'] = 'record'
                    self.session.save()
                    etree.SubElement(x_work, 'continue')
                else:
                    etree.SubElement(x_work, 'playback', file='ivr/ivr-recording_saved.wav')
                    etree.SubElement(x_work, 'hangup')
        else:
            pin_number = self.qdict.get('pin_number')
            if not pin_number:
                return self.error_hangup('R2001')

            self.session.json['pin_number'] = pin_number
            self.session.json['next_action'] = 'chk-pin'
            self.session.save()
            x_work.append(self.play_and_get_digits('phrase:voicemail_enter_pass:#'))

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml
