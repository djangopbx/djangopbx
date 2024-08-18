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
import logging
import json
from pika import BasicProperties as PikaBasicProperties
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from switch.models import IpRegister
from tenants.models import DefaultSetting, Domain
from xmlcdr.models import XmlCdr, CallTimeline
from voicemail.models import Voicemail, VoicemailGreeting
from pbx.commonfunctions import shcommand
from pbx.scripts.resources.pbx.amqpconnection import AmqpConnection
from pbx.sshconnect import SFTPConnection
from .cdrhandlermixin import CdrHandlerMixin

logger = logging.getLogger(__name__)

class Command(BaseCommand, CdrHandlerMixin):
    help = 'PBX Event Receiver'
    nonstr = 'none'
    debug = False
    mb_key_host = 'message_broker'
    mb_key_port = 'message_broker_port'
    mb_key_user = 'message_broker_user'
    mb_key_pass = 'message_broker_password'
    mb_key_adhoc = 'message_broker_adhoc_publish'
    switch_recordings_path = '/var/lib/freeswitch/recordings'
    pop_call_recordings = False
    call_recordings_path = 'fs/recordings'
    vm_greetings_path = 'fs/voicemail'
    updated_by = 'Event Receiver'
    domains = {}

    def str2int(self, tmpstr):
        if not tmpstr:
            return 0
        try:
            number = int(tmpstr)
        except (TypeError, ValueError):
            number = 0
        return number

    def str2float(self, tmpstr):
        if not tmpstr:
            return 0.0
        try:
            number = round(float(tmpstr), 2)
        except (TypeError, ValueError):
            number = 0.0
        return number

    def get_domain_name(self, event):
        domain_name = event.get('variable_domain_name')
        if not domain_name:
            domain_name = event.get('variable_sip_auth_realm')
        if not domain_name:
            domain_name = event.get('realm')
        if not domain_name:
            domain_name = event.get('variable_user_context')
        if not domain_name:
            domain_name = event.get('variable_sip_from_host')
        return domain_name

    def get_domain(self, domain_name):
        d = self.domains.get(domain_name)
        if d:
            return d
        try:
            d = Domain.objects.get(name=domain_name)
        except Domain.DoesNotExist:
            return None
        except Domain.MultipleObjectsReturned:
            return None
        self.domains[domain_name] = d
        return d

    def get_direction(self, event):
        direction = event.get('Call-Direction')
        if not direction:
            direction = event.get('variable_direction')
        if not direction:
            direction = event.get('variable_call_direction')
        if not direction:
            direction = event.get('Caller-Direction')
        return direction

    def on_message(self, channel, method, properties, body):
        msg = body.decode('utf8')
        if self.debug:
            if logger is not None:
                logger.debug('Event Receiver PID: %s\n%s', (self.pid, msg))
        event = json.loads(msg)
        event_name = event.get('Event-Name', self.nonstr)
        event_subclass = event.get('Event-Subclass', self.nonstr)
        if event_name == 'CHANNEL_HANGUP_COMPLETE':
            self.handle_hup_complete(event)
        elif event_name == 'CHANNEL_CREATE':
            self.handle_create(event)
        elif event_name == 'CHANNEL_BRIDGE':
            self.handle_bridge(event)
        elif event_name == 'CHANNEL_ANSWER':
            self.handle_answer(event)
        elif event_name == 'CHANNEL_UUID':
            self.handle_chuuid(event)
        elif event_name == 'DTMF':
            self.handle_dtmf(event)
        elif event_name == 'CHANNEL_HOLD':
            self.handle_channel_hold(event)
        elif event_name == 'CHANNEL_UNHOLD':
            self.handle_channel_hold(event)
        elif event_name == 'PLAYBACK_START':
            self.handle_playback_start(event)
        elif event_name == 'PLAYBACK_STOP':
            self.handle_playback_stop(event)
        elif event_name == 'RECORD_STOP':
            self.handle_record_stop(event)
        elif event_name == 'CUSTOM':
            if event.get('Event-Subclass', self.nonstr) == 'sofia::register':
                self.handle_register(channel, event)
            elif event.get('Event-Subclass', self.nonstr) == 'callcenter::info':
                self.handle_callcentreinfo(event)
            elif event.get('Event-Subclass', self.nonstr) == 'menu::enter':
                self.handle_ivrmenu(event)
            elif event.get('Event-Subclass', self.nonstr) == 'menu::exit':
                self.handle_ivrmenu(event)
            elif event.get('Event-Subclass', self.nonstr) == 'conference::maintenance':
                self.handle_conferencemaintenance(event)
            elif event.get('Event-Subclass', self.nonstr) == 'vm::maintenance':
                self.handle_vmmaintenance(event)
            elif event.get('Event-Subclass', self.nonstr) == 'valet_parking::info':
                self.handle_park(event)

    def handle(self, *args, **kwargs):
        self.pid = os.getpid()
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
        self.b_leg = settings.PBX_CDRH_B_LEG
        self.cdrformat = settings.PBX_CDRH_FORMAT
        self.pop_call_recordings = settings.PBX_CDRH_POPULATE_CALL_RECORDINGS
        self.call_recordings_path = settings.PBX_CDRH_RECORDINGS
        self.switch_recordings_path = settings.PBX_CDRH_SWITCH_RECORDINGS

        self.firewall_event_template = '{\"Event-Name\":\"FIREWALL\", \"Action\":\"add\", \"IP-Type\":\"%s\",\"Fw-List\":\"sip-customer\", \"IP-Address\":\"%s\"}' # noqa: E501
        self.mq = AmqpConnection(mb[self.mb_key_host], mb[self.mb_key_port],
                                    mb[self.mb_key_user], mb[self.mb_key_pass])
        self.sftp = SFTPConnection()
        self.mq.connect()
        self.mq.setup_queues()
        self.mq.consume(self.on_message)

    def create_call_timeline(self, event):
        d = None
        domain_name = self.get_domain_name(event)
        if domain_name:
            d = self.get_domain(domain_name)
        try:
            ctl = CallTimeline(
                domain_id = d,
                core_uuid = event.get('Core-UUID'),
                hostname = event.get('FreeSWITCH-Hostname'),
                switchame = event.get('FreeSWITCH-Switchname'),
                switch_ipv4 = event.get('FreeSWITCH-IPv4'),
                switch_ipv6 = event.get('FreeSWITCH-IPv6'),
                call_uuid = event.get('Channel-Call-UUID'),
                event_name = event.get('Event-Name'),
                event_subclass = event.get('Event-Subclass'),
                event_date_local = event.get('Event-Date-Local'),
                event_epoch = self.str2int(event.get('Event-Date-Timestamp')),
                event_sequence = self.str2int(event.get('Event-Sequence')),
                event_calling_file = event.get('Event-Calling-File'),
                event_calling_function = event.get('Event-Calling-Function')
            )
        except:
            return False
        return ctl

    def add_ctl_unique_ids(self, ctl, event):
        ctl.unique_id = event.get('Unique-ID')
        ctl.other_leg_unique_id = event.get('Other-Leg-Unique-ID')
        return

    def add_ctl_caller_channel_data(self, ctl, event):
        ctl.other_leg_direction = event.get('Other-Leg-Direction')
        ctl.context = event.get('Caller-Context')
        ctl.other_leg_context = event.get('Other-Leg-Context')
        ctl.hit_dialplan = event.get('Channel-HIT-Dialplan', 'false')
        ctl.caller_user_name = event.get('Caller-Username')
        ctl.caller_ani = event.get('Caller-ANI')
        ctl.other_leg_user_name = event.get('Other-Leg-Username')
        ctl.caller_uuid = event.get('Caller-Unique-ID')
        ctl.other_leg_caller_uuid = event.get('Other-Leg-Caller-Unique-ID')
        ctl.channel_name = event.get('Caller-Channel-Name')
        ctl.channel_state = event.get('Channel-State')
        ctl.channel_call_state = event.get('Channel-Call-State')
        ctl.answer_state = event.get('Answer-State')
        ctl.caller_id_name = event.get('Caller-Caller-ID-Name')
        ctl.other_leg_caller_id_name = event.get('Other-Leg-Caller-ID-Name')
        ctl.caller_id_number = event.get('Caller-Caller-ID-Number')
        ctl.other_leg_caller_id_number = event.get('Other-Leg-Callee-ID-Number')
        ctl.caller_destination = event.get('Caller-Destination-Number')
        ctl.other_leg_caller_destination = event.get('Other-Leg-Destination-Number')
        ctl.network_addr = event.get('Caller-Network-Addr')
        ctl.other_leg_network_addr = event.get('Other-Leg-Network-Addr')
        ctl.created_time = self.str2int(event.get('Caller-Channel-Created-Time'))
        ctl.other_leg_created_time = self.str2int(event.get('Other-Leg-Channel-Created-Time'))
        ctl.answered_time = self.str2int(event.get('Caller-Channel-Answered-Time'))
        ctl.other_leg_answered_time = self.str2int(event.get('Other-Leg-Channel-Answered-Time'))
        ctl.progress_time = self.str2int(event.get('Caller-Channel-Progress-Time'))
        ctl.other_leg_progress_time = self.str2int(event.get('Other-Leg-Channel-Progress-Time'))
        ctl.progress_media_time = self.str2int(event.get('Caller-Channel-Progress-Media-Time'))
        ctl.other_leg_progress_media_time = self.str2int(event.get('Other-Leg-Channel-Progress-Media-Time'))
        ctl.hangup_time = self.str2int(event.get('Caller-Channel-Hangup-Time'))
        ctl.other_leg_hangup_time = self.str2int(event.get('Other-Leg-Channel-Hangup-Time'))
        ctl.transfer_time = self.str2int(event.get('Caller-Channel-Transfer-Time'))
        ctl.other_leg_transfer_time = self.str2int(event.get('Other-Leg-Channel-Transfer-Time'))
        ctl.resurrect_time = self.str2int(event.get('Caller-Channel-Resurrect-Time'))
        ctl.other_leg_resurrect_time = self.str2int(event.get('Other-Leg-Channel-Resurrect-Time'))
        ctl.bridged_time = self.str2int(event.get('Caller-Channel-Bridged-Time'))
        ctl.other_leg_bridged_time = self.str2int(event.get('Other-Leg-Channel-Bridged-Time'))
        ctl.last_hold_time = self.str2int(event.get('Caller-Channel-Last-Hold'))
        ctl.other_leg_last_hold_time = self.str2int(event.get('Other-Leg-Channel-Last-Hold'))
        ctl.hold_accu_time = self.str2int(event.get('Caller-Channel-Hold-Accum'))
        ctl.other_leg_hold_accu_time = self.str2int(event.get('Other-Leg-Channel-Hold-Accum'))
        ctl.transfer_source = event.get('Caller-Transfer-Source')
        return

    def handle_register(self, channel, event):
        if event.get('status', 'N/A').startswith('Registered'):
            ip_address = event.get('network-ip')
            if not ip_address:
                return
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

    def handle_hup_complete(self, event):
        call_direction = self.get_direction(event)
        q850 = event.get('variable_hangup_cause_q850', self.nonstr)
        if q850 == '502': # LOSE_RACE (call connected elsewhere)
            return False
        if q850 == '605': # PICKED_OFF (intercepting it from another extension)
            return False
        if q850 == '101': # WRONG_CALL_STATE
            if not call_direction:
                return False
        ctl = self.create_call_timeline(event)
        if not ctl:
            return
        ctl.direction = call_direction
        self.add_ctl_unique_ids(ctl, event)
        self.add_ctl_caller_channel_data(ctl, event)
        ctl.save()
        self.handle_cdr(event, call_direction, q850)
        return

    def handle_dtmf(self, event):
        ctl = self.create_call_timeline(event)
        if not ctl:
            return
        ctl.direction = self.get_direction(event)
        self.add_ctl_unique_ids(ctl, event)
        self.add_ctl_caller_channel_data(ctl, event)
        ctl.dtmf_digit = event.get('DTMF-Digit')
        ctl.dtmf_duration = self.str2int(event.get('DTMF-Duration'))
        ctl.dtmf_source = event.get('DTMF-Source')
        ctl.save()
        return

    def handle_channel_hold(self, event):
        ctl = self.create_call_timeline(event)
        if not ctl:
            return
        ctl.direction = self.get_direction(event)
        self.add_ctl_unique_ids(ctl, event)
        self.add_ctl_caller_channel_data(ctl, event)
        ctl.bridge_channel = event.get('variable_bridge_channel')
        ctl.save()
        return

    def handle_playback_start(self, event):
        ctl = self.create_call_timeline(event)
        if not ctl:
            return
        ctl.direction = self.get_direction(event)
        self.add_ctl_unique_ids(ctl, event)
        self.add_ctl_caller_channel_data(ctl, event)
        ctl.application_name = 'playback'
        ctl.application = event.get('variable_current_application')
        ctl.application_data = event.get('variable_current_application_data')
        ctl.application_file_path = event.get('Playback-File-Path')
        ctl.save()
        return

    def handle_playback_stop(self, event):
        ctl = self.create_call_timeline(event)
        if not ctl:
            return
        ctl.direction = self.get_direction(event)
        self.add_ctl_unique_ids(ctl, event)
        self.add_ctl_caller_channel_data(ctl, event)
        ctl.application_name = 'playback' # We put this manual label in because the current_application is not always what you expect it to be.
        ctl.application = event.get('variable_current_application')
        ctl.application_data = event.get('variable_current_application_data')
        ctl.application_status = event.get('Playback-Status')
        ctl.application_file_path = event.get('Playback-File-Path')
        ctl.application_seconds = self.str2int(event.get('variable_playback_seconds'))
        ctl.save()
        return

    def handle_record_stop(self, event):
        ctl = self.create_call_timeline(event)
        if not ctl:
            return
        ctl.direction = self.get_direction(event)
        self.add_ctl_unique_ids(ctl, event)
        self.add_ctl_caller_channel_data(ctl, event)
        ctl.application_name = 'record'
        ctl.application = event.get('variable_current_application')
        ctl.application_data = event.get('variable_current_application_data')
        ctl.application_status = event.get('variable_record_completion_cause')
        ctl.application_file_path = event.get('Record-File-Path')
        ctl.application_seconds = self.str2int(event.get('variable_record_seconds'))
        ctl.save()
        return

    def handle_callcentreinfo(self, event):
        ctl = self.create_call_timeline(event)
        if not ctl:
            return
        ctl.direction = self.get_direction(event)
        self.add_ctl_unique_ids(ctl, event)
        self.add_ctl_caller_channel_data(ctl, event)
        ctl.application_name = 'callcentre'
        ctl.application = event.get('variable_current_application')
        ctl.application_data = event.get('variable_current_application_data')
        ctl.cc_side = event.get('variable_cc_side')
        ctl.cc_queue = event.get('CC-Queue')
        ctl.cc_action = event.get('CC-Action')
        ctl.cc_count = self.str2int(event.get('CC-Count'))
        jt = event.get('CC-Member-Joined-Time')
        if jt:
            ctl.cc_member_joining_time = self.str2int(jt)
        else:
            ctl.cc_member_joining_time = self.str2int(event.get('variable_cc_queue_joined_epoch'))
        ctl.cc_member_leaving_time = self.str2int(event.get('CC-Member-Leaving-Time'))
        ctl.cc_cause = event.get('CC-Cause')
        ctl.cc_hangup_cause = event.get('CC-Hangup-Cause')
        ctl.cc_cancel_reason = event.get('CC-Cancel-Reason')
        ctl.cc_member_uuid = event.get('CC-Member-UUID')
        ctl.cc_member_session_uuid = event.get('CC-Member-Session-UUID')
        ctl.cc_member_caller_id_name = event.get('CC-Member-CID-Name')
        ctl.cc_member_caller_id_number = event.get('CC-Member-CID-Number')
        ctl.cc_agent = event.get('CC-Agent')
        ctl.cc_agent_uuid = event.get('CC-Agent-UUID')
        ctl.cc_agent_system = event.get('CC-Agent-System')
        ctl.cc_agent_type = event.get('CC-Agent-Type')
        ctl.cc_agent_state = event.get('CC-Agent-State')
        ctl.cc_agent_called_time = self.str2int(event.get('CC-Agent-Called-Time'))
        ctl.cc_agent_answered_time = self.str2int(event.get('CC-Agent-Answered-Time'))
        ctl.save()
        return

    def handle_conferencemaintenance(self, event):
        ctl = self.create_call_timeline(event)
        if not ctl:
            return
        ctl.direction = self.get_direction(event)
        self.add_ctl_unique_ids(ctl, event)
        self.add_ctl_caller_channel_data(ctl, event)
        ctl.application_name = 'conference'
        ctl.cf_name = event.get('Conference-Name')
        ctl.cf_action = event.get('Action')
        ctl.cf_uuid = event.get('Conference-Unique-ID')
        ctl.cf_domain = event.get('Conference-Domain')
        ctl.cf_size = event.get('Conference-Size')
        ctl.cf_ghosts = event.get('Conference-Ghosts')
        ctl.cf_profile_name = event.get('Conference-Profile-Name')
        ctl.cf_member_type = event.get('Member-Type')
        ctl.cf_member_id = event.get('Member-ID')
        ctl.save()
        return

    def handle_vmmaintenance(self, event):
        vm_action = event.get('VM-Action', '')
        if vm_action == 'mwi-update':
            return
        ctl = self.create_call_timeline(event)
        if not ctl:
            return
        vm_domain = event.get('VM-Domain', 'None')
        vm_user = event.get('VM-User', '000')
        vm_greeting_no = event.get('VM-User', '000')
        ctl.direction = self.get_direction(event)
        self.add_ctl_unique_ids(ctl, event)
        self.add_ctl_caller_channel_data(ctl, event)
        ctl.application_name = 'voicemail'
        ctl.application = event.get('variable_current_application')
        ctl.application_action = event.get('VM-Action')
        ctl.application_uuid = event.get('variable_uuid')
        ctl.application_data = event.get('variable_current_application_data')
        ctl.application_file_path = event.get('VM-Greeting-Path')
        if vm_action == 'record-greeting':
            path = event.get('VM-Greeting-Path')
            filename= os.path.basename(path)
            storage_path='%s/default/%s/%s/%s' % (self.vm_greetings_path.lstrip('/'), vm_domain, vm_user, filename)
            # Create or update the voicemail greetings record with the currect filename adjusting storage path to be relative to MEDIA_ROOT
            vm = Voicemail.objects.get(extension_id__extension=vm_user, extension_id__domain_id__name=vm_domain)
            if not vm:
                ctl.general_error = 'Voicemail record not found'
                ctl.save()
                return
            vmg, created = VoicemailGreeting.objects.get_or_create(
                                        voicemail_id=vm,
                                        filename=storage_path,
                                        updated_by=self.updated_by,
                                        defaults={'name': filename}
                                        )
            if not settings.PBX_FREESWITCH_LOCAL and not settings.PBX_USE_LOCAL_FILE_STORAGE:
                # if freeswitch and filestore are not local copy recordings contents to filestore
                grtg = filename.open(mode='rb')
                sftp.getfo(path, grtg)
            vmg.save()
        #if vm_action == 'remove-greeting':
        #    There is not much we can do because freeswitch does not provide the greeting path
        ctl.save()
        return

    def handle_ivrmenu(self, event):
        ctl = self.create_call_timeline(event)
        if not ctl:
            return
        ctl.direction = self.get_direction(event)
        self.add_ctl_unique_ids(ctl, event)
        self.add_ctl_caller_channel_data(ctl, event)
        ctl.application_name = 'ivrmenu'
        ctl.application = event.get('variable_current_application')
        ctl.application_data = event.get('variable_current_application_data')
        ctl.save()
        return

    def handle_create(self, event):
        ctl = self.create_call_timeline(event)
        if not ctl:
            return
        ctl.direction = self.get_direction(event)
        self.add_ctl_unique_ids(ctl, event)
        ctl.channel_name = event.get('Channel-Name')
        ctl.channel_state = event.get('Channel-State')
        ctl.answer_state = event.get('Answer-State')
        ctl.save()
        return

    def handle_bridge(self, event):
        ctl = self.create_call_timeline(event)
        if not ctl:
            return
        ctl.direction = self.get_direction(event)
        self.add_ctl_unique_ids(ctl, event)
        self.add_ctl_caller_channel_data(ctl, event)
        ctl.application_name = 'Bridge'
        ctl.application = event.get('variable_current_application')
        ctl.application_file_path = 'A:%s B:%s' % (event.get('Bridge-A-Unique-ID', self.nonstr),
                                             event.get('Bridge-B-Unique-ID', self.nonstr))
        ctl.application_data = event.get('variable_current_application_data')
        ctl.save()
        return

    def handle_answer(self, event):
        ctl = self.create_call_timeline(event)
        if not ctl:
            return
        ctl.direction = self.get_direction(event)
        self.add_ctl_unique_ids(ctl, event)
        self.add_ctl_caller_channel_data(ctl, event)
        ctl.application = event.get('variable_current_application')
        ctl.application_data = event.get('variable_current_application_data')
        ctl.save()
        return

    def handle_chuuid(self, event):
        ctl = self.create_call_timeline(event)
        if not ctl:
            return
        ctl.direction = self.get_direction(event)
        ctl.unique_id = event.get('Unique-ID')
        ctl.other_leg_unique_id = event.get('Old-Unique-ID')
        ctl.application = event.get('variable_sip_destination_url')
        ctl.application_uuid = event.get('Old-Unique-ID')
        ctl.application_data = event.get('variable_channel_name')
        ctl.save()
        return

    def handle_park(self, event):
        ctl = self.create_call_timeline(event)
        if not ctl:
            return
        ctl.direction = self.get_direction(event)
        self.add_ctl_unique_ids(ctl, event)
        self.add_ctl_caller_channel_data(ctl, event)
        ctl.application = event.get('variable_current_application')
        ctl.application_name = 'park: %s' % event.get('variable_park_lot', '')
        ctl.application_action = 'park-in' if event.get('variable_inline_detination') else 'update'
        ctl.application_data = event.get('variable_current_application_data')
        ctl.application_status = event.get('variable_park_in_use')
        ctl.save()
        return
