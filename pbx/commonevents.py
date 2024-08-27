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

from pbx.fscmdabslayer import FsCmdAbsLayer
from .scripts.resources.pbx.fsevent import FsEvent


class PbxEvent():
    def __init__(self):
        self.connected = False
        self.es = FsCmdAbsLayer()
        self.connect()

    def connect(self):
        if self.es.connect():
            self.connected = True
        return

    def disconnect(self):
        self.es.disconnect()
        return

    def send(self, *args, **kwargs):
        raise NotImplementedError('Subclasses must implement this method.')


class PresenceIn(PbxEvent):
    def send(self, user_uuid, status, user_code, domain_name, host=None):
        if not self.connected:
            return False
        user_id = '%s@%s' % (user_code, domain_name)
        fse = FsEvent('PRESENCE_IN')
        fse.addHeader('proto', 'sip')
        fse.addHeader('event_type', 'presence')
        fse.addHeader('alt_event_type', 'dialog')
        fse.addHeader('Presence-Call-Direction', 'outbound')
        fse.addHeader('from', user_id)
        fse.addHeader('login', user_id)
        fse.addHeader('unique-id', user_uuid)
        fse.addHeader('status', 'Active (1 waiting)')
        if status == 'true':
            fse.addHeader('answer-state', 'terminated')
        else:
            fse.addHeader('answer-state', 'confirmed')
            fse.addHeader('rpid', 'unknown')
            fse.addHeader('event_count', '1')
        self.es.clear_responses()
        self.es.send(fse.getEvent(), host)
        self.es.process_events()
        self.es.get_responses()
        return True

class MessageWaiting(PbxEvent):
    def send(self, user_name, domain_name, new, saved, kill_mwi=False, host=None):
        if not self.connected:
            return False
        sip_profile = self.get_sofia_profile(user_name, domain_name)
        if not sip_profile:
            return False
        fse = FsEvent('message_waiting')
        fse.addHeader('sofia-profile', sip_profile)
        fse.addHeader('MWI-Message-Account', 'sip:%s@%s' % (user_name, domain_name))
        if kill_mwi:
            fse.addHeader('MWI-Messages-Waiting', 'no')
            fse.addHeader('MWI-Voice-Message', '0/0 (0/0)')
        else:
            fse.addHeader('MWI-Messages-Waiting', 'yes' if new > 0 else 'no')
            fse.addHeader('MWI-Voice-Message', '%s/%s (0/0)' % (new, saved))
        self.es.clear_responses()
        self.es.send(fse.getEvent(), host)
        self.es.process_events()
        self.es.get_responses()
        return True

    def get_sofia_profile(self, user, domain):
        self.es.send('api sofia_contact */%s@%s' % (user, domain))
        self.es.process_events()
        self.es.get_responses()
        for resp in self.es.responses:
            if not resp:
                continue
            if resp.startswith('error'):
                continue
            parts = resp.split('/')
            if len(parts) > 1:
                return parts[1]
        return False
