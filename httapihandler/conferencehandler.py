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

import os
from datetime import datetime
from django.db.models import Q
from django.db.models.functions import Now
from lxml import etree
from .httapihandler import HttApiHandler
from tenants.pbxsettings import PbxSettings
from conferencesettings.models import ConferenceCentres, ConferenceSessions


class ConferenceHandler(HttApiHandler):

    handler_name = 'conference'

    def get_variables(self):
        self.var_list = [
        'conference_uuid',
        ]
        self.var_list.extend(self.domain_var_list)

    def get_data(self):
        self.conf_session = None
        if self.getfile:
            self.get_uploaded_file()
        if self.exiting:
            self.exit_actions()
            return self.return_data('Ok\n')

        self.get_domain_variables()
        self.caller_id_name = self.qdict.get('Caller-Orig-Caller-ID-Name', 'None')
        self.caller_id_number = self.qdict.get('Caller-Orig-Caller-ID-Number', 'None')

        if 'conf_uuid' not in self.session.json[self.handler_name]:
            conf_uuid = self.qdict.get('conference_uuid')
            try:
                self.cnf = ConferenceCentres.objects.get(pk=conf_uuid)
            except ConferenceCentres.DoesNotExist:
                self.logger.debug(self.log_header.format('conference', 'Conference UUID not found'))
                return self.return_data(self.error_hangup('C0001'))

        self.x_root = self.XrootApi()
        etree.SubElement(self.x_root, 'params')
        self.x_work = etree.SubElement(self.x_root, 'work')


        if 'next_action' in self.session.json[self.handler_name]:
            next_action =  self.session.json[self.handler_name]['next_action']
            if next_action == 'chk-pin':
                self.act_chk_pin()
            elif next_action == 'join-conf':
                self.act_join_conf()
        else:
            self.act_get_pin()

        etree.indent(self.x_root)
        xml = str(etree.tostring(self.x_root), "utf-8")
        return xml

    # Action Get Pin
    def act_get_pin(self):
        self.session.json[self.handler_name]['next_action'] = 'chk-pin'
        self.session.save()
        self.x_work.append(self.play_and_get_digits('conference/conf-enter_conf_pin.wav'))
        return

    # Action Check Pin
    def act_chk_pin(self):
        pin_number = self.qdict.get('pb_input')
        cnfroom = self.cnf.conferencerooms_set.filter(
            (Q(participant_pin=pin_number) | Q(moderator_pin=pin_number)),
            (Q(start_time__isnull=True)|Q(start_time__lte=Now())),
            (Q(stop_time__isnull=True)|Q(stop_time__gte=Now())),
            enabled='true').first()
        if cnfroom:
            self.get_conf_session(cnfroom.c_profile_id.name, cnfroom)
            flag_list = []
            member_type = 1
            if pin_number == cnfroom.participant_pin:
                member_type = 0
            if cnfroom.wait_mod == 'true' and member_type == 0:
                flag_list.append('wait-mod')
            if cnfroom.mute == 'true' and member_type == 0:
                flag_list.append('mute')
            if member_type == 1:
                flag_list.append('moderator')
                etree.SubElement(self.x_work, 'execute', application='set', data='conference_controls=moderator')

            self.session.json[self.handler_name]['conf_name'] = '%s-%s-%s' % (self.domain_name, cnfroom.c_centre_id.name.replace(' ', '_' ), cnfroom.name.replace(' ', '_' )) # noqa: E501
            self.session.json[self.handler_name]['conf_uuid'] = str(cnfroom.id)
            self.session.json[self.handler_name]['sess_uuid'] = str(self.conf_session.id)
            self.session.json[self.handler_name]['name'] = cnfroom.name
            self.session.json[self.handler_name]['profile'] = cnfroom.c_profile_id.name
            self.session.json[self.handler_name]['max_members'] = str(cnfroom.max_members)
            self.session.json[self.handler_name]['record'] = cnfroom.record
            self.session.json[self.handler_name]['wait_mod'] = cnfroom.wait_mod
            self.session.json[self.handler_name]['announce'] = cnfroom.announce
            self.session.json[self.handler_name]['sounds'] = cnfroom.sounds
            self.session.json[self.handler_name]['mute'] = cnfroom.mute
            self.session.json[self.handler_name]['flags'] = '|'.join(flag_list)
            self.session.json[self.handler_name]['member_type'] = member_type

            if self.get_live_session_count(cnfroom.id) > cnfroom.max_members:
                etree.SubElement(self.x_work, 'playback', file='conference/conf-locked.wav')
                etree.SubElement(self.x_work, 'hangup', cause='CALL_REGECTED')
            else:
                if cnfroom.announce == 'true':
                    etree.SubElement(self.x_work, 'playback', file='ivr/ivr-say_name.wav')
                    self.x_work.append(self.record_and_get_digits('%s.wav' % self.session_id))

                if cnfroom.record == 'true':
                    etree.SubElement(self.x_work, 'pause', milliseconds='500')
                    etree.SubElement(self.x_work, 'playback', file='ivr/ivr-recording_started.wav')

                self.session.json[self.handler_name]['next_action'] = 'join-conf'
            self.session.save()

        else:
            self.session.json[self.handler_name].pop('next_action', None)
            if 'pin_retries' in self.session.json[self.handler_name]:
                 self.session.json[self.handler_name]['pin_retries'] = self.session.json[self.handler_name]['pin_retries'] + 1 # noqa: E501
            else:
                self.session.json[self.handler_name]['pin_retries'] = 1
            if self.session.json[self.handler_name]['pin_retries'] < 4:
                etree.SubElement(self.x_work, 'playback', file='conference/conf-bad-pin.wav')
            else:
                etree.SubElement(self.x_work, 'playback', file='phrase:voicemail_fail_auth:#')
                etree.SubElement(self.x_work, 'hangup')
            self.session.save()
        return

    # Action Join Conference
    def act_join_conf(self):
        self.get_conf_session()
        if not self.conf_session:
            self.logger.debug(self.log_header.format('conference', 'Conference session not found'))
            return self.return_data(self.error_hangup('C0002'))

        if self.session.json[self.handler_name]['record'] == 'true':
            rec_dir = PbxSettings().default_settings('switch', 'recordings', 'dir', '/var/lib/freeswitch/recordings', True)[0] # noqa: E501
            dt = datetime.now()

            rec_full_path = '%s/%s/archive/%s/%s/%s/%s.wav' % (rec_dir, self.domain_name, dt.strftime('%Y'), dt.strftime('%b'), dt.strftime('%d'), self.session.json[self.handler_name]['sess_uuid']) # noqa: E501
            rec_tmp_flag_file = '/tmp/%s-recording' % self.session.json[self.handler_name]['conf_uuid']
            try:
                with open(rec_tmp_flag_file, "r") as rec_flag:
                    rec_full_path = rec_flag.read()
            except FileNotFoundError:
                with open(rec_tmp_flag_file, "w") as rec_flag:
                    rec_flag.write(rec_full_path)
                record_data = 'res=${sched_api +6 none conference %s record %s}' % (self.session.json[self.handler_name]['conf_name'], rec_full_path) # noqa: E501
                etree.SubElement(self.x_work, 'execute', application='set', data=record_data)

            self.session.json[self.handler_name]['rec_tmp_flag_file'] = rec_tmp_flag_file
            self.session.save()
            self.conf_session.recording = rec_full_path
        self.conf_session.caller_id_name = self.caller_id_name
        self.conf_session.caller_id_number = self.caller_id_number
        self.conf_session.save()

        if self.session.json[self.handler_name]['announce'] == 'true':
            announce_data = 'res=${sched_api +1 none conference %s play file_string://%s!conference/conf-has_joined.wav}' % (self.session.json[self.handler_name]['conf_name'], self.session.json[self.handler_name]['name_recording']) # noqa: E501
        etree.SubElement(self.x_work, 'execute', application='set', data=announce_data)
        x_conference = etree.SubElement(self.x_work, 'conference', profile=self.session.json[self.handler_name]['profile'], flags=self.session.json[self.handler_name]['flags']) # noqa: E501
        x_conference.text = self.session.json[self.handler_name]['conf_name']
        return

    # Get ConferenceSession (this instance for this user)
    def get_conf_session(self, profile='default', cnfroom=None):
        if 'sess_uuid' in self.session.json[self.handler_name]:
            try:
                self.conf_session = ConferenceSessions.objects.get(pk=self.session.json[self.handler_name]['sess_uuid'])
            except ConferenceSessions.DoesNotExist:
                if not cnfroom:
                    self.conf_session = None
                    return
                self.conf_session = ConferenceSessions.objects.create(c_room_id=cnfroom, profile=profile)
        else:
            if not cnfroom:
                self.conf_session = None
                return
            self.conf_session = ConferenceSessions.objects.create(c_room_id=cnfroom, profile=profile)
        return

    # Get a count of current live participants
    def get_live_session_count(self, c_room_id):
        return ConferenceSessions.objects.filter(c_room_id=c_room_id, live='true').count()

    # Get any files uploaded
    def get_uploaded_file(self):
        received_file_name = 'conference-%s' % self.fdict['rd_input'].name
        with open('/tmp/%s' % received_file_name, "wb+") as destination:
            for chunk in self.fdict['rd_input'].chunks():
                destination.write(chunk)
        self.session.json[self.handler_name]['name_recording'] = '/tmp/%s' % received_file_name
        self.session.save()
        return

    # Perform any exit actions
    def exit_actions(self):
        self.get_conf_session()
        if self.conf_session:
            self.conf_session.live = 'false'
            self.conf_session.save()
            if 'rec_tmp_flag_file' in self.session.json[self.handler_name]:
                if self.get_live_session_count(self.conf_session.c_room_id) < 1:
                    try:
                        os.remove(self.session.json[self.handler_name]['rec_tmp_flag_file'])
                    except OSError:
                        pass
        if 'name_recording' in self.session.json[self.handler_name]:
            try:
                os.remove(self.session.json[self.handler_name]['name_recording'])
            except OSError:
                pass
        return
