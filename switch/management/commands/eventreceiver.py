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
#import time
#import random
import logging
#import pika
#import socket
#import functools
import json
from pika import BasicProperties as PikaBasicProperties
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.management.base import BaseCommand
from switch.models import IpRegister
from tenants.models import DefaultSetting, Domain
from xmlcdr.models import XmlCdr
from accounts.models import Extension
from pbx.commonfunctions import shcommand
from pbx.scripts.resources.pbx.amqpconnection import AmqpConnection


logger = logging.getLogger(__name__)
#logging.getLogger("pika").setLevel(logging.WARNING)


class Command(BaseCommand):
    help = 'PBX Event Receiver'
    nonstr = 'none'
    debug = False
    mb_key_host = 'message_broker'
    mb_key_port = 'message_broker_port'
    mb_key_user = 'message_broker_user'
    mb_key_pass = 'message_broker_password'
    mb_key_adhoc = 'message_broker_adhoc_publish'

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

    def on_message(self, channel, method, properties, body):
        msg = body.decode('utf8')
        if self.debug:
            if logger is not None:
                logger.debug('Event Receiver: %s', msg)
            print(msg)
        event = json.loads(msg)
        event_name = event.get('Event-Name', self.nonstr)
        event_subclass = event.get('Event-Subclass', self.nonstr)
        if event_name == 'CHANNEL_HANGUP_COMPLETE':
            self.handle_cdr(event)
        elif event_name == 'CUSTOM':
            if event.get('Event-Subclass', self.nonstr) == 'sofia::register':
                self.handle_register(channel, event)
            if event.get('Event-Subclass', self.nonstr) == 'callcenter::info':
                self.handle_callcentreinfo(event)

    def handle(self, *args, **kwargs):
        mb = {self.mb_key_host: '127.0.0.1', self.mb_key_port: 5672,
            self.mb_key_pass: 'djangopbx-insecure',
            self.mb_key_user: 'guest', self.mb_key_adhoc: False}
        mbl = DefaultSetting.objects.filter(
                category='cluster',
                subcategory__istartswith='message_broker',
                enabled='true',
                )
        for mbr in mbl:
            if mbr.value_type == 'text':
                mb[mbr.subcategory] = mbr.value
            if mbr.value_type == 'numeric':
                try:
                    mb[mbr.subcategory] = int(mbr.value)
                except ValueError:
                    pass
            if mbr.value_type == 'boolean':
                mb[mbr.subcategory] = (True if mbr.value == 'true' else False)
        del mbl
        self.message_broker_adhoc_publish = mb[self.mb_key_adhoc]
        bleg = DefaultSetting.objects.filter(
                category='cdr',
                subcategory='b_leg',
                value_type='array',
                enabled='true',
                )
        self.b_leg = []
        for leg in bleg:
            self.b_leg.append(leg.value)
        del bleg
        fmt = DefaultSetting.objects.filter(
                category='cdr',
                subcategory='format',
                value_type='text',
                enabled='true',
                )
        if fmt:
            self.cdrformat = fmt[0].value
        del fmt
        srp = DefaultSetting.objects.filter(
                category='switch',
                subcategory='recordings',
                value_type='dir',
                enabled='true',
                )
        if srp:
            self.switch_recordings_path = srp[0].value
        del srp

        self.firewall_event_template = '{\"Event-Name\":\"FIREWALL\", \"Action\":\"add\", \"IP-Type\":\"%s\",\"Fw-List\":\"sip-customer\", \"IP-Address\":\"%s\"}' # noqa: E501
        self.mq = AmqpConnection(mb[self.mb_key_host], mb[self.mb_key_port],
                                    mb[self.mb_key_user], mb[self.mb_key_pass])
        self.mq.connect()
        self.mq.setup_queues()
        self.mq.consume(self.on_message)


    def handle_callcentreinfo(self, event):
        pass

    def handle_register(self, channel, event):
        if event.get('status', 'N/A').startswith('Registered'):
            ip_address = event.get('network-ip', '192.168.42.1')
            ip, created = IpRegister.objects.update_or_create(address=ip_address, defaults={"status": 1})
            if created:
                ip_type = 'ipv4'
                if ':' in ip.address:
                    ip_type = 'ipv6'
                shcommand(['/usr/local/bin/fw-add-%s-sip-customer-list.sh' % ip_type, ip.address])
                if self.message_broker_adhoc_publish:
                    firewall_routing = 'DjangoPBX.%s.FIREWALL.add.%s' % (self.mq.hostname, ip_type)
                    payload = self.firewall_event_template % (ip_type, ip.address)
                    try:
                        channel.basic_publish('TAP.Firewall', firewall_routing, payload.encode(),
                            properties=PikaBasicProperties(delivery_mode=2), # Delivery Mode 2 for persistent
                            )
                    except:
                        logger.warn('EVENT Register {}: Unable send TAP.Firewall message {}.'.format(ip.address, firewall_routing))

    def handle_cdr(self, event):
        t_uuid = event.get('Channel-Call-UUID', self.nonstr)
        call_direction = event.get('variable_call_direction', self.nonstr)
        q850 = event.get('variable_hangup_cause_q850', self.nonstr)
        if q850 == '502': # LOSE_RACE (call connected elsewhere)
            return False
        if q850 == '605': # PICKED_OFF (intercepting it from another extension)
            return False
        if q850 == '101': # WRONG_CALL_STATE
            if call_direction == self.nonstr:
                return False

        domain_name = event.get('variable_domain_name')
        if not domain_name:
            domain_name = event.get('variable_sip_req_host')
        if not domain_name:
            logger.warn('EVENT CDR request {}: No domain name provided.'.format(t_uuid))
            return False
        if event.get('Channel-HIT-Dialplan', 'false') == 'true':
            leg = 'a'
        else:
            leg = 'b'
            if not call_direction in self.b_leg:
                return False

        try:
            d = Domain.objects.get(name=domain_name)
        except Domain.ObjectDoesNotExist:
            logger.warn('EVENT CDR request {}: Unable to find domain {}.'.format(t_uuid, domain_name))
            return False
        except Domain.MultipleObjectsReturned:
            logger.warn('EVENT CDR request {}: Multiple domain record found for {}.'.format(t_uuid, domain_name))
            return False

        extension_found = False
        extension_uuid = event.get('variable_extension_uuid')
        if extension_uuid:
            try:
                e = Extension.objects.get(pk=extension_uuid)
            except Extension.ObjectDoesNotExist:
                logger.debug('EVENT CDR request {}: Unable to find extension by uuid {}.'.format(t_uuid, extension_uuid))
            else:
                extension_found = True
        else:
            tmpstr = event.get('variable_dialed_user')
            if tmpstr and not extension_found:
                try:
                    e = Extension.objects.get((Q(extension=tmpstr) | Q(number_alias=tmpstr)), domain_id=d.id)
                except Extension.ObjectDoesNotExist:
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
                except Extension.ObjectDoesNotExist:
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
                except Extension.ObjectDoesNotExist:
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

        xcdr = XmlCdr(domain_id=d)
        if extension_found:
            xcdr.extension_id=e
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
            if os.path.exists('%s/%s' % (record_path, record_name)) and record_length > 0:
                xcdr.record_path = record_path
                xcdr.record_name = record_name
                # record_description = event.get('variable_record_description', self.nonstr)

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

        xcdr.updated_by = 'system'
        xcdr.save()

        return True


