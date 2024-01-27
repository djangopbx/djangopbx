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
import time
import random
import logging
import pika
import socket
import functools
import json
from django.utils.translation import gettext_lazy as _
from django.core.management.base import BaseCommand
from switch.models import IpRegister
from tenants.models import DefaultSetting

logger = logging.getLogger(__name__)
logging.getLogger("pika").setLevel(logging.WARNING)


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
        if logger is not None:
            logger.info('Event Receiver: Attempting to connect to %s' % self.rabbithostname)
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
                logger.info('Event Receiver: Connection refused from %s' % self.rabbithostname)
            os._exit(1)
        self.channel = self.connection.channel()
        if logger is not None:
            logger.info('Event Receiver: Connected Successfully to %s' % self.rabbithostname)
        print('Connected Successfully to %s' % self.rabbithostname)

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
                if logger is not None:
                    logger.warning('Event Receiver: %s, retrying in %s seconds...' % (e, delay))
                time.sleep(delay)
                delay *= backoff
                if isinstance(jitter, tuple):
                    delay += random.uniform(*jitter)
                else:
                    delay += jitter
                if max_delay is not None:
                    delay = min(_delay, max_delay)


class Command(BaseCommand):
    help = 'PBX Event Receiver'
    debug = False

    def on_message(self, channel, method, properties, body):
        msg = body.decode('utf8')
        if self.debug:
            if logger is not None:
                logger.debug('Event Receiver: %s', msg)
            print(msg)
        event = json.loads(msg)
        if event.get('Event-Subclass', 'none') == 'sofia::register':
            self.handle_register(event)


    def handle(self, *args, **kwargs):
        mb = {'message_broker': '127.0.0.1', 'message_broker_port': 5672, 'message_broker_password': 'djangopbx-insecure', 'message_broker_user': 'guest'}
        mbl = DefaultSetting.objects.filter(
                category='cluster',
                subcategory__istartswith='message_broker',
                enabled='true',
                )
        for mbr in mbl:
            if mbr.value_type == 'text':
                mb[mbr.subcategory] = mbr.value
            if mbr.value_type == 'numeric':
                try:
                    mb[mbr.subcategory] = int(mbr.value)
                except ValueError:
                    pass

        mq = AmqpConnection(mb['message_broker'], mb['message_broker_port'], mb['message_broker_user'], mb['message_broker_password'])
        mq.connect()
        mq.setup_queues()
        mq.consume(self.on_message)

    def handle_register(self, event):
        if event.get('status', 'N/A').startswith('Registered'):
            ip_address = event.get('network-ip', '192.168.42.1')
            ip, created = IpRegister.objects.update_or_create(address=ip_address, defaults={"status": 1})


