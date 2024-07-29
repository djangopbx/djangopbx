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

import pika
import socket
import logging
import uuid
import time
from django.conf import settings
from tenants.models import DefaultSetting

logger = logging.getLogger(__name__)
logging.getLogger("pika").setLevel(logging.WARNING)


class AmqpCmdEvent:

    mb_key_host = 'message_broker'
    mb_key_port = 'message_broker_port'
    mb_key_user = 'message_broker_user'
    mb_key_pass = 'message_broker_password'
    mb_key_adhoc = 'message_broker_adhoc_publish'
    fs_cmd_exchange = 'TAP.Commands'
    responses = []

    def __init__(self, debug=False):
        self.debug = debug
        self.mb = {self.mb_key_host: '127.0.0.1', self.mb_key_port: 5672,
                    self.mb_key_pass: 'djangopbx-insecure', self.mb_key_user: 'guest', self.mb_key_adhoc: False }
        try:
            self.hostname = socket.gethostname()
        except:
            self.hostname = 'localhost'
        self.inbound_route_key = str(uuid.uuid4()).replace('-', '')
        qs = DefaultSetting.objects.filter(
                category='cluster',
                subcategory__istartswith=self.mb_key_host,
                enabled='true',
                )
        for mbcf in qs:
            if mbcf.value_type == 'text':
                self.mb[mbcf.subcategory] = mbcf.value
            if mbcf.value_type == 'numeric':
                try:
                    self.mb[mbcf.subcategory] = int(mbcf.value)
                except ValueError:
                    pass
            if mbcf.value_type == 'boolean':
                self.mb[mbcf.subcategory] = (True if mbcf.value == 'true' else False)
        self.channel = None
        self.freeswitches = settings.PBX_FREESWITCHES
        if len(self.freeswitches) < 1:
            self.freeswitches = [self.hostname]
        self.switchcount = len(self.freeswitches)
        self.singlehostrequest = False

    def on_response(self, ch, method, props, body):
        if self.debug:
            print('ch')
            print(ch)
            print('method')
            print(method)
            print('props')
            print(props)
            print(body)
        self.responses.append(body.decode().replace('\t', ''))

    def connect(self):
        if logger is not None:
            logger.info('AMQP Cmd Event: Attempting to connect to %s' % self.mb[self.mb_key_host])
        params = pika.ConnectionParameters(
            host=self.mb[self.mb_key_host],
            port=self.mb[self.mb_key_port],
            credentials=pika.PlainCredentials(self.mb[self.mb_key_user], self.mb[self.mb_key_pass]),
            client_properties={'connection_name': '%s-AmqpCmdEvent' % self.hostname})
        try:
            self.connection = pika.BlockingConnection(parameters=params)
        except pika.exceptions.ProbableAuthenticationError:
            if logger is not None:
                logger.info('AMQP Cmd Event: Connection refused from %s' % self.mb[self.mb_key_host])
            return False
        self.channel = self.connection.channel()
        if logger is not None:
            logger.info('AMQP Cmd Event: Connected Successfully to %s' % self.mb[self.mb_key_host])
        return True

    def setup_queues(self):
        result = self.channel.queue_declare(
            queue=self.inbound_route_key,
            passive=False,
            durable=False,
            auto_delete=True,
            arguments=None)
        self.channel.queue_bind(
            self.inbound_route_key,
            self.fs_cmd_exchange,
            routing_key=self.inbound_route_key,
            arguments=None)
        self.callback_queue = result.method.queue

    def clear_responses(self):
        self.responses = []

    def publish(self, payload, host=None):
        if self.connection.is_open and self.channel.is_open:
            if host:
                self.singlehostrequest = True
                freeswitch_route_key = '%s_command' % host
                if self.debug:
                    print('Publishing to %s' % freeswitch_route_key)
                self.channel.basic_publish(
                    exchange=self.fs_cmd_exchange,
                    routing_key=freeswitch_route_key,
                    properties=pika.BasicProperties(
                        headers={'x-fs-api-resp-exchange': self.fs_cmd_exchange, 'x-fs-api-resp-key': self.inbound_route_key} # Add a key/value headers required by FreeSWITCH
                    ),
                    body=payload
                    )
                return

            self.singlehostrequest = False
            for fs in self.freeswitches:
                freeswitch_route_key = '%s_command' % fs
                if self.debug:
                    print('Publishing to %s' % freeswitch_route_key)
                self.channel.basic_publish(
                    exchange=self.fs_cmd_exchange,
                    routing_key=freeswitch_route_key,
                    properties=pika.BasicProperties(
                        headers={'x-fs-api-resp-exchange': self.fs_cmd_exchange, 'x-fs-api-resp-key': self.inbound_route_key} # Add a key/value headers required by FreeSWITCH
                    ),
                    body=payload
                    )

    def adhoc_publish(self, payload, routing='1.2.3.4.5', exchange='TAP.Firewall'):
        if self.connection.is_open and self.channel.is_open and self.mb[self.mb_key_adhoc]:
            try:
                self.channel.basic_publish('TAP.Firewall', routing, payload.encode(),
                    properties=pika.BasicProperties(delivery_mode=2), # Delivery Mode 2 for persistent
                    )
            except:
                logger.warn('AMQP addhoc publish {}: Unable send message {}.'.format(exchange, routing))

    def process_events(self, timeout=3):
        if self.connection.is_open and self.channel.is_open:
            t = time.time()
            while len(self.responses) < self.switchcount:
                self.connection.process_data_events(time_limit=timeout)
                if self.singlehostrequest:
                    break
                if (time.time() - t) > timeout:
                    break

    def consume(self):
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def disconnect(self):
        if self.channel.is_open:
            self.channel.close()
        if self.connection.is_open:
            self.connection.close()
