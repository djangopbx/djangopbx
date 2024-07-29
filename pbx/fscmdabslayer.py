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
from pbx.fseventsocket import EventSocket
from pbx.amqpcmdevent import AmqpCmdEvent


class FsCmdAbsLayer:

    loc_ev_skt = False
    responses = []

    def __init__(self, debug=False):
        self.debug = debug
        self.err_count = 0
        try:
            self.hostname = socket.gethostname()
        except:
            self.hostname = 'localhost'
        self.loc_ev_skt = settings.PBX_USE_LOCAL_EVENT_SOCKET

        if self.loc_ev_skt:
            self.broker = EventSocket()
            if self.debug:
                print('Event Socket')
            self.freeswitches = [self.hostname]
        else:
            self.broker = AmqpCmdEvent(self.debug)
            if self.debug:
                print('Event Broker')
            self.freeswitches = self.broker.freeswitches

    def connect(self):
        if self.loc_ev_skt:
            resp = self.broker.connect(*settings.EVSKT)
            if not resp:
                self.err_count += 1
            return resp
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
            if self.err_count > 0:
                return False
            return True
        for resp_raw in self.broker.responses:
            output_json = json.loads(resp_raw)
            resp = output_json['output']
            if '-ERR' in resp:
                self.err_count += 1
            self.responses.append(resp)
            # Return True if at least one freeswitch did not return an error
            if self.err_count < len(self.freeswitches):
                return True
        return False

    def clear_responses(self):
        if not self.loc_ev_skt:
            self.broker.clear_responses()
        self.responses = []
        self.err_count = 0

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

    def adhoc_publish(self, payload, routing, exchange):
        if not self.loc_ev_skt:
            self.broker.adhoc_publish(payload, routing, exchange)
