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

from django.core.cache import cache
from lxml import etree
from .httapihandler import HttApiHandler
from accounts.models import Extension


class FollowMeToggleHandler(HttApiHandler):

    handler_name = 'followmetoggle'

    def get_data(self):
        if self.exiting:
            return self.return_data('Ok\n')

        extension_uuid = self.session_json.get('variable_extension_uuid')
        try:
            e = Extension.objects.get(pk=extension_uuid)
        except Extension.DoesNotExist:
            self.logger.debug(self.log_header.format('follow me toggle', 'Extn UUID not found'))
            return self.return_data(self.error_hangup('E1001'))

        x_root = self.XrootApi()
        etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')
        etree.SubElement(x_work, 'execute', application='sleep', data='2000')
        if e.follow_me_enabled == 'true':
            etree.SubElement(
                x_work, 'playback',
                file='ivr/ivr-call_forwarding_has_been_cancelled.wav'
                )
            e.follow_me_enabled = 'false'
        else:
            etree.SubElement(
                x_work, 'playback',
                file='ivr/ivr-call_forwarding_has_been_set.wav'
                )
            e.follow_me_enabled = 'true'

        e.save()
        directory_cache_key = 'directory:%s@%s' % (e.extension, self.domain_name)
        cache.delete(directory_cache_key)
        etree.SubElement(x_work, 'hangup')
        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml
