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

import os
from .models import MusicOnHold
from tenants.pbxsettings import PbxSettings
from lxml import etree


class MohSource():
    def choices(self, prefix='local_stream://'):
        return [('%s%s' % (prefix, c.name), c.name) for c in MusicOnHold.objects.distinct('name')]

class MohFunctions():
    def write_local_stream_xml(self):
        mlist = MusicOnHold.objects.all().order_by('name', 'rate')
        xml = ''

        conflist = PbxSettings().default_settings('switch', 'conf', 'dir')
        if conflist:
            confdir = conflist[0]

            root = etree.Element('configuration', name='local_stream.conf', description='stream files from local dir')

            for m in mlist:
                mdir = etree.SubElement(root, 'directory', name='moh/%s' % m.rate, path=m.path)
                param = etree.SubElement(mdir, 'param', name='rate', value=str(m.rate))
                param = etree.SubElement(mdir, 'param', name='shuffle', value=m.shuffle)
                param = etree.SubElement(mdir, 'param', name='channels', value=str(m.channels))
                param = etree.SubElement(mdir, 'param', name='interval', value=str(m.interval))
                param = etree.SubElement(mdir, 'param', name='timer-name', value=m.timer_name)

            etree.indent(root)
            xml =  str(etree.tostring(root), "utf-8")

            try:
                os.makedirs('%s/autoload_configs' % confdir, mode=0o755, exist_ok = True)
            except OSError:
                return 2

            try:
                with open('%s/autoload_configs/local_stream.conf.xml' % confdir, 'w') as f:
                    f.write(xml)
            except OSError:
                return 3

            return 0
        else:
            return 1

