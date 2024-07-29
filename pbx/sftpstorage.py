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
from urllib.parse import urljoin
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.storage.mixins import StorageSettingsMixin
from django.utils._os import safe_join
from django.utils.deconstruct import deconstructible
from django.utils.encoding import filepath_to_uri
from django.utils.functional import cached_property
from pbx.sshconnect import SFTPConnection


@deconstructible
class SftpStorage(Storage, StorageSettingsMixin):
    filestores = []
    freeswitches = []

    def __init__(self, location=None, base_url=None, open_find=False):
        self._location = location
        self._base_url = base_url
        self.open_find = open_find
        self.err_count = 0
        self.sftp = SFTPConnection()
        self.filestores = settings.PBX_FILESTORES
        self.freeswitches = settings.PBX_FREESWITCHES
        self.current_filestore = settings.PBX_DEFAULT_FILESTORE

    @cached_property
    def base_location(self):
        return self._value_or_setting(self._location, settings.MEDIA_ROOT)

    @cached_property
    def location(self):
        return os.path.abspath(self.base_location)

    @cached_property
    def base_url(self):
        if self._base_url is not None and not self._base_url.endswith("/"):
            self._base_url += "/"
        return self._value_or_setting(self._base_url, settings.MEDIA_URL)

    # If True Follow all known SFTP connections to locate a file
    def set_open_find(self, open_find=False):
        self.open_find = open_find

    # Allow an SFTP location to have an additional path prefix
    def set_base_path(self, base_path=''):
        self.sftp.set_base_path(base_path)

    def set_current_filestore(self, host=0):
        self.current_filestore = host

    def _open(self, filename, mode='rb'):
        if settings.PBX_USE_LOCAL_FILE_STORAGE:
            raise FileNotFoundError('SftpStorage PBX_USE_LOCAL_FILE_STORAGE set to True')
            for s in self.freeswitches:
                if self.sftp.exists(s, filename):
                    return self.sftp.open(s, filename)
            for s in self.filestores:
                if self.sftp.exists(s, filename):
                    return self.sftp.open(s, filename)
            raise FileNotFoundError('FileAbsLayer open find failed to locate file')
        return self.sftp.open(self.filestores[self.current_filestore], self.path(filename))

    def _save(self, filename, content):
        self.sftp.save(self.filestores[self.current_filestore], self.path(filename), content)
        # Store filenames with forward slashes, even on Windows.
        return str(filename).replace("\\", "/")

    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")
        url = filepath_to_uri(name)
        if url is not None:
            url = url.lstrip("/")
        return urljoin(self.base_url, url)

    def exists(self, filename):
        return self.sftp.exists(self.filestores[self.current_filestore], self.path(filename))

    def delete(self, filename):
        if not filename:
            raise ValueError("The name must be given to delete().")
        return self.sftp.delete(self.filestores[self.current_filestore], self.path(filename))

    def path(self, filename):
        return safe_join(self.base_location, filename)

    def size(self, filename):
        return self.sftp.size(self.filestores[self.current_filestore], self.path(filename))
