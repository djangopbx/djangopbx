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
import datetime
import time
import random
import logging
import pika
import socket
import functools
import json


logger = logging.getLogger(__name__)
logging.getLogger("pika").setLevel(logging.WARNING)


class AmqpConnection:

    def __init__(self, hostname='localhost', port=5672, username='guest',
                    password='djangopbx-insecure', routing=None,
                    auto_delete=False, event_queue_name=None):
        self.rabbithostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None
        self.auto_delete = auto_delete
        self.pid = os.getpid()
        try:
            self.hostname = socket.gethostname()
        except:
            self.hostname = 'localhost'
        if routing:
            self.routing = routing
        else:
            self.routing = {'TAP.Events': [
                '*.*.CUSTOM.*.*',
                '*.*.CHANNEL_CREATE.*.*',
                '*.*.CHANNEL_CALLSTATE.*.*',
                '*.*.CHANNEL_UUID.*.*',
                '*.*.CHANNEL_BRIDGE.*.*',
                '*.*.CHANNEL_ANSWER.*.*',
                '*.*.CHANNEL_HANGUP_COMPLETE.*.*',
                '*.*.RECORD_STOP.*.*',
                '*.*.CHANNEL_HOLD.*.*',
                '*.*.CHANNEL_UNHOLD.*.*',
                '*.*.DTMF.*.*'
                ]}
        if event_queue_name:
            self.event_queue_name = event_queue_name
        else:
            self.event_queue_name = '%s_event_queue' % self.hostname

    def connect(self):
        if logger is not None:
            logger.info('Event Receiver PID: %s Attempting to connect to %s' % (self.pid, self.rabbithostname))
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
            if logger is not None:
                logger.info('Event Receiver PID: %s Connection refused from %s' % (self.pid, self.rabbithostname))
            os._exit(1)
        self.channel = self.connection.channel()
        # To Enable delivery confirmations. This is REQUIRED.
        # self.channel.confirm_delivery()
        if logger is not None:
            logger.info('Event Receiver PID: %s Connected Successfully to %s' % (self.pid, self.rabbithostname))
        print('Connected Successfully to %s' % self.rabbithostname)

    def setup_exchange(self, exchange, exchange_type='topic', passive=False,
                        durable=True, auto_delete=False, internal=False,
                        arguments=None, callback=None):
        self.channel.exchange_declare(exchange, exchange_type, passive, durable,
                                        auto_delete)

    def setup_queues(self):
        self.queue = self.event_queue_name
        self.channel.queue_declare(self.queue, auto_delete=self.auto_delete, durable=True)
        for k, v in self.routing.items():
            for r in v:
                self.channel.queue_bind(self.queue, exchange=k, routing_key=r)

        # Examples of Queue bindings:
        #   self.channel.queue_bind(self.queue, exchange='TAP.Events', routing_key='*.*.CUSTOM.*.*')
        #   self.channel.queue_bind(self.queue, exchange='TAP.Events', routing_key='*.*.CHANNEL_HANGUP_COMPLETE.*.*')
        #   self.channel.queue_bind(self.queue, exchange='TAP.Events', routing_key='*.*.*.*.*')
        #   self.channel.queue_bind(self.queue, exchange='TAP.Events', routing_key='FreeSWITCH.#')

    def _consume(self, on_message):
        if self.connection.is_closed or self.channel.is_closed:
            self.connect()
            self.setup_queues()
        try:
            self.channel.basic_consume(queue=self.queue, auto_ack=True, on_message_callback=on_message)
            self.channel.start_consuming()
        except KeyboardInterrupt:
            if logger is not None:
                logger.info('Event Receiver PID: %s Received interrupt, shutting down... %s' % (self.pid, self.rabbithostname))
            print('Keyboard interrupt received')
            self.channel.stop_consuming()
            self.connection.close()
            os._exit(1)
        except pika.exceptions.ChannelClosedByBroker:
            print('Channel Closed By Broker Exception')
            if logger is not None:
                logger.info('Event Receiver PID: %s Channel closed by broker exception. %s' % (self.pid, self.rabbithostname))

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
                if logger is not None:
                    logger.warning('Event Receiver PID: %s %s, retrying in %s seconds...' % (self.pid, e, delay))
                time.sleep(delay)
                delay *= backoff
                if isinstance(jitter, tuple):
                    delay += random.uniform(*jitter)
                else:
                    delay += jitter
                if max_delay is not None:
                    delay = min(_delay, max_delay)
