#!/home/django-pbx/envdpbx/bin/python
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

import argparse
import json
from resources.pbx.amqpconnection import AmqpConnection
from resources.pbx.shellcommand import shcommand

nonstr = 'none'

def handle_firewall(event):
    action = event.get('Action', 'add')
    if action in ['add', 'delete']:
        iptype = event.get('IP-Type', 'ipv4')
        fwlist = event.get('Fw-List', 'sip-customer')
        ip_address = event.get('IP-Address', '192.168.42.1')
        shcommand(['/usr/local/bin/fw-%s-%s-%s-list.sh' % (action, iptype, fwlist), ip_address])
    if action == 'save':
        shcommand(['/usr/local/bin/fw-save-ruleset.sh'])

def on_message(channel, method, properties, body):
    msg = body.decode('utf8')
    event = json.loads(msg)
    event_name = event.get('Event-Name', nonstr)
    if event_name == 'FIREWALL':
        handle_firewall(event)

def main():
    broker = '127.0.0.1'
    broker_port = 5672
    broker_user = 'djangopbx'
    broker_password = 'djangopbx-insecure'
    if args.host:
        broker = args.host
    if args.port:
        broker_port = args.port
    if args.user:
        broker_user = args.user
    if args.password:
        broker_password = args.password
    routing = {'TAP.Firewall': ['*.*.*.*.*']}
    mq = AmqpConnection(broker, broker_port, broker_user, broker_password,
                            routing, False, '%s_remote_event_queue' % broker)
    mq.connect()
    mq.setup_exchange('TAP.Firewall')
    mq.setup_queues()
    mq.consume(on_message)

if __name__ == '__main__':
    nonstr = 'none'
    parser=argparse.ArgumentParser(description='AMQP Remote Event Listener')
    parser.add_argument('--host')
    parser.add_argument('--port', type=int)
    parser.add_argument('--user')
    parser.add_argument('--password')
    args=parser.parse_args()
    main()
