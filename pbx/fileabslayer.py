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
import socket
from django.conf import settings
from pbx.sshconnect import SFTPConnection


class FileAbsLayer:

    loc_files = False
    filestores = []
    freeswitches = []

    def __init__(self, debug=False, open_find=False):
        self.debug = debug
        self.open_find = open_find
        self.err_count = 0
        self.sftp = SFTPConnection()
        try:
            self.hostname = socket.gethostname()
        except:
            self.hostname = 'localhost'
        self.loc_files = settings.PBX_USE_LOCAL_FILE_STORAGE
        self.loc_freeswich = settings.PBX_FREESWITCH_LOCAL
        self.filestores = settings.PBX_FILESTORES
        self.freeswitches = settings.PBX_FREESWITCHES

    # If True Follow all known SFTP connections to locate a file
    def set_open_find(self, open_find=False):
        self.open_find = open_find

    # Allow an SFTP location to have an additional path prefix
    def set_base_path(self, base_path='', host=None):
        if not self.use_local(host):
            self.sftp.set_base_path(base_path)

    def check_host(self, host=None):
        return (host if host else self.hostname)

    def exists(self, filename, host=None):
        if self.use_local(host):
            return os.path.exists(filename)
        return self.sftp.exists(self.check_host(host), filename)

    def open(self, filename, mode='rb', host=None):
        if self.use_local(host):
            return open(filename, mode)
        if self.open_find:
            for s in self.freeswitches:
                if self.sftp.exists(s, filename):
                    return self.sftp.open(s, filename)
            for s in self.filestores:
                if self.sftp.exists(s, filename):
                    return self.sftp.open(s, filename)
            raise FileNotFoundError('FileAbsLayer open find failed to locate file')
        return self.sftp.open(self.check_host(host), filename)

    def save_to_freeswitches(self, localfile, remotefile):
        for sw in self.freeswitches:
            self.sftp.put(sw, localfile, remotefile)

    def use_local(self, host=None):
        if host in self.freeswitches and not self.loc_freeswich:
            return True
        return self.loc_files

    def listdir(self, path, host=None):
        dirs = []
        files = []
        if self.use_local(host):
            with os.scandir(path) as it:
                for f in it:
                    if f.is_dir():
                        dirs.append(f.name)
                    else:
                        files.append(f.name)
            return (dirs, files)
        return self.sftp.listdir(host, path)
