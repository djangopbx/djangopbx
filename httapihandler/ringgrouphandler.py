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

from lxml import etree
from .httapihandler import HttApiHandler
from ringgroups.ringgroupfunctions import RgFunctions, get_ringgroup


class RingGroupHandler(HttApiHandler):

    handler_name = 'ringgroup'

    def get_variables(self):
        self.var_list = ['ring_group_uuid']
        self.var_list.extend(self.domain_var_list)

    def get_data(self):
        if self.exiting:
            return self.return_data('Ok\n')

        self.get_domain_variables()
        ringgroup_uuid = self.qdict.get('ring_group_uuid')
        rg = get_ringgroup(ringgroup_uuid)
        if not rg:
            return self.return_data(self.error_hangup('R1001'))
        try:
            rgf = RgFunctions(self.domain_uuid, self.domain_name, rg)
        except:
            return self.return_data(self.error_hangup('R1002'))

        x_root = self.XrootApi()
        etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')
        etree.SubElement(x_work, 'execute', application='bridge', data=rgf.generate_bridge())
        toa = rgf.generate_timeout_action()
        if toa[0] == 'hangup':
            etree.SubElement(x_work, toa[0])
        else:
            etree.SubElement(x_work, 'execute', application=toa[0], data=toa[1])

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml
