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

import os.path
import datetime
import logging
import xmltodict
from xml.parsers.expat import ExpatError
from urllib.parse import unquote
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from .models import XmlCdr
from recordings.models import CallRecording
from tenants.models import Domain
from accounts.models import Extension

logger = logging.getLogger(__name__)


class XmlCdrFunctions():

    def accept_b_leg(self, direction):
        if direction in settings.PBX_CDRH_B_LEG:
            return True
        return False

    def uq(self, url):
        if url:
            return unquote(url)
        return None

    def str2int(self, tmpstr):
        try:
            number = int(tmpstr)
        except (TypeError, ValueError):
            number = 0
        return number

    def str2float(self, tmpstr):
        try:
            number = round(float(tmpstr), 2)
        except (TypeError, ValueError):
            number = 0.0
        return number

    def xml_cdr_import(self, t_uuid, xml):
        if not xml:
            logger.warn('XML CDR request: Contained no data.')
            return False

        if not t_uuid:
            logger.warn('XML CDR request: Contained no UUID.')
            return False

        if t_uuid[:2] == 'a_':
            leg = 'a'
        else:
            leg = 'b'

        try:
            cdr_dict = xmltodict.parse(xml)
        except ExpatError:
            logger.warn('XML CDR request {}: Error parsing xml.'.format(t_uuid))
            cdr_dict = {}

        if 'cdr' not in cdr_dict:  # check root has children
            logger.warn('XML CDR request {}: Contained no cdr element.'.format(t_uuid))
            return False
        nonestr = 'None'
        cdr_variables = cdr_dict['cdr'].get('variables')

        if leg == 'b':
            if not self.accept_b_leg(cdr_variables.get('call_direction', nonestr)):
                return False

        domain_name = cdr_variables.get('domain_name')
        if not domain_name:
            domain_name = cdr_variables.get('sip_req_host')
        if not domain_name:
            logger.warn('XML CDR request {}: No domain name provided.'.format(t_uuid))
            return False

        try:
            d = Domain.objects.get(name=domain_name)
        except ObjectDoesNotExist:
            logger.warn('XML CDR request {}: Unable to find domain {}.'.format(t_uuid, domain_name))
            return False
        except MultipleObjectsReturned:
            logger.warn('XML CDR request {}: Multiple domain record found for {}.'.format(t_uuid, domain_name))
            return False

        extension_found = False
        extension_uuid = cdr_variables.get('extension_uuid')
        if extension_uuid:
            try:
                e = Extension.objects.get(pk=extension_uuid)
            except ObjectDoesNotExist:
                logger.debug('XML CDR request {}: Unable to find extension by uuid {}.'.format(t_uuid, extension_uuid))
            else:
                extension_found = True
        else:
            tmpstr = cdr_variables.get('dialed_user')
            if tmpstr and not extension_found:
                try:
                    e = Extension.objects.get((Q(extension=tmpstr) | Q(number_alias=tmpstr)), domain_id=d.id)
                except ObjectDoesNotExist:
                    logger.debug(
                        'XML CDR request {}: Unable to find extension by number dialled_user {}.'.
                        format(t_uuid, tmpstr)
                        )
                except MultipleObjectsReturned:
                    logger.warn(
                        'XML CDR request {}: Multiple extension records found for dialed_user {}.'.
                        format(t_uuid, tmpstr)
                        )
                else:
                    extension_found = True

            tmpstr = cdr_variables.get('referred_by_user')
            if tmpstr and not extension_found:
                try:
                    e = Extension.objects.get((Q(extension=tmpstr) | Q(number_alias=tmpstr)), domain_id=d.id)
                except ObjectDoesNotExist:
                    logger.debug(
                        'XML CDR request {}: Unable to find extension by number referred_by_user {}.'.
                        format(t_uuid, tmpstr)
                        )
                except MultipleObjectsReturned:
                    logger.warn(
                        'XML CDR request {}: Multiple extension records found for referred_by_user {}.'.
                        format(t_uuid, tmpstr)
                        )
                else:
                    extension_found = True

            tmpstr = cdr_variables.get('last_sent_callee_id_number')
            if tmpstr and not extension_found:
                try:
                    e = Extension.objects.get((Q(extension=tmpstr) | Q(number_alias=tmpstr)), domain_id=d.id)
                except ObjectDoesNotExist:
                    logger.debug(
                        'XML CDR request {}: Unable to find extension by number last_sent_callee_id_number {}.'.
                        format(t_uuid, tmpstr)
                        )
                except MultipleObjectsReturned:
                    logger.warn(
                        'XML CDR request {}: Multiple extension records found for last_sent_callee_id_number {}.'.
                        format(t_uuid, tmpstr)
                        )
                else:
                    extension_found = True

            if not extension_found:
                logger.info('XML CDR request {}: Unable to find extension.'.format(t_uuid))

        caller_id_name = cdr_variables.get('effective_caller_id_name')
        if not caller_id_name:
            caller_id_name = cdr_variables.get('caller_id_name')

        caller_id_number = cdr_variables.get('effective_caller_id_number')
        if not caller_id_number:
            caller_id_name = cdr_variables.get('caller_id_number')

        context = nonestr
        destination_number = '-'
        network_addr = '-'

        callflows = cdr_dict['cdr'].get('callflow')
        if type(callflows) is dict:
            context = self.uq(callflows['caller_profile'].get('context'))
            destination_number = self.uq(callflows['caller_profile'].get('destination_number'))
            network_addr = self.uq(callflows['caller_profile'].get('network_addr'))
            tmpstr = callflows['caller_profile'].get('caller_id_name')
            if tmpstr:
                caller_id_name = tmpstr
                tmpstr = callflows['caller_profile'].get('caller_id_number')
                if tmpstr:
                    caller_id_number = tmpstr

        elif type(callflows) is list:
            i = 0
            for callflow in callflows:
                if i == 0:
                    context = self.uq(callflow['caller_profile'].get('context'))
                    destination_number = self.uq(callflow['caller_profile'].get('destination_number'))
                    network_addr = self.uq(callflow['caller_profile'].get('network_addr'))
                tmpstr = callflow['caller_profile'].get('caller_id_name')
                if tmpstr:
                    caller_id_name = tmpstr
                tmpstr = callflow['caller_profile'].get('caller_id_number')
                if tmpstr:
                    caller_id_number = tmpstr
                i += 1

        tmpstr = cdr_variables.get('last_sent_callee_id_number')
        if tmpstr and leg == 'a':
            destination_number = tmpstr

        tz = timezone.get_current_timezone()

        start_stamp = self.uq(cdr_variables.get('start_stamp'))
        if start_stamp:
            start_time = datetime.datetime.strptime(start_stamp, '%Y-%m-%d %H:%M:%S')
        else:
            start_stamp = datetime.datetime.now()

        start_year = start_time.strftime('%Y')
        start_month = start_time.strftime('%b')
        start_day = start_time.strftime('%d')

        record_path = None
        record_name = None

        if cdr_variables.get('record_session'):
            record_path = self.uq(cdr_variables.get('record_path'))
            record_name = self.uq(cdr_variables.get('record_name'))
            record_length = self.str2int(cdr_variables.get('record_seconds'))
        elif not record_path and cdr_variables.get('last_app', nonestr) == 'record_session':
            record_path = os.path.dirname(self.uq(cdr_variables.get('last_arg')))
            record_name = os.path.basename(self.uq(cdr_variables.get('last_arg')))
            record_length = self.str2int(cdr_variables.get('record_seconds'))
        elif cdr_variables.get('record_name'):
            record_path = self.uq(cdr_variables.get('record_path'))
            record_name = self.uq(cdr_variables.get('record_name'))
            record_length = self.str2int(cdr_variables.get('record_seconds'))
        elif cdr_variables.get('sofia_record_file'):
            record_path = os.path.dirname(self.uq(cdr_variables.get('sofia_record_file')))
            record_name = os.path.basename(self.uq(cdr_variables.get('sofia_record_file')))
            record_length = self.str2int(cdr_variables.get('record_seconds'))
        elif cdr_variables.get('cc_record_filename'):
            record_path = os.path.dirname(self.uq(cdr_variables.get('cc_record_filename')))
            record_name = os.path.basename(self.uq(cdr_variables.get('cc_record_filename')))
            record_length = self.str2int(cdr_variables.get('record_seconds'))
        elif cdr_variables.get('api_on_answer'):
            command = self.uq(cdr_variables.get('api_on_answer'))
            command = command.replace('\n', ' ').split(' ')
            for parts in command:
                if parts[0] == 'uuid_record':
                    recording = parts[3]
                    record_path = os.path.dirname(recording)
                    record_name = os.path.basename(recording)
                    record_length = self.str2int(cdr_variables.get('duration'))
        elif cdr_variables.get('current_application_data'):
            commands = self.uq(cdr_variables.get('current_application_data'))
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
                        record_length = self.str2int(cdr_variables.get('duration'))

        switch_recordings_path = settings.PBX_CDRH_SWITCH_RECORDINGS
        uuid = cdr_variables.get('uuid', nonestr)

        if not record_name:
            bridge_uuid = cdr_variables.get('bridge_uuid', nonestr)
            path = '%s/%s/archive/%s/%s/%s/%s.wav' % (
                    switch_recordings_path, domain_name, start_year, start_month, start_day, bridge_uuid
                    )
            if os.path.exists(path):
                record_path = os.path.dirname(path)
                record_name = os.path.basename(path)
                record_length = self.str2int(cdr_variables.get('duration'))
            path = '%s/%s/archive/%s/%s/%s/%s.mp3' % (
                    switch_recordings_path, domain_name, start_year, start_month, start_day, bridge_uuid
                    )
            if os.path.exists(path):
                record_path = os.path.dirname(path)
                record_name = os.path.basename(path)
                record_length = self.str2int(cdr_variables.get('duration'))

        if not record_name:
            bridge_uuid = cdr_variables.get('bridge_uuid', nonestr)
            path = '%s/%s/archive/%s/%s/%s/%s.wav' % (
                    switch_recordings_path, domain_name, start_year, start_month, start_day, uuid
                    )
            if os.path.exists(path):
                record_path = os.path.dirname(path)
                record_name = os.path.basename(path)
                record_length = self.str2int(cdr_variables.get('duration'))
            path = '%s/%s/archive/%s/%s/%s/%s.mp3' % (
                    switch_recordings_path, domain_name, start_year, start_month, start_day, uuid
                    )
            if os.path.exists(path):
                record_path = os.path.dirname(path)
                record_name = os.path.basename(path)
                record_length = self.str2int(cdr_variables.get('duration'))

        xcdr = XmlCdr(domain_id=d)
#        crec = CallRecording()

        if extension_found:
            xcdr.extension_id=e
        xcdr.call_uuid = cdr_variables.get('call_uuid')
        xcdr.domain_name = domain_name
        xcdr.accountcode = cdr_variables.get('accountcode')
        xcdr.direction = cdr_variables.get('call_direction', nonestr)
        xcdr.context = context
        if caller_id_name:
            xcdr.caller_id_name = unquote(caller_id_name)
        if caller_id_number:
            xcdr.caller_id_number = unquote(caller_id_number)

        xcdr.caller_destination = self.uq(cdr_variables.get('caller_destination'))
        # xcdr.source_number = cdr_variables.get('')
        xcdr.destination_number = destination_number

        xcdr.start_epoch = self.str2int(cdr_variables.get('start_epoch'))
        xcdr.start_stamp = timezone.make_aware(start_time, tz)
        xcdr.answer_epoch = self.str2int(cdr_variables.get('answer'))

        answer_stamp = self.uq(cdr_variables.get('answer_stamp'))
        if answer_stamp:
            answer_time = datetime.datetime.strptime(answer_stamp, '%Y-%m-%d %H:%M:%S')
            xcdr.answer_stamp = timezone.make_aware(answer_time, tz)

        xcdr.end_epoch = self.str2int(cdr_variables.get('end_epoch'))

        end_stamp = self.uq(cdr_variables.get('end_stamp'))
        if end_stamp:
            end_time = datetime.datetime.strptime(end_stamp, '%Y-%m-%d %H:%M:%S')
            xcdr.end_stamp = timezone.make_aware(end_time, tz)

        xcdr.duration = self.str2int(cdr_variables.get('duration'))
        xcdr.mduration = self.str2int(cdr_variables.get('mduration'))
        xcdr.billsec = self.str2int(cdr_variables.get('billsec'))
        xcdr.billmsec = self.str2int(cdr_variables.get('billmsec'))
        xcdr.bridge_uuid = cdr_variables.get('bridge_uuid')
        xcdr.read_codec = cdr_variables.get('read_codec')
        xcdr.read_rate = cdr_variables.get('read_rate')
        xcdr.write_codec = cdr_variables.get('write_codec')
        xcdr.write_rate = cdr_variables.get('write_rate')
        xcdr.remote_media_ip = self.uq(cdr_variables.get('remote_media_ip'))
        xcdr.network_addr = network_addr
        if record_path and record_name:
            if record_length > 0:
                xcdr.record_path = record_path
                xcdr.record_name = record_name
                # record_description = cdr_variables.get('record_description', nonestr)
                populate_call_recordings = settings.PBX_CDRH_POPULATE_CALL_RECORDINGS
                if populate_call_recordings:
                    call_recordings_path = settings.PBX_CDRH_RECORDINGS
                    path_parts = record_path.split('/')[-5:]
                    if len(path_parts) == 5:
                        local_path = '%s/%s' % (switch_recordings_path, '/'.join(path_parts))
                        call_rec_path = '%s/%s' % (call_recordings_path[1:], '/'.join(path_parts))
                        rec_start_stamp = cdr_variables.get('start_stamp', '')
                        try:
                            CallRecording.objects.create(name=record_name,
                                    domain_id=d, year=path_parts[2],
                                    month=path_parts[3], day=path_parts[4],
                                    filename='%s/%s' % (call_rec_path, record_name),
                                    description='%s-%s @ %s' % (caller_id_number, destination_number, rec_start_stamp[-8:]),
                                    updated_by='XML CDR Import')
                        except:
                            pass
        xcdr.leg = leg
        xcdr.pdd_ms = self.str2int(cdr_variables.get(
            'progress_mediamsec'
            )) + self.str2int(cdr_variables.get('progressmsec'))
        xcdr.rtp_audio_in_mos = self.str2float(cdr_variables.get('rtp_audio_in_mos'))
        xcdr.last_app = cdr_variables.get('last_app')
        xcdr.last_arg = self.uq(cdr_variables.get('last_arg'))

        xcdr.missed_call = False
        if (cdr_variables.get('call_direction', nonestr) == 'local' or
                cdr_variables.get('call_direction', nonestr) == 'inbound'):
            if self.str2int(cdr_variables.get('billsec')) == 0:
                xcdr.missed_call = True
        if cdr_variables.get('missed_call', 'false') == 'true':
            xcdr.missed_call = True

        xcdr.cc_side = cdr_variables.get('cc_side')
        xcdr.cc_member_uuid = cdr_variables.get('cc_member_uuid')
        xcdr.cc_queue_joined_epoch = self.str2int(cdr_variables.get('cc_queue_joinded_epoch'))
        xcdr.cc_queue = cdr_variables.get('cc_queue')
        xcdr.cc_member_session_uuid = cdr_variables.get('cc_member_session_id')
        xcdr.cc_agent_uuid = cdr_variables.get('cc_agent_uuid')
        xcdr.cc_agent = cdr_variables.get('cc_agent')
        xcdr.cc_agent_type = cdr_variables.get('cc_agent_type')
        xcdr.cc_agent_bridged = cdr_variables.get('cc_agent_bridged')
        xcdr.cc_queue_answered_epoch = self.str2int(cdr_variables.get('cc_queue_answered_epoch'))
        xcdr.cc_queue_terminated_epoch = self.str2int(cdr_variables.get('cc_queue_terminated_epoch'))
        xcdr.cc_queue_canceled_epoch = self.str2int(cdr_variables.get('cc_queue_canceled_epoch'))
        xcdr.cc_cancel_reason = cdr_variables.get('cc_cancel_reason')
        xcdr.cc_cause = cdr_variables.get('cc_cause')
        xcdr.waitsec = self.str2int(cdr_variables.get('waitsec'))
        xcdr.conference_name = cdr_variables.get('conference_name')
        xcdr.conference_uuid = cdr_variables.get('conference_uuid')
        xcdr.conference_member_id = cdr_variables.get('conference_member_id')
        # xcdr.digits_dialed = cdr_variables.get('digits_dialed')
        pin_number = cdr_variables.get('pin_number')
        if pin_number:
            xcdr.pin_number = unquote(pin_number)

        xcdr.hangup_cause = cdr_variables.get('hangup_cause')
        xcdr.hangup_cause_q850 = self.str2int(cdr_variables.get('hangup_cause_q850'))
        xcdr.sip_hangup_disposition = cdr_variables.get('sip_hangup_disposition')

        format = settings.PBX_CDRH_FORMAT
        if format == 'xml':
            xcdr.xml = xml
        if format == 'json':
            xcdr.json = cdr_dict['cdr']

        xcdr.updated_by = 'system'
        xcdr.save()

        return True

    @staticmethod
    def get_call_status(record):
        call_result = 'None'
        if record.direction == 'inbound' or record.direction == 'local':
            if record.answer_stamp and record.bridge_uuid:
                call_result = _('answered')
            elif record.answer_stamp and not record.bridge_uuid:
                call_result = _('voicemail')
            elif (not record.answer_stamp and not record.bridge_uuid and
                    not record.sip_hangup_disposition == 'send_refuse'):
                call_result = _('cancelled')
            elif (not record.answer_stamp and not record.bridge_uuid and
                    record.sip_hangup_disposition == 'send_refuse'):
                call_result = _('no answer')
            else:
                call_result = _('failed')
        elif record.direction == 'outbound':
            if record.answer_stamp and record.bridge_uuid:
                call_result = _('answered')
            elif not record.answer_stamp and record.bridge_uuid:
                call_result = _('cancelled')
            else:
                call_result = _('failed')

        return call_result
