#!/usr/bin/python3
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

import sys
from resources.db.pgdb import PgDb
from resources.pbx.telneteventsocket import EventSocket

debug = False

event = 'sendevent PRESENCE_IN\nproto: sip\nevent_type: presence\nalt_event_type: dialog\n Presence-Call-Direction: outbound\nfrom: %s\nlogin: %s\nunique-id: %sstatus: Active (1 waiting)\n%s'
event_on = 'answer-state: confirmed\nrpid: unknown\nevent_count: 1'
event_off = 'answer-state: terminated'

es = EventSocket()
if not es.connect():
    sys.exit('Event socket connection/login error')

dbh = PgDb('djangopbx')
if not dbh.connect():
    sys.exit('Database connection/login error')

with dbh.cursor() as c:
    c.execute('select id, extension, feature_code, status, context from pbx_call_flows')
    while True:
        record = c.fetchone()
        if not record:
            break
        if debug:
            print(record)
        user_id = '%s@%s' % (record[2], record[4])
        if record[3] == 'true':
            event_cmd = event % (user_id, user_id, record[0], event_off)
        else:
            event_cmd = event % (user_id, user_id, record[0], event_on)
        es.send(event_cmd)
        result = es.read()
        if debug:
            print(result[0])
            print(result[1])
es.send('exit')
es.read()
if debug:
    print(result[0])
    print(result[1])
es.close()
