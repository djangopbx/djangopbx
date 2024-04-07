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
import os
import datetime
import time
import random
import pika
import socket
import functools
import json


class AmqpConnection:

    def __init__(self, hostname='localhost', port=5672, username='guest', password='djangopbx-insecure'):
        self.rabbithostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None
        try:
            self.hostname = socket.gethostname()
        except:
            self.hostname = 'localhost'

    def connect(self):
        print('Attempting to connect to %s' % self.rabbithostname)
        params = pika.ConnectionParameters(
            host=self.rabbithostname,
            port=self.port,
            credentials=pika.PlainCredentials(self.username, self.password),
            client_properties={'connection_name': '%s-EventReceiver' % self.hostname})
        try:
            self.connection = pika.BlockingConnection(parameters=params)
        except pika.exceptions.ProbableAuthenticationError:
            print('ConnectionClosedByBroker: (403) ACCESS_REFUSED')
            os._exit(1)
        self.channel = self.connection.channel()
        print('Connected Successfully to %s\n' % self.rabbithostname)

    def setup_queues(self):
        self.queue = '%s_event_queue' % self.hostname
        self.channel.queue_declare(self.queue, auto_delete=False, durable=True)
        self.channel.queue_bind(self.queue, exchange='TAP.Events', routing_key='*.*.CUSTOM.*.*')
        self.channel.queue_bind(self.queue, exchange='TAP.Events', routing_key='*.*.CHANNEL_HANGUP_COMPLETE.*.*')
        #self.channel.queue_bind(self.queue, exchange='TAP.Events', routing_key='*.*.*.*.*')
        #self.channel.queue_bind(self.queue, exchange='TAP.Events', routing_key='FreeSWITCH.#')

    def _consume(self, on_message):
        if self.connection.is_closed or self.channel.is_closed:
            self.connect()
            self.setup_queues()
        try:
            self.channel.basic_consume(queue=self.queue, auto_ack=True, on_message_callback=on_message)
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print('Keyboard interrupt received')
            self.channel.stop_consuming()
            self.connection.close()
            os._exit(1)
        except pika.exceptions.ChannelClosedByBroker:
            print('Channel Closed By Broker Exception')

    def consume(self, on_message):
        tries = -1
        backoff = 2
        jitter = 0 # Can be a (min, max) tuple
        delay = 1
        max_delay=None

        while tries:
            try:
                return self._consume(on_message)
            except Exception as e:
                tries -= 1
                if not tries:
                    raise
                print('Event cli: %s, retrying in %s seconds...' % (e, delay))
                time.sleep(delay)
                delay *= backoff
                if isinstance(jitter, tuple):
                    delay += random.uniform(*jitter)
                else:
                    delay += jitter
                if max_delay is not None:
                    delay = min(_delay, max_delay)


def on_message(channel, method, properties, body):
    msg = body.decode('utf8')
    event = json.loads(msg)
    event_name = event.get('Event-Name', nonstr)
    event_subclass = event.get('Event-Subclass')
    if event_subclass:
        print('%s, %s\n' % (event_name, event_subclass))
    else:
        print('%s\n' % event_name)
    print(msg)
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
    mq = AmqpConnection(broker, broker_port, broker_user, broker_password)
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
