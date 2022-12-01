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

import socket
import logging
import time

logger = logging.getLogger(__name__)


class EventSocket:

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.headers = {}
        self.auth_fail_str = ' '


    def __del__(self):
        if (self.sock):
            self.sock.shutdown(1)
            self.sock.close()


    def connect(self, host, port, password):
        self.password = 'auth %s' % password
        try:
            self.sock.connect((host, port))
        except socket.error as err:
            logger.warn('[Event Socket] Connect Error: {}'.format(err))
            return False
        if not self.auth():
            logger.warn('[Event Socket] Auth failed: {}'.format(self.auth_fail_str))
            return False
        return True


    def auth(self):
        self.read()
        if 'Content-Type' in self.headers:
            if self.headers['Content-Type'] == 'auth/request':
                self.send(self.password)
                if 'Content-Type' in self.headers:
                    if self.headers['Content-Type'] == 'command/reply':
                        if 'Reply-Text' in self.headers:
                            if self.headers['Reply-Text'] == '+OK accepted':
                                return True
                    else:
                        self.auth_fail_str = 'No commanf/reply stage 2.'
                else:
                    self.auth_fail_str = 'No Content-Type header stage 2.'
            else:
                self.auth_fail_str = 'No auth/request stage 1.'
        else:
            self.auth_fail_str = 'No Content-Type header stage 1.'
        return False


    def send(self, cmd):
        cmd = '%s\n\n' % cmd
        try:
            self.sock.sendall(cmd.encode())
        except socket.error as err:
            logger.warn('[Event Socket] Send Error: {}'.format(err))
            return False
        self.read()
        return self.body


    def read(self):
        time.sleep(.01) #allow fs time to send body
        try:
            self.msg = self.sock.recv(4096)
        except socket.error as err:
            logger.warn('[Event Socket] Send Error: {}'.format(err))
            return False
        self.parse_msg()
        return


    def parse_msg(self):
        self.headers.clear()
        self.msg = self.msg.decode()
        hdr_end = self.msg.find('\n\n')
        if hdr_end == -1:
            logger.warn('[Event Socket] Double linefeed not found.')
            hdr = self.msg
            self.body = self.msg
        else:
            hdr = self.msg[ : hdr_end]
            self.body = self.msg[hdr_end+2 :]
        hdrs = hdr.split('\n')
        for h in hdrs:
            if ':' in h:
                kv = h.split(': ')
                self.headers[kv[0]] = kv[1]
        return

