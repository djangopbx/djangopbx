#
#    DjangoPBX
#
#    MIT License
#
#    Copyright (c) 2016 - 2023 Adrian Fretwell <adrian@djangopbx.com>
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
import telnetlib


class EventSocket:
    sleep_time = 0.005

    def __init__(self, host='127.0.0.1', password='ClueCon', port=8021):
        self.host = host
        self.port = port
        self.password = password
        self.headers = {}
        self.body = None
        self.auth_fail_str = ' '
        self.tn = telnetlib.Telnet()

    def __del__(self):
        if (self.tn):
            self.tn.close()

    def connect(self):
        self.auth_string = 'auth %s' % self.password
        try:
            self.tn.open(self.host, self.port)
        except:
            return False
        self.read()
        if self.headers['Content-Type'] == 'auth/request':
            self.send(self.auth_string)
            self.read()
            if not self.headers['Reply-Text'] == '+OK accepted':
                self.tn.close()
                return False
        return True

    def send(self, cmd):
        cmd = '%s\n\n' % cmd
        try:
            self.tn.write(cmd.encode())
        except:
            return False
        return True

    def parse_header(self, hdr):
        hdrs = hdr.split('\n')
        for h in hdrs:
            if ':' in h:
                kv = h.split(': ')
                self.headers[kv[0]] = kv[1]
        return

    def read(self):
        self.body = ''
        content = []
        header = self.tn.read_until(b'\n\n', 5)
        self.parse_header(header.decode())
        if 'Content-Length' in self.headers:
            try:
                body_size = int(self.headers['Content-Length'])
            except:
                body_size = 0
            c = 0
            while (c < body_size):
                # sleep for sometime to stop loop consuming CPU
                time.sleep(self.sleep_time)
                tmp = self.tn.read_eager().decode()
                if tmp:
                    c = c + len(tmp)
                    content.append(tmp)
            self.body = ''.join(content)
        return (self.headers, self.body)

    def close(self):
        if (self.tn):
            self.tn.close()
