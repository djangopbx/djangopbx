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

import time
import json
import socket
from django.conf import settings
from tenants.pbxsettings import PbxSettings
from pbx.fseventsocket import EventSocket
from pbx.amqpcmdevent import AmqpCmdEvent


class FsCmdAbsLayer:

    loc_ev_skt = False
    responses = []

    def __init__(self, debug=False):
        self.debug = debug
        try:
            self.hostname = socket.gethostname()
        except:
            self.hostname = 'localhost'
        s = PbxSettings().default_settings('cluster', 'use_local_event_socket', 'boolean', 'true', True)[0]
        if s == 'true':
            self.loc_ev_skt = True
        if self.loc_ev_skt:
            self.broker = EventSocket()
            if self.debug:
                print('Event Socket')
            self.freeswitches = [self.hostname]
        else:
            self.broker = AmqpCmdEvent()
            if self.debug:
                print('Event Broker')
            self.freeswitches = self.broker.freeswitches

    def connect(self):
        if self.loc_ev_skt:
            return self.broker.connect(*settings.EVSKT)
        else:
            result = self.broker.connect()
        if result:
            self.broker.setup_queues()
            self.broker.consume()
        return result

    def send(self, payload, host=None):
        if self.loc_ev_skt:
            self.responses.append(self.broker.send(payload))
        else:
            if payload.startswith('sendevent'):
                self.broker.publish(self.build_event(payload), host)
                return
            self.broker.publish(payload.removeprefix('api '), host)

    def process_events(self, timeout=3):
        if self.loc_ev_skt:
            return
        self.broker.process_events(timeout)

    def get_responses(self):
        if self.loc_ev_skt:
            return
        for resp in self.broker.responses:
            output = json.loads(resp)
            self.responses.append(output['output'])

    def clear_responses(self):
        if not self.loc_ev_skt:
            self.broker.clear_responses()
        self.responses = []

    def disconnect(self):
        self.broker.disconnect()

    def build_event(self, payload):
        ev_name, hdrs = self.parse_event(payload)
        return 'luarun send_event.lua %s --h %s' % (ev_name, ' --h '.join(['%s %s' % (k, v) for k, v in hdrs.items()]))

    def parse_event(self, payload):
        hdrs = {}
        ev = payload.split('\n')
        ev_name = ev[0].split(' ')
        if len(ev_name) > 0:
            ev_name = ev_name[1]
        else:
            ev_name = 'NONE'
        for header in ev:
            if ':' in header:
                h, v = header.split(': ')
                hdrs[h] = v
        return (ev_name, hdrs)
