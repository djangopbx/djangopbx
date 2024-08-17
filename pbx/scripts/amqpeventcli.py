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

import sys
import argparse
import json
from resources.pbx.amqpconnection import AmqpConnection


def on_message(channel, method, properties, body):
    msg = body.decode('utf8')
    event = json.loads(msg)
    event_name = event.get('Event-Name', 'none')
    event_subclass = event.get('Event-Subclass')
    if event_subclass:
        print('%s, %s\n' % (event_name, event_subclass))
    else:
        print('%s\n' % event_name)
    sys.stdout.write(msg)
    print('\n')

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
    #routing = {'TAP.Events': ['*.*.CUSTOM.*.*', '*.*.CHANNEL_HANGUP_COMPLETE.*.*', '*.*.CHANNEL_CALLSTATE.*.*']}
    routing = {'TAP.Events': ['*.*.*.*.*']}
    mq = AmqpConnection(broker, broker_port, broker_user, broker_password,
                            routing, True, '%s_cli_event_queue' % broker)
    mq.connect()
    mq.setup_queues()
    mq.consume(on_message)

if __name__ == '__main__':
    nonstr = 'none'
    parser=argparse.ArgumentParser(description='CLI AMQP FreeSWITCH Event Listener')
    parser.add_argument('--host')
    parser.add_argument('--port', type=int)
    parser.add_argument('--user')
    parser.add_argument('--password')
    args=parser.parse_args()
    main()
