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
from io import StringIO


class TimeCondition():
    domain_id             = 'djangopbx.com'                                      # noqa: E221
    name                  = ''                                                   # noqa: E221
    number                = '00000000'                                           # noqa: E221
    context               = 'djangopbx.com'                                      # noqa: E221
    settings              = ''                                                   # noqa: E221
    alternate_destination = '201'                                                # noqa: E221
    sequence              = 301                                                  # noqa: E221
    enabled               = 'true'                                               # noqa: E221
    description           = ''                                                   # noqa: E221

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def generate_xml(self, dp):
        x_root = etree.Element('extension', name=dp.name)
        x_root.set('continue', dp.dp_continue)
        x_root.set('uuid', str(dp.id))
        parser = etree.XMLParser(remove_comments=True)
        tree = etree.parse(StringIO(self.settings), parser)
        settings = tree.getroot()
        tree = etree.parse(StringIO(self.alternate_destination), parser)
        alternate_destination = tree.getroot()
        for settingchild in settings:
            x_root.append(settingchild)
        x_root.append(alternate_destination)
        etree.indent(x_root)
        return str(etree.tostring(x_root), "utf-8").replace('&lt;', '<')
