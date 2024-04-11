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
from pbx.commonfunctions import str2regex


class InboundRoute():
    prefix                = ''                      # noqa: E221
    number                = '00000000'              # noqa: E221
    context               = 'djangopbx.com'         # noqa: E221
    application           = 'transfer'              # noqa: E221
    data                  = '201 XML djangopbx.com' # noqa: E221
    caller_id_name_prefix = ''                      # noqa: E221
    record                = 'false'                 # noqa: E221
    accountcode           = None                    # noqa: E221
    enabled               = 'true'                  # noqa: E221
    description           = ''                      # noqa: E221
    domain_id             = 'djangopbx.com'         # noqa: E221

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def generate_xml(self, dp):
        x_root = etree.Element('extension', name=dp.name)
        x_root.set('continue', dp.dp_continue)
        x_root.set('uuid', str(dp.id))
        x_condition = etree.SubElement(
            x_root, 'condition', field='destination_number',
            expression=str2regex(self.number, self.prefix)
            )
        etree.SubElement(x_condition, 'action', application='export', data='call_direction=inbound', inline='true')
        etree.SubElement(
            x_condition, 'action', application='set',
            data='domain_uuid=%s' % str(dp.domain_id_id), inline='true'
            )
        etree.SubElement(
            x_condition, 'action', application='set',
            data='domain_name=%s' % self.domain_id, inline='true'
            )
        etree.SubElement(x_condition, 'action', application='set', data='hangup_after_bridge=true')
        etree.SubElement(x_condition, 'action', application='set', data='continue_on_fail=true')
        if self.caller_id_name_prefix:
            etree.SubElement(
                x_condition, 'action', application='set',
                data='effective_caller_id_name=%s#${caller_id_name}' % self.caller_id_name_prefix
                )
        if self.record == 'true':
            etree.SubElement(
                x_condition, 'action', application='set',
                data='record_path=${recordings_dir}/${domain_name}/'
                'archive/${strftime(%Y)}/${strftime(%b)}/${strftime(%d)}',
                inline='true'
                )
            etree.SubElement(
                x_condition, 'action', application='set',
                data='record_name=${uuid}.${record_ext}', inline='true'
                )
            etree.SubElement(
                x_condition, 'action', application='set',
                data='record_append=true', inline='true'
                )
            etree.SubElement(
                x_condition, 'action', application='set',
                data='record_in_progress=true', inline='true'
                )
            etree.SubElement(
                x_condition, 'action', application='set',
                data='recording_follow_transfer=true', inline='true'
                )
            etree.SubElement(
                x_condition, 'action', application='record_session',
                data='${record_path}/${record_name}'
                )
        if self.accountcode:
            etree.SubElement(x_condition, 'action', application='set', data='accountcode=%s' % self.accountcode)

        etree.SubElement(x_condition, 'action', application=self.application, data=self.data)
        etree.indent(x_root)
        return str(etree.tostring(x_root), "utf-8").replace('&lt;', '<')
