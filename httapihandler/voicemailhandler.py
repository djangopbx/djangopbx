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
import wave
from base64 import b64encode, b64decode
import pickle
from lxml import etree
from django.conf import settings
from django.core.files import File
from django.utils import timezone
from tenants.models import Domain
from voicemail.models import (
    Voicemail, VoicemailGreeting, VoicemailMessages
)
from pbx.hostslookup import HostsLookup
from pbx.pbxsendsmtp import PbxTemplateMessage
from pbx.commonevents import MessageWaiting
from .httapihandler import HttApiHandler


class VoicemailHandler(HttApiHandler):

    handler_name = 'voicemail'
    vm = None
    vm_new = 0
    vm_saved = 0

    def destroy_session_ok(self):
        return False

    def get_data(self):
        if self.getfile:
            self.get_uploaded_file()

        if self.exiting and not self.getfile:
            self.destroy_session()
            return self.return_data('Ok\n')
        if not self.vmuser or not self.vmdomain:
            return self.error_hangup('V2001')

        self.x_root = self.XrootApi()
        etree.SubElement(self.x_root, 'params')
        self.x_work = etree.SubElement(self.x_root, 'work')
        self.get_vm_object()
        if not self.vm:
            if self.exiting:
                self.destroy_session()
                return self.return_data('Ok\n')
            etree.SubElement(self.x_work, 'playback', file='voicemail/vm-not_available_no_voicemail.wav')
            etree.SubElement(self.x_work, 'hangup')
            etree.indent(self.x_root)
            xml = str(etree.tostring(self.x_root), "utf-8")
            return xml
        if self.hraction == 'check':
            if not self.check_auth():
                etree.indent(self.x_root)
                xml = str(etree.tostring(self.x_root), "utf-8")
                return xml
            if self.main_loop():
                etree.SubElement(self.x_work, 'playback', file='voicemail/vm-goodbye.wav')
                etree.SubElement(self.x_work, 'hangup')
            else:
                etree.SubElement(self.x_work, 'continue')
        elif self.hraction == 'record':
            if self.inbound_voicemail():
                etree.SubElement(self.x_work, 'playback', file='voicemail/vm-goodbye.wav')
                etree.SubElement(self.x_work, 'hangup')
            else:
                etree.SubElement(self.x_work, 'continue')
        else:
            return self.error_hangup('V2003')

        if self.exiting:
            self.destroy_session()
            return self.return_data('Ok\n')
        self.session.save()
        etree.indent(self.x_root)
        xml = str(etree.tostring(self.x_root), "utf-8")
        return xml

    def main_loop(self):
        # not really a loop as such, but it gets returned to until it returns True or call is hungup
        menu = self.session_json.get('menu')
        if not menu:
            self.msgs_summary()
            self.menu_main()
            return False
        ###########################################################
        # Main Menu
        ###########################################################
        if menu == 'main':
            choice = self.menu_main()
            if not choice:
                return False
            if choice == '#':   # Exit ############################
                return True
            elif choice == '1': # Listen to new messages ##########
                self.set_skip_invalid()
                self.listen('new')
                return False
            elif choice == '2': # Listen to saved massages ########
                self.set_skip_invalid()
                self.listen('saved')
                return False
            elif choice == '5': # Advanced Options ################
                self.menu_config()
                return False
            else:
                return True
        ###########################################################
        # Listen to Messages Menu
        ###########################################################
        elif menu == 'listen_msgs':
            msg_type = self.session_json.get('vm_message_type', 'new')
            choice = self.menu_listen_msgs()
            if not choice:
                return False
            if choice == '1':   # play/listen #####################
                self.listen(msg_type)
                return False
            elif choice == '2': # Save ############################
                if self.msg_save():
                    etree.SubElement(self.x_work, 'playback', file='phrase:voicemail_ack:saved')
                else:
                    etree.SubElement(self.x_work, 'playback', file='misc/error.wav')
                etree.SubElement(self.x_work, 'pause', milliseconds='500')
                self.listen(msg_type)
                return False
            elif choice == '5': # Return Call #####################
                self.msg_return_call()
                return False

            elif choice == '7': # Delete ##########################
                self.msg_delete()
                etree.SubElement(self.x_work, 'playback', file='phrase:voicemail_ack:deleted')
                etree.SubElement(self.x_work, 'pause', milliseconds='500')
                self.listen(msg_type)
                return False
            elif choice == '8': # Forward #########################
                self.menu_forward_msg()
                return False
            elif choice == '9': # Forward to email ################
                self.msg_forward_email()
                etree.SubElement(self.x_work, 'playback', file='phrase:voicemail_ack:emailed')
                return False

            else:               # Default and captured 'invalid' ##
                self.msg_save()
                etree.SubElement(self.x_work, 'playback', file='phrase:voicemail_ack:saved')
                etree.SubElement(self.x_work, 'pause', milliseconds='500')
                self.listen(msg_type)
                return False
        ###########################################################
        # Forward Message Menu
        ###########################################################
        elif menu == 'forward_msg':
            choice = self.menu_forward_msg()
            if not choice:
                return False
            vm = self.get_msg_forward_vm(choice)
            if not vm:
                etree.SubElement(self.x_work, 'playback', file='phrase:voicemail_invalid_extension')
            else:
                self.msg_forward(vm)
            self.session_json['menu'] = 'listen_msgs'
            return False
        ###########################################################
        # Config (Advanced) Menu
        ###########################################################
        elif menu == 'config':
            choice = self.menu_config()
            if not choice:
                return False
            if choice == '0':     # Exit ##########################
                self.menu_main()
                return False
            elif choice == '1':   # Record Greeting ###############
                self.session_json['vm_choose_greeting_purpose'] = 'record'
                self.menu_choose_greet()
                return False
            elif choice == '2':   # Choose Greeting ###############
                self.session_json['vm_choose_greeting_purpose'] = 'use'
                self.menu_choose_greet()
                return False
            elif choice == '3':   # Record Name ###################
                self.menu_record(playfile='voicemail/vm-record_name1.wav', recfile=self.create_temporary_file('.wav'), rectype='name')
                return False
            elif choice == '6':   # Change Password ###############
                self.session_json['vm_chg_pass_stage'] = 1
                self.menu_chg_pass(1)
                return False
            return False
        ###########################################################
        # Choose Greeting Menu
        ###########################################################
        elif menu == 'choose_greet':
            choice = self.menu_choose_greet()
            if not choice:
                return False
            if choice in '123456789':
                self.session_json['vm_current_greeting'] = choice
                cgp = self.session_json.get('vm_choose_greeting_purpose', 'use')
                if cgp == 'record':
                    self.menu_record(playfile='voicemail/vm-record_greeting.wav', recfile=self.create_temporary_file('.wav'), rectype='greeting')
                if cgp == 'use':
                    greeting_id = self.str2int(choice)
                    self.vm.greeting_id = greeting_id
                    self.vm.save()
                    etree.SubElement(self.x_work, 'playback', file='phrase:voicemail_greeting_selected:%s' % choice)
                    self.menu_config()
            return False
        ###########################################################
        # Record Menu
        ###########################################################
        elif menu == 'record':
            choice = self.menu_record()
            if not choice:
                return False
            self.menu_record_review()
            return False
        ###########################################################
        # Record Review Menu
        ###########################################################
        elif menu == 'record_review':
            choice = self.menu_record_review()
            if not choice:
                return False
            if choice == '1':   # Listen to Recording ############
                tmpfile = self.get_tmp_recording_filename()
                if not tmpfile:
                    etree.SubElement(self.x_work, 'playback', file='misc/error')
                    return True
                etree.SubElement(self.x_work, 'playback', file='%s/portal/tmprecording/%s_%s' % (
                        settings.PBX_SERVER_URL, self.session_id, tmpfile.split('/')[-1:][0]))
                        #'http://localhost:8080', self.session_id, tmpfile.split('/')[-1:][0])) # Used for debug purposes
                return False
            if choice == '2':   # Save Greeting #################
                tmpfile = self.get_tmp_recording_filename()
                if not tmpfile:
                    etree.SubElement(self.x_work, 'playback', file='misc/error')
                    return True
                self.save_recording(tmpfile)
                return False
            if choice == '3':   # Re-Record #####################
                self.menu_record(recfile=self.create_temporary_file('.wav'))
                return False
            if choice == '#':   # Exit ##########################
                self.menu_config()
                return False
            return False
        ###########################################################
        # Change Password
        ###########################################################
        elif menu == 'chg_pass':
            stage = self.session_json.get('vm_chg_pass_stage', 1)
            choice = self.menu_chg_pass(stage)
            if not choice:
                return False
            if stage == 1:
                self.session_json['vm_chg_pass_pass1'] = choice
                self.session_json['vm_chg_pass_stage'] = 2
                self.menu_chg_pass(2)
            if stage == 2:
                if choice == self.session_json.get('vm_chg_pass_pass1'):
                    self.vm.password = choice
                    self.vm.save()
                    etree.SubElement(self.x_work, 'playback', file='voicemail/vm-password_has_been_changed.wav')
                else:
                    etree.SubElement(self.x_work, 'playback', file='voicemail/vm-password_not_valid.wav')
                self.menu_config()
            return False
        return True
        ############# main loop / meuns end #######################

    ###############################################################
    # Main Voicemail Record Message Handler function
    ###############################################################
    def inbound_voicemail(self):
        if self.getfile:
            tmpfile = self.get_tmp_recording_filename()
            if not tmpfile:
                return False
            duration=self.str2int(self.session_json.get('variable_record_seconds', '-1'))
            if duration < 0:
                with wave.open(tmpfile, 'r') as f:
                    try:
                        duration = int(f.getnframes() / f.getframerate())
                    except:
                        duration = 0
            rec = self.create_vm_message(self.vm, tmpfile, duration)
            rf = open(tmpfile, 'rb')
            djangofile = File(rf)
            mwi = MessageWaiting()
            mwi.connect()
            if rec:
                rec.filename.save(rec.name, djangofile)
                new_count, saved_count = self.get_message_counts()
                self.msg_forward_email(rec)
                if self.vm.local_after_email == 'true':
                    mwi.send(self.vmuser, self.vmdomain, new_count, saved_count)
                else:
                    rec.status = 'deleted'
                    rec.save()
            fwd_uuids = []
            fwd_dstns = self.vm.voicemaildestinations_set.all()
            if len(fwd_dstns) > 0:
                for dst in fwd_dstns:
                    fwd_uuids.append(dst.voicemail_dest)
                qs = Voicemail.objects.filter(pk__in=fwd_uuids)
                for q in qs:
                    djangofile.seek(0)
                    rec = self.create_vm_message(q, tmpfile, duration)
                    if rec:
                        rec.filename.save(rec.name, djangofile)
                        new_count, saved_count = self.get_message_counts(q)
                        self.msg_forward_email(rec, q)
                        if q.local_after_email == 'true':
                            mwi.send(q.extension_id.extension, self.vmdomain, new_count, saved_count)
                        else:
                            rec.status = 'deleted'
                            rec.save()
            mwi.disconnect()

        option = self.menu('inbound_voicemail')
        if option:
            opt = self.vm.voicemailoptions_set.filter(option_digits=option).first()
            if opt:
                app_data = opt.option_param.split(' ', 1)
                if len(app_data) == 2:
                    etree.SubElement(self.x_work, 'execute', application=app_data[0], data=app_data[1])
                else:
                    etree.SubElement(self.x_work, 'execute', application=app_data[0])
                etree.SubElement(self.x_work, 'break')
                return True
            etree.SubElement(self.x_work, 'playback', file='voicemail/vm-record_message.wav')
            recfile = self.create_temporary_file('.wav')
            self.session_json['vm_record_current_recfile'] = recfile
            self.x_work.append(self.record_and_get_digits(recfile, digit_timeout='1000'))
            return True
        else:
            try:
                grtg = VoicemailGreeting.objects.get(voicemail_id=self.vm.id, name='greeting_%s.wav' % self.vm.greeting_id)
            except VoicemailGreeting.DoesNotExist:
                grtg = None
            except Domain.MultipleObjectsReturned:
                grtg = VoicemailGreeting.objects.filter(voicemail_id=self.vm.id, name='greeting_%s.wav' % self.vm.greeting_id).first()
            if grtg:
                self.session_json['vm_inbound_expecting_option'] = 'true'
                self.x_work.append(self.play_and_get_digits(self.get_fs_file_path(grtg.filename.name, grtg.filestore),
                                                loops='0', input_timeout='1500', digit_regex='~[0-9#\*]' ))
            else:
                etree.SubElement(self.x_work, 'playback', file='phrase:voicemail_play_greeting:%s' % self.vmuser)
        return False

    ###############################################################
    # Menu Handler functions
    ###############################################################
    def menu(self, name):
        self.session_json['menu'] = name
        expecting_str = 'expecting_%s_menu' % name
        if self.session_json.get(expecting_str, 'false') == 'true':
            self.session_json[expecting_str] = 'false'
            choice =  self.qdict.get('pb_input', '#')
            if choice == 'invalid' and self.session_json.get('vm_menu_skip_invalid'):
                choice = None
                self.session_json[expecting_str] = 'true'
                self.unset_skip_invalid()
            return choice
        self.session_json[expecting_str] = 'true'
        return False

    def menu_main(self):
        self.session_json['vm_current_message'] = None
        self.session_json['vm_qs_new_pickle'] = None
        self.session_json['vm_qs_saved_pickle'] = None
        r = self.menu('main')
        if r:
            return r
        etree.SubElement(self.x_work, 'pause', milliseconds='250')
        self.x_work.append(self.play_and_get_digits('phrase:voicemail_menu:1:2:5:#',  digit_regex='~[0-9#*]'))
        return False

    def menu_forward_msg(self):
        r = self.menu('forward_msg')
        if r:
            return r
        self.x_work.append(self.play_and_get_digits('phrase:voicemail_forward_message_enter_extension:#', loops= '1', digit_regex='~\\d{2,11}#'))
        return False

    def menu_listen_msgs(self):
        r = self.menu('listen_msgs')
        if r:
            return r
        self.x_work.append(self.play_and_get_digits('phrase:voicemail_listen_file_check:1:2:7:9:5:8:retuen_call', loops= '0', digit_regex='~[0-9#*]'))
        return False

    def menu_config(self):
        r = self.menu('config')
        if r:
            return r
        etree.SubElement(self.x_work, 'pause', milliseconds='250')
        self.x_work.append(self.play_and_get_digits('phrase:voicemail_config_menu:1:2:3:6:0', digit_regex='~[0-6#*]'))
        return False

    def menu_choose_greet(self):
        r = self.menu('choose_greet')
        if r:
            return r
        self.x_work.append(self.play_and_get_digits('voicemail/vm-choose_greeting_choose.wav', digit_regex='~[1-9]'))
        return False

    def menu_record(self, **kwargs):
        playfile = kwargs.get('playfile')
        recfile = kwargs.get('recfile')
        rectype = kwargs.get('rectype')
        if playfile:
            self.session_json['vm_record_current_playfile'] = playfile
        else:
            playfile = self.session_json.get('vm_record_current_playfile', 'voicemail/vm-record_message.wav')
        if recfile:
            self.session_json['vm_record_current_recfile'] = recfile
        else:
            recfile = self.session_json.get('vm_record_current_recfile', 'recording_tmp_1.wav')
        if rectype:
            self.session_json['vm_record_current_rectype'] = rectype
        r = self.menu('record')
        if r:
            return r
        etree.SubElement(self.x_work, 'playback', file=playfile)
        self.x_work.append(self.record_and_get_digits(recfile))
        return False

    def menu_record_review(self):
        r = self.menu('record_review')
        if r:
            return r
        etree.SubElement(self.x_work, 'pause', milliseconds='1000')
        self.x_work.append(self.play_and_get_digits('phrase:voicemail_record_file_check:1:2:3', digit_regex='~[123#]'))
        return

    def menu_chg_pass(self, stage):
        r = self.menu('chg_pass')
        if r:
            return r
        etree.SubElement(self.x_work, 'pause', milliseconds='500')
        if stage == 1:
            self.x_work.append(self.play_and_get_digits('phrase:voicemail_enter_pass:#', digit_regex='~[0-9]{4,}#'))
        if stage == 2:
            etree.SubElement(self.x_work, 'playback', file='ivr/ivr-repeat_this_information')
            etree.SubElement(self.x_work, 'pause', milliseconds='500')
            self.x_work.append(self.play_and_get_digits('phrase:voicemail_enter_pass:#', digit_regex='~[0-9]{4,}#'))
        return

    ###############################################################
    # Menu Support functions
    ###############################################################
    def listen(self, msg_type='new'):
        if msg_type == 'new' and self.session_json.get('vm_mwi_kill_sent', 'no') == 'no':
            self.session_json['vm_mwi_kill_sent'] = 'yes'
            mwi = MessageWaiting()
            mwi.connect()
            mwi.send(self.vmuser, self.vmdomain, 0, 0, True)
            mwi.disconnect()
        cur_msg = self.session_json.get('vm_current_message')
        qsp = self.session_json.get('vm_qs_%s_pickle' % msg_type)
        if qsp:
            qs = pickle.loads(b64decode(qsp.encode()))
        else:
            qs = self.vm.voicemailmessages_set.filter(status=msg_type).order_by('created')[:50] # Limit resultset to 50 entries.  This is the equivalent of SQL’s LIMIT clause.
            self.session_json['vm_qs_%s_pickle' % msg_type] = b64encode(pickle.dumps(qs)).decode() # we pickle the queryset so we always get back to the same dataset within any one voicemail session.
        breaknext = False
        msg_count = len(qs)
        if msg_count < 1:
            etree.SubElement(self.x_work, 'playback', file='phrase:voicemail_message_count:%s:%s' % (msg_count, msg_type))
            return False
        i = 0
        for q in qs:
            i += 1
            if not cur_msg or breaknext:
                breaknext = False
                break
            if str(q.id) == cur_msg:
                breaknext = True

        if cur_msg == str(q.id):  # We played this one before
            self.session_json['menu'] = 'main'
            return False
        self.session_json['menu'] = 'listen_msgs'
        self.session_json['vm_message_type'] = msg_type
        self.session_json['vm_current_message'] = str(q.id)
        self.session_json['expecting_listen_msgs_menu'] = 'true'  # play_and_get_messages should end up back at the menu with a pb_input
        etree.SubElement(self.x_work, 'playback', file='phrase:voicemail_say_message_number:%s:%s' % (msg_type, i)) # Only say for saved, as new messages are saved or deleted number will always be 1.
        vm_say_caller_id_number = self.session_json.get('variable_vm_say_caller_id_number', 'true')
        if vm_say_caller_id_number == 'true':
            etree.SubElement(self.x_work, 'playback', file='phrase:voicemail_say_phone_number:%s' % q.caller_id_number)
        vm_say_date_time = self.session_json.get('variable_vm_say_date_time', 'true')
        if vm_say_date_time == 'true':
            etree.SubElement(self.x_work, 'playback', file='phrase:voicemail_say_date:%s' % int(q.created.timestamp()))  # lookup short-date-time
        self.x_work.append(self.play_and_get_digits(self.get_fs_file_path(q.filename.name, q.filestore),
                                            loops='0', input_timeout='3000', digit_regex='~[125789#]' ))
        return True

    def save_recording(self, tmpfile):
        rectype = self.session_json.get('vm_record_current_rectype', 'greeting')
        if rectype == 'greeting':
            recname = 'greeting_%s.wav' % self.session_json.get('vm_current_greeting', '1')
        elif rectype == 'name':
            recname = 'recording_name.wav'
        else:
            return False
        rec_file_exists = True
        try:
            rec = VoicemailGreeting.objects.get(voicemail_id=self.vm.id, name=recname)
        except VoicemailGreeting.DoesNotExist:
            rec_file_exists = False
            rec = VoicemailGreeting.objects.create(name=recname, voicemail_id=self.vm,
                    description='via voicemail handler.', updated_by='%s@%s' % (self.vmuser, self.vmdomain))
        if rec_file_exists:
            rec.filename.delete(save=False)
        rf = open(tmpfile, 'rb')
        djangofile = File(rf)
        rec.filename.save(recname, djangofile)
        return True

    def msg_forward_email(self, msg=None, vm=None):
        if not msg:
            msg = self.get_vm_message()
        if not msg:
            return False
        if not vm:
            vm = self.vm
        if not vm.mail_to:
            return False
        m = PbxTemplateMessage()
        tp_subject, tp_body, tp_type = m.GetTemplate(
            vm.extension_id.domain_id_id, '%s-%s' % (
                            self.session_json.get('variable_default_language', 'en'),
                            self.session_json.get('variable_default_dialect', 'us')
                            ),
            'voicemail', 'default'
            )
        if not tp_subject:
            return False
        file_to_attach = None
        if vm.attach_file == 'link':
            download_link = '%s/portal/voicemail/%s_%s' % (settings.PBX_SERVER_URL, str(vm.id), str(msg.id))
            #download_link = '%s/portal/voicemail/%s_%s' % ('http://localhost:8080', str(vm.id), str(msg.id)) # Used for debug purposes
            body_message = 'Donwload Link: <a href=\"%s\">%s</a>' % (download_link, download_link)
        elif vm.attach_file == 'true':
            file_to_attach = msg.filename
            body_message = 'Audio file attached'
        else:
            body_message = 'Voicemail details only.  No attachmant or download link specified.'

        msg_caller_id_name = msg.caller_id_name if msg.caller_id_name else ''
        subject = tp_subject.replace('$', '').format(
                caller_id_name=msg_caller_id_name, caller_id_number=msg.caller_id_number,
                message_duration=msg.duration)
        body = tp_body.replace('$', '').format(
                caller_id_name=msg_caller_id_name, caller_id_number=msg.caller_id_number,
                voicemail_name_formatted=vm.mail_to, message_date=msg.created,
                message_duration=msg.duration, message=body_message
                )
        try:
            out = m.Send(vm.mail_to, subject, body, tp_type, file_to_attach)
        except:
            return False
        return out[0]

    def msg_forward(self, vm):
        msg = self.get_vm_message()
        if not msg:
            return False
        self._msg_save(msg, 'saved')
        VoicemailMessages.objects.create(
            voicemail_id=vm,
            filename=msg.filename,
            name=msg.name,
            filestore=msg.filestore,
            caller_id_name=msg.caller_id_name,
            caller_id_number=msg.caller_id_number,
            duration=msg.duration,
            status='new',
            updated_by='%s@%s' % (self.vmuser, self.vmdomain)
        )
        etree.SubElement(self.x_work, 'playback', file='ivr/ivr-thank_you')
        etree.SubElement(self.x_work, 'playback', file='misc/error.wav')
        return True

    def msg_save(self):
        msg = self.get_vm_message()
        if not msg:
            return False
        self._msg_save(msg, 'saved')
        return True

    def msg_return_call(self):
        msg = self.get_vm_message()
        if not msg:
            return False
        self._msg_save(msg, 'saved')
        etree.SubElement(self.x_work, 'playback', file='ivr/ivr-transferring_to')
        etree.SubElement(self.x_work, 'playback', file='ivr/ivr-number')
        etree.SubElement(
            self.x_work, 'execute', application='transfer',
            data='%s XML %s' % (msg.caller_id_number, self.qdict.get('Caller-Context', 'None'))
        )
        return True

    def msg_delete(self):
        msg = self.get_vm_message()
        if not msg:
            return False
        self._msg_save(msg, 'deleted')
        return True

    def msgs_summary(self):
        new_count, saved_count = self.get_message_counts()
        self.session_json['vm_new_count'] = new_count
        self.session_json['vm_saved_count'] = saved_count
        etree.SubElement(self.x_work, 'playback', file='phrase:voicemail_message_count:%s:new' % new_count)
        etree.SubElement(self.x_work, 'playback', file='phrase:voicemail_message_count:%s:saved' % saved_count)

    ###############################################################
    # General Support functions
    ###############################################################
    def check_auth(self):
        if self.session_json.get('variable_voicemail_authorized', 'false') == 'true':
            return True
        if self.session_json.get('expecting_pin', 'false') == 'true':
            if self.vm.password == self.qdict.get('pb_input', ''):
                self.session_json['variable_voicemail_authorized'] = 'true'
                self.session.save()
                return True
            etree.SubElement(self.x_work, 'playback', file='phrase:voicemail_fail_auth:#')
            etree.SubElement(self.x_work, 'hangup')
        else:
            self.x_work.append(self.play_and_get_digits('phrase:voicemail_enter_pass:#'))
            self.session_json['expecting_pin'] = 'true'
            self.session.save()
        return False

    def _msg_save(self, msg, status):
        msg.status = status
        msg.read = timezone.now()
        msg.save()

    def get_message_counts(self, vm=None):
        if not vm:
            vm = self.vm
        new_count = vm.voicemailmessages_set.filter(status='new').count()
        saved_count = vm.voicemailmessages_set.filter(status='saved').count()
        return((new_count, saved_count))

    def create_vm_message(self, voicemail_id, filename, duration):
        try:
            rec = VoicemailMessages.objects.create(
                voicemail_id=voicemail_id,
                name='msg_%s' % filename.split('/')[-1:][0],
                caller_id_name=self.session_json.get('variable_caller_id_name', 'anonymous'),
                caller_id_number=self.session_json.get('variable_caller_id_number', 'anonymous'),
                duration=duration
                )
        except:
            rec = None
        return rec

    def get_vm_object(self):
        self.vm = None
        id = self.session_json.get('vm_object_id')
        if id:
            try:
                self.vm = Voicemail.objects.get(pk=id)
            except Voicemail.DoesNotExist:
                pass
            return
        try:
            self.vm = Voicemail.objects.get(enabled='true', 
                extension_id__domain_id__name=self.vmdomain, extension_id__extension=self.vmuser)
            self.session_json['vm_object_id'] = str(self.vm.id)
        except Voicemail.DoesNotExist:
            pass
        return

    def get_msg_forward_vm(self, extn):
        try:
            return Voicemail.objects.get(enabled='true', 
                extension_id__domain_id__name=self.vmdomain, extension_id__extension=extn)
        except Voicemail.DoesNotExist:
            return False

    def get_vm_message(self):
        cur_msg = self.session_json.get('vm_current_message')
        try:
            return VoicemailMessages.objects.get(pk=cur_msg)
        except VoicemailMessages.DoesNotExist:
            return False

    def get_fs_file_path(self, filename, filestore):
        # typical filename fs/voicemail/default/test1.lantecsip.uk/201/greeting_2.wav
        if settings.PBX_FREESWITCH_LOCAL and settings.PBX_USE_LOCAL_FILE_STORAGE:
            return os.path.join(settings.MEDIA_ROOT, filename)
        if settings.PBX_USE_LOCAL_FILE_STORAGE:
            return os.path.join(settings.MEDIA_ROOT, filename)
        else:
            hosts = HostsLookup()
            filestore_ip = hosts.get_host(filestore)
            return '%s' % (settings.PBX_FILESTORE_SCHEME, os.path.join(filestore_ip, filename.lstrip('/')))

    def set_skip_invalid(self):
        self.session_json['vm_menu_skip_invalid'] = 'true'

    def unset_skip_invalid(self):
        self.session_json['vm_menu_skip_invalid'] = None

    def get_uploaded_file(self):
        # workaround since freeswitch 10 httapi record prepends a UUID to the filename
        # this strips it on the part following the underscore.
        filename = self.fdict['rd_input'].name.split('_')[-1:][0]
        tmpfile = self.get_tmp_recording_filename()
        if not tmpfile:
            return False
        with open(tmpfile, 'wb') as destination:
            for chunk in self.fdict['rd_input'].chunks():
                destination.write(chunk)
        return True

    def get_tmp_recording_filename(self):
        try:
            return self.session_json['tmpfiles'].get(self.session_json.get('vm_record_current_recfile'))
        except KeyError:
            return False
