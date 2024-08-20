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

from lxml import etree
from .httapihandler import HttApiHandler
from tenants.models import Domain
from recordings.models import Recording


class RecordingsHandler(HttApiHandler):

    handler_name = 'recordings'

    def get_data(self):
        if self.getfile:
            self.get_uploaded_file()

        if self.exiting:
            return self.return_data('Ok\n')

        self.x_root = self.XrootApi()
        etree.SubElement(self.x_root, 'params')
        self.x_work = etree.SubElement(self.x_root, 'work')

        next_action =  self.get_next_action()

        if next_action:
            if next_action == 'chk-pin':
                self.act_chk_pin()
            elif next_action == 'record':
                self.act_record()
            elif next_action == 'review':
                self.act_review()
            elif next_action == 'rerecord':
                self.act_rerecord()
        else:
            self.act_get_pin()

        etree.indent(self.x_root)
        xml = str(etree.tostring(self.x_root), "utf-8")
        return xml

    def act_get_pin(self):
        pin_number = self.session_json.get('variable_pin_number')
        if not pin_number:
            return self.error_hangup('R2001')

        self.session_json['pin_number'] = pin_number
        self.session_json[self.next_action_str] = 'chk-pin'
        self.session.save()
        self.x_work.append(self.play_and_get_digits('phrase:voicemail_enter_pass:#'))
        return

    def act_chk_pin(self):
        pin_number = self.session_json['pin_number']
        if pin_number == self.qdict.get('pb_input', ''):
            self.session_json[self.next_action_str] = 'record'
            self.session.save()
            self.x_work.append(self.play_and_get_digits('ivr/ivr-id_number.wav'))
        else:
            etree.SubElement(self.x_work, 'playback', file='phrase:voicemail_fail_auth:#')
            etree.SubElement(self.x_work, 'hangup')
        return

    def act_record(self):
        rec_no = self.qdict.get('pb_input', '')
        rec_prefix = self.session_json.get('variable_recording_prefix', 'recording')
        rec_file = '%s%s.wav' % (rec_prefix, rec_no)
        self.session_json['rec_file'] = '%s/%s/%s' % (
            self.recordings_dir, self.session_json['variable_domain_name'], rec_file
            )
        self.session_json[self.next_action_str] = 'review'
        self.session.save()
        etree.SubElement(self.x_work, 'playback', file='ivr/ivr-recording_started.wav')
        self.x_work.append(self.record_and_get_digits(rec_file))
        return

    def act_review(self):
        rec_file = self.session_json['rec_file']
        self.session_json[self.next_action_str] = 'rerecord'
        self.session.save()
        etree.SubElement(self.x_work, 'pause', milliseconds='1000')
        etree.SubElement(self.x_work, 'playback', file=rec_file)
        etree.SubElement(self.x_work, 'pause', milliseconds='500')
        etree.SubElement(self.x_work, 'playback', file='voicemail/vm-press.wav')
        etree.SubElement(self.x_work, 'playback', file='digits/1.wav')
        etree.SubElement(self.x_work, 'playback', file='voicemail/vm-rerecord.wav')
        etree.SubElement(self.x_work, 'pause', milliseconds='250')
        etree.SubElement(self.x_work, 'playback', file='digits/2.wav')
        self.x_work.append(self.play_and_get_digits('voicemail/vm-save_recording.wav', 'pb_input', '~\\d{1}'))
        return

    def act_rerecord(self):
        re_rec = self.qdict.get('pb_input', '')
        if re_rec == '1':
            rec_file = self.session_json['rec_file']
            self.session_json[self.next_action_str] = 'review'
            self.session.save()
#            etree.SubElement(self.x_work, 'continue')
            etree.SubElement(self.x_work, 'playback', file='ivr/ivr-recording_started.wav')
            self.x_work.append(self.record_and_get_digits(rec_file))
        else:
            etree.SubElement(self.x_work, 'playback', file='ivr/ivr-recording_saved.wav')
            etree.SubElement(self.x_work, 'hangup')
        return

    def get_uploaded_file(self):
        rec_file_exists = True
        # workaround since freeswitch 10 httapi record prepends a UUID to the filename
        # this strips it on the known part of the name 'recording'
        received_file_name = 'recording%s' % self.fdict['rd_input'].name.rsplit('recording', 1)[1]
        try:
            rec = Recording.objects.get(domain_id=self.domain_uuid, name=received_file_name)
        except Recording.DoesNotExist:
            rec_file_exists = False
            d = Domain.objects.get(pk=self.domain_uuid)
            rec = Recording.objects.create(name=received_file_name, domain_id=d, 
                    description='via recordings (%s)' % self.qdict.get('Caller-Destination-Number', ''))
        if rec_file_exists:
            rec.filename.delete(save=False)
        rec.filename.save(received_file_name, self.fdict['rd_input'])
        return
