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

from lxml import etree
from .httapihandler import HttApiHandler
from accounts.models import Extension
from accounts.extensionfunctions import ExtFeatureSyncFunctions


class DndHandler(HttApiHandler):

    handler_name = 'donotdisturb'

    def get_variables(self):
        self.var_list = [
        'extension_uuid'
        ]

    def get_data(self):
        if self.exiting:
            return self.return_data('Ok\n')

        if not self.hraction:
            self.error_hangup('DND: action not specified')
        extension_uuid = self.qdict.get('extension_uuid')
        if extension_uuid:
            self.error_hangup('DND: extension uuid not specified')

        try:
            e = Extension.objects.get(pk=extension_uuid)
        except:
            e = None
        if not e:
            self.error_hangup('DND: extension not found')

        x_root = self.XrootApi()
        etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')
        etree.SubElement(x_work, 'execute', application='answer', data='')

        if self.hraction == 'toggle':
            self.hraction = ('false' if e.do_not_disturb == 'true' else 'true')

        if self.hraction == 'true':
            e.do_not_disturb = self.hraction
            e.follow_me_enabled = 'false'
            etree.SubElement(x_work, 'playback', file='ivr/ivr-dnd_activated.wav')

        if self.hraction == 'false':
            e.do_not_disturb = self.hraction
            etree.SubElement(x_work, 'playback', file='ivr/ivr-dnd_cancelled.wav')
        e.save()
        efsf = ExtFeatureSyncFunctions(extension_uuid, DoNotDisturbOn=e.do_not_disturb)
        efsf.clear_extension_cache()
        efsf.sync_dnd()
        efsf.es_disconnect()
        etree.SubElement(x_work, 'pause', milliseconds='1000')
        etree.SubElement(x_work, 'hangup')
        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml
