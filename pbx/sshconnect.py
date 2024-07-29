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
#    Inspired by the SFTP storage backend for Django by Brent Tubbs <brent.tubbs@gmail.com>
#
#    Contributor(s):
#    Adrian Fretwell <adrian@djangopbx.com>
#

import os
import posixpath
import stat
import getpass
import logging
# Workaround for the CryptographyDeprecationWarning: TripleDES has been moved warnings
# this workaround can be removed once the Paramiko devs have worked out a fix
import warnings
from cryptography.utils import CryptographyDeprecationWarning
with warnings.catch_warnings(action="ignore", category=CryptographyDeprecationWarning):
    import paramiko
### End workaround
from paramiko.util import ClosingContextManager

logging.getLogger("paramiko").setLevel(logging.WARNING)

class SSHConnection(ClosingContextManager):

    client = None

    def __init__(self, base_path='', known_host_file=None, interactive=False):
        self.ssh_dict = {}
        self.interactive = interactive
        self.known_host_file = known_host_file
        self.base_path = base_path

    def close(self):
        for k, v in self.ssh_dict.items():
            v['client'].close()

    def connect(self, host, username='django-pbx', port=22, timeout=3.0, password=None):
        if host in self.ssh_dict:
            ssh_host = self.ssh_dict[host]
            self.client = ssh_host['client']
        else:
            ssh_host = self.ssh_dict[host] = {}
            ssh_host['username'] = username
            ssh_host['password'] = password
            ssh_host['port'] = port
            ssh_host['timeout'] = timeout
            self.client = ssh_host['client'] = paramiko.SSHClient()

        known_host_file = self.known_host_file or os.path.expanduser(
            os.path.join("~", ".ssh", "known_hosts")
        )

        if os.path.exists(known_host_file):
            self.client.load_host_keys(known_host_file)

        # Automatically add new host keys for hosts we haven't seen before.
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.client.connect(hostname=host, port=ssh_host['port'], username=ssh_host['username'], password=ssh_host['password'], timeout=ssh_host['timeout'])
        except paramiko.ssh_exception.AuthenticationException as e:
            if self.interactive and not ssh_host['password']:
                # If authentication has failed, and we haven't already tried
                # username/password, and configuration allows it, then try
                # again with username/password.
                if not ssh_host['username']:
                    ssh_host['username'] = getpass.getuser()
                ssh_host["password"] = getpass.getpass()
                self.connect(host, ssh_host['username'], ssh_host['port'], ssh_host['timeout'], ssh_host['password'])
            else:
                raise paramiko.ssh_exception.AuthenticationException(e)

    def ssh(self, host):
        # Lazy SSH connection...
        if not self.ssh_dict.get(host) or not self.ssh_dict[host]['client'].get_transport().is_active():
            self.connect(host)
        return self.ssh_dict.get(host)['client']

    def command(self, host, cmd):
        return self.ssh(host).exec_command(cmd)


class SFTPConnection(SSHConnection):

    def __init__(self, base_path='', known_host_file=None, interactive=False):
        super().__init__(base_path, known_host_file, interactive)
        self.sftp_dict = {}

    def set_base_path(self, base_path):
        self.base_path = base_path

    def is_seekable(self, file_object):
        return not hasattr(file_object, 'seekable') or file_object.seekable()

    def close(self):
        for k, v in self.sftp_dict.items():
            v.close()
        super().close()

    def connect(self, host, username='django-pbx', port=22, timeout=3.0, password=None):
        super().connect(host, username, port, timeout, password)
        if self.client.get_transport():
            self.sftp_dict[host] = self.client.open_sftp()

    def sftp(self, host):
        # Lazy SFTP connection...
        if not self.sftp_dict.get(host) or not self.ssh_dict[host]['client'].get_transport().is_active():
            self.connect(host)
        return self.sftp_dict.get(host)

    def sftp_path(self, name):
        return posixpath.join(self.base_path, name)

    def exists(self, host, name):
        try:
            self.sftp(host).stat(self.sftp_path(name))
            return True
        except FileNotFoundError:
            return False

    def is_dir(self, item):
        if item.st_mode is not None:
            return stat.S_IFMT(item.st_mode) == stat.S_IFDIR
        else:
            return False

    def listdir(self, host, path):
        sftp_path = self.sftp_path(path)
        dirs = []
        files = []
        for item in self.sftp(host).listdir_attr(sftp_path):
            if self.is_dir(item):
                dirs.append(item.filename)
            else:
                files.append(item.filename)
        return (dirs, files)

    def mkdir(self, host, path):
        # Create directory, recursing up to create parent dirs if necessary.
        parent = posixpath.dirname(path)
        print(parent)
        if not self.exists(host, parent):
            self.mkdir(host, parent)
        self.sftp(host).mkdir(path)

    def size(self, host, name):
        sftp_path = self.sftp_path(name)
        return self.sftp(host).stat(sftp_path).st_size

    def get(self, host, remotefile, localfile):
        sftp_path = self.sftp_path(remotefile)
        try:
            self.sftp(host).get(sftp_path, localfile)
            return True
        except FileNotFoundError:
            return False

    def put(self, host, localfile, remotefile):
        sftp_path = self.sftp_path(remotefile)
        return self.sftp(host).put(localfile, sftp_path)

    def save(self, host, name, content):
        # Copy the contents of an open file object (content) to the SFTP server
        if self.is_seekable(content):
            content.seek(0, os.SEEK_SET)
        sftp_path = self.sftp_path(name)
        dirname = posixpath.dirname(sftp_path)
        if not self.exists(host, dirname):
            self.mkdir(host, dirname)
        self.sftp(host).putfo(content, sftp_path)
        return name

    def open(self, host, name, mode='r'):
        # Mode: The Python 'b' flag is ignored, since SSH treats all files as binary.
        sftp_path = self.sftp_path(name)
        return self.sftp(host).open(sftp_path, mode)

    def chown(self, host, path, uid=None, gid=None):
        # Paramiko's chown requires both uid and gid, so look them up first if
        # we're only supposed to set one.
        if uid is None or gid is None:
            attr = self.sftp(host).stat(path)
            uid = uid or attr.st_uid
            gid = gid or attr.st_gid
        self.sftp(host).chown(path, uid, gid)

    def delete(self, host, name):
        sftp_path = self.sftp_path(name)
        try:
            self.sftp(host).remove(sftp_path)
        except OSError:
            pass

