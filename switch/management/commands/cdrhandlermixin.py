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
import datetime
import logging
from django.utils import timezone
from django.db.models import Q
from xmlcdr.models import XmlCdr, CallTimeline
from recordings.models import CallRecording
from accounts.models import Extension

logger = logging.getLogger(__name__)


class CdrHandlerMixin():

    def handle_cdr(self, event, call_direction, q850):
        core_uuid = event.get('Core-UUID')
        t_uuid = event.get('Channel-Call-UUID', self.nonstr)

        if event.get('Channel-HIT-Dialplan', 'false') == 'true':
            leg = 'a'
        else:
            leg = 'b'
            if not call_direction in self.b_leg:
                return False

        domain_name = self.get_domain_name(event)
        if not domain_name:
            logger.warn('EVENT CDR request {}: No domain name provided.'.format(t_uuid))
            return False

        d = self.get_domain(domain_name)
        if not d:
            logger.warn('EVENT CDR request {}: Unable to find domain {}.'.format(t_uuid, domain_name))
            return False

        extension_found = False
        extension_uuid = event.get('variable_extension_uuid')
        if extension_uuid:
            try:
                e = Extension.objects.get(pk=extension_uuid)
            except Extension.DoesNotExist:
                logger.debug('EVENT CDR request {}: Unable to find extension by uuid {}.'.format(t_uuid, extension_uuid))
            else:
                extension_found = True
        else:
            tmpstr = event.get('variable_dialed_user')
            if tmpstr and not extension_found:
                try:
                    e = Extension.objects.get((Q(extension=tmpstr) | Q(number_alias=tmpstr)), domain_id=d.id)
                except Extension.DoesNotExist:
                    logger.debug(
                        'EVENT CDR request {}: Unable to find extension by number dialled_user {}.'.
                        format(t_uuid, tmpstr)
                        )
                except Extension.MultipleObjectsReturned:
                    logger.warn(
                        'EVENT CDR request {}: Multiple extension records found for dialed_user {}.'.
                        format(t_uuid, tmpstr)
                        )
                else:
                    extension_found = True

            tmpstr = event.get('variable_referred_by_user')
            if tmpstr and not extension_found:
                try:
                    e = Extension.objects.get((Q(extension=tmpstr) | Q(number_alias=tmpstr)), domain_id=d.id)
                except Extension.DoesNotExist:
                    logger.debug(
                        'EVENT CDR request {}: Unable to find extension by number referred_by_user {}.'.
                        format(t_uuid, tmpstr)
                        )
                except Extension.MultipleObjectsReturned:
                    logger.warn(
                        'EVENT CDR request {}: Multiple extension records found for referred_by_user {}.'.
                        format(t_uuid, tmpstr)
                        )
                else:
                    extension_found = True

            tmpstr = event.get('variable_last_sent_callee_id_number')
            if tmpstr and not extension_found:
                try:
                    e = Extension.objects.get((Q(extension=tmpstr) | Q(number_alias=tmpstr)), domain_id=d.id)
                except Extension.DoesNotExist:
                    logger.debug(
                        'EVENT CDR request {}: Unable to find extension by number last_sent_callee_id_number {}.'.
                        format(t_uuid, tmpstr)
                        )
                except Extension.MultipleObjectsReturned:
                    logger.warn(
                        'EVENT CDR request {}: Multiple extension records found for last_sent_callee_id_number {}.'.
                        format(t_uuid, tmpstr)
                        )
                else:
                    extension_found = True

            if not extension_found:
                logger.info('EVENT CDR request {}: Unable to find extension.'.format(t_uuid))

        caller_id_name = event.get('variable_effective_caller_id_name')
        if not caller_id_name:
            caller_id_name = event.get('variable_caller_id_name')

        caller_id_number = event.get('variable_effective_caller_id_number')
        if not caller_id_number:
            caller_id_name = event.get('variable_caller_id_number')

        context = event.get('Caller-Context',self.nonstr)
        destination_number = event.get('Caller-Destination-Number', '-')
        network_addr = event.get('Caller-Network-Addr', '-')

        tmpstr = event.get('variable_last_sent_callee_id_number')
        if tmpstr and leg == 'a' and not call_direction in self.b_leg:
            destination_number = tmpstr

        tz = timezone.get_current_timezone()

        start_stamp = event.get('variable_start_stamp')
        if start_stamp:
            start_time = datetime.datetime.strptime(start_stamp, '%Y-%m-%d %H:%M:%S')
        else:
            start_stamp = datetime.datetime.now()

        start_year = start_time.strftime('%Y')
        start_month = start_time.strftime('%b')
        start_day = start_time.strftime('%d')

        record_path = None
        record_name = None

        if event.get('variable_record_session'):
            record_path = event.get('variable_record_path')
            record_name = event.get('variable_record_name')
            record_length = self.str2int(event.get('variable_record_seconds'))
        elif not record_path and event.get('variable_last_app', self.nonstr) == 'record_session':
            record_path = os.path.dirname(event.get('variable_last_arg'))
            record_name = os.path.basename(event.get('variable_last_arg'))
            record_length = self.str2int(event.get('variable_record_seconds'))
        elif event.get('variable_record_name'):
            record_path = event.get('variable_record_path')
            record_name = event.get('variable_record_name')
            record_length = self.str2int(event.get('variable_record_seconds'))
        elif event.get('variable_sofia_record_file'):
            record_path = os.path.dirname(event.get('variable_sofia_record_file'))
            record_name = os.path.basename(event.get('variable_sofia_record_file'))
            record_length = self.str2int(event.get('variable_record_seconds'))
        elif event.get('variable_cc_record_filename'):
            record_path = os.path.dirname(event.get('variable_cc_record_filename'))
            record_name = os.path.basename(event.get('variable_cc_record_filename'))
            record_length = self.str2int(event.get('variable_record_seconds'))
        elif event.get('variable_api_on_answer'):
            command = self.uq(event.get('variable_api_on_answer'))
            command = command.replace('\n', ' ').split(' ')
            for parts in command:
                if parts[0] == 'uuid_record':
                    recording = parts[3]
                    record_path = os.path.dirname(recording)
                    record_name = os.path.basename(recording)
                    record_length = self.str2int(event.get('variable_duration'))
        elif event.get('variable_current_application_data'):
            commands = event.get('variable_current_application_data')
            commands = commands.split(',')
            for command in commands:
                cmd = command.split('=')
                if cmd[0] == 'api_on_answer':
                    a = cmd[1].split(']')
                    parts = a[0].replace(',', '').split(' ')
                    if parts[0] == 'uuid_record':
                        recording = parts[3]
                        record_path = os.path.dirname(recording)
                        record_name = os.path.basename(recording)
                        record_length = self.str2int(event.get('variable_duration'))

        uuid = event.get('variable_uuid', self.nonstr)

        if not record_name:
            bridge_uuid = event.get('variable_bridge_uuid', self.nonstr)
            path = '%s/%s/archive/%s/%s/%s/%s.wav' % (
                    self.switch_recordings_path, domain_name, start_year, start_month, start_day, bridge_uuid
                    )
            if os.path.exists(path):
                record_path = os.path.dirname(path)
                record_name = os.path.basename(path)
                record_length = self.str2int(event.get('variable_duration'))
            path = '%s/%s/archive/%s/%s/%s/%s.mp3' % (
                    self.switch_recordings_path, domain_name, start_year, start_month, start_day, bridge_uuid
                    )
            if os.path.exists(path):
                record_path = os.path.dirname(path)
                record_name = os.path.basename(path)
                record_length = self.str2int(event.get('variable_duration'))

        if not record_name:
            bridge_uuid = event.get('variable_bridge_uuid', self.nonstr)
            path = '%s/%s/archive/%s/%s/%s/%s.wav' % (
                    self.switch_recordings_path, domain_name, start_year, start_month, start_day, uuid
                    )
            if os.path.exists(path):
                record_path = os.path.dirname(path)
                record_name = os.path.basename(path)
                record_length = self.str2int(event.get('variable_duration'))
            path = '%s/%s/archive/%s/%s/%s/%s.mp3' % (
                    self.switch_recordings_path, domain_name, start_year, start_month, start_day, uuid
                    )
            if os.path.exists(path):
                record_path = os.path.dirname(path)
                record_name = os.path.basename(path)
                record_length = self.str2int(event.get('variable_duration'))

        xcdr = XmlCdr(domain_id=d, core_uuid=core_uuid)
        if extension_found:
            xcdr.extension_id=e
        xcdr.call_uuid = event.get('Unique-ID')
        xcdr.domain_name = domain_name
        xcdr.accountcode = event.get('variable_accountcode')
        xcdr.direction = event.get('variable_call_direction', self.nonstr)
        xcdr.context = context
        if caller_id_name:
            xcdr.caller_id_name = caller_id_name
        if caller_id_number:
            xcdr.caller_id_number = caller_id_number
        caller_destination = event.get('variable_caller_destination')
        if not caller_destination:
            caller_destination = event.get('Caller-Destination-Number')
        xcdr.caller_destination = caller_destination
        # xcdr.source_number = event.get('variable_')
        xcdr.destination_number = destination_number

        xcdr.start_epoch = self.str2int(event.get('variable_start_epoch'))
        xcdr.start_stamp = timezone.make_aware(start_time, tz)
        xcdr.answer_epoch = self.str2int(event.get('variable_answer'))

        answer_stamp = event.get('variable_answer_stamp')
        if answer_stamp:
            answer_time = datetime.datetime.strptime(answer_stamp, '%Y-%m-%d %H:%M:%S')
            xcdr.answer_stamp = timezone.make_aware(answer_time, tz)

        xcdr.end_epoch = self.str2int(event.get('variable_end_epoch'))

        end_stamp = event.get('variable_end_stamp')
        if end_stamp:
            end_time = datetime.datetime.strptime(end_stamp, '%Y-%m-%d %H:%M:%S')
            xcdr.end_stamp = timezone.make_aware(end_time, tz)

        xcdr.duration = self.str2int(event.get('variable_duration'))
        xcdr.mduration = self.str2int(event.get('variable_mduration'))
        xcdr.billsec = self.str2int(event.get('variable_billsec'))
        xcdr.billmsec = self.str2int(event.get('variable_billmsec'))
        xcdr.bridge_uuid = event.get('variable_bridge_uuid')
        xcdr.read_codec = event.get('variable_read_codec')
        xcdr.read_rate = event.get('variable_read_rate')
        xcdr.write_codec = event.get('variable_write_codec')
        xcdr.write_rate = event.get('variable_write_rate')
        xcdr.remote_media_ip = event.get('variable_remote_media_ip')
        xcdr.network_addr = network_addr
        if record_path and record_name:
            if record_length > 0:
                xcdr.record_path = record_path
                xcdr.record_name = record_name
                # record_description = event.get('variable_record_description', self.nonstr)
                if self.pop_call_recordings:
                    path_parts = record_path.split('/')[-5:]
                    if len(path_parts) == 5:
                        local_path = '%s/%s' % (self.switch_recordings_path, '/'.join(path_parts))
                        call_rec_path = '%s/%s' % (self.call_recordings_path.lstrip('/'), '/'.join(path_parts))
                        rec_start_stamp = event.get('variable_start_stamp', '')
                        try:
                            CallRecording.objects.create(name=record_name,
                                    domain_id=d, year=path_parts[2],
                                    month=path_parts[3], day=path_parts[4],
                                    filename='%s/%s' % (call_rec_path, record_name),
                                    description='%s-%s @ %s' % (caller_id_number, destination_number, rec_start_stamp[-8:]),
                                    updated_by=self.updated_by)
                        except:
                            pass

        xcdr.leg = leg
        xcdr.pdd_ms = self.str2int(event.get(
            'progress_mediamsec'
            )) + self.str2int(event.get('variable_progressmsec'))
        xcdr.rtp_audio_in_mos = self.str2float(event.get('variable_rtp_audio_in_mos'))
        xcdr.last_app = event.get('variable_last_app')
        xcdr.last_arg = event.get('variable_last_arg')

        xcdr.missed_call = False
        if (event.get('variable_call_direction', self.nonstr) == 'local' or
                event.get('variable_call_direction', self.nonstr) == 'inbound'):
            if self.str2int(event.get('variable_billsec')) == 0:
                xcdr.missed_call = True
        if event.get('variable_missed_call', 'false') == 'true':
            xcdr.missed_call = True

        xcdr.cc_side = event.get('variable_cc_side')
        xcdr.cc_member_uuid = event.get('variable_cc_member_uuid')
        xcdr.cc_queue_joined_epoch = self.str2int(event.get('variable_cc_queue_joinded_epoch'))
        xcdr.cc_queue = event.get('variable_cc_queue')
        xcdr.cc_member_session_uuid = event.get('variable_cc_member_session_id')
        xcdr.cc_agent_uuid = event.get('variable_cc_agent_uuid')
        xcdr.cc_agent = event.get('variable_cc_agent')
        xcdr.cc_agent_type = event.get('variable_cc_agent_type')
        xcdr.cc_agent_bridged = event.get('variable_cc_agent_bridged')
        xcdr.cc_queue_answered_epoch = self.str2int(event.get('variable_cc_queue_answered_epoch'))
        xcdr.cc_queue_terminated_epoch = self.str2int(event.get('variable_cc_queue_terminated_epoch'))
        xcdr.cc_queue_canceled_epoch = self.str2int(event.get('variable_cc_queue_canceled_epoch'))
        xcdr.cc_cancel_reason = event.get('variable_cc_cancel_reason')
        xcdr.cc_cause = event.get('variable_cc_cause')
        xcdr.waitsec = self.str2int(event.get('variable_waitsec'))
        xcdr.conference_name = event.get('variable_conference_name')
        xcdr.conference_uuid = event.get('variable_conference_uuid')
        xcdr.conference_member_id = event.get('variable_conference_member_id')
        # xcdr.digits_dialed = event.get('variable_digits_dialed')
        pin_number = event.get('variable_pin_number')
        if pin_number:
            xcdr.pin_number = pin_number

        xcdr.hangup_cause = event.get('variable_hangup_cause')
        xcdr.hangup_cause_q850 = self.str2int(q850)
        xcdr.sip_hangup_disposition = event.get('variable_sip_hangup_disposition')

        if self.cdrformat == 'json':
            xcdr.json = event

        xcdr.updated_by = self.updated_by
        xcdr.save()
        return

