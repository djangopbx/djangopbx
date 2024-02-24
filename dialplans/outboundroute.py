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
from accounts.accountfunctions import AccountFunctions


class OutboundRoute():
    domain_id    = None            # noqa: E221
    name         = ''              # noqa: E221
    gateway_1    = ''              # noqa: E221
    gateway_2    = None            # noqa: E221
    gateway_3    = None            # noqa: E221
    number       = '00000000'      # noqa: E221
    prefix       = ''              # noqa: E221
    limit        = 0               # noqa: E221
    account_code = None            # noqa: E221
    toll_allow   = ''              # noqa: E221
    pin_numbers  = 'false'         # noqa: E221
    sequence     = 101             # noqa: E221
    enabled      = 'true'          # noqa: E221
    description  = ''              # noqa: E221

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def generate_xml(self, dp):
        gateway1_bridge_data = False
        gateway2_bridge_data = False
        gateway3_bridge_data = False
        af = AccountFunctions()

        if self.gateway_1:
            gateway1_type = af.gateway_type(self.gateway_1)
            gateway1_bridge_data = af.gateway_bridge_data(self.gateway_1, gateway1_type, self.prefix)
        if self.gateway_2:
            gateway2_type = af.gateway_type(self.gateway_2)
            gateway2_bridge_data = af.gateway_bridge_data(self.gateway_2, gateway2_type, self.prefix)
        else:
            gateway2_type = 'N/A'

        if self.gateway_3:
            gateway3_type = af.gateway_type(self.gateway_3)
            gateway3_bridge_data = af.gateway_bridge_data(self.gateway_3, gateway3_type, self.prefix)

        x_root = etree.Element('extension', name=dp.name)
        x_root.set('continue', dp.dp_continue)
        x_root.set('uuid', str(dp.id))
        etree.SubElement(x_root, 'condition', field='${user_exists}', expression='false')
        if self.toll_allow:
            etree.SubElement(x_root, 'condition', field='${toll_allow}', expression='^%s$' % self.toll_allow)
        x_condition = etree.SubElement(x_root, 'condition', field='destination_number', expression=self.number)
        etree.SubElement(
            x_condition, 'action', application='export',
            data='call_direction=outbound', inline='true'
            )
        etree.SubElement(x_condition, 'action', application='unset', data='call_timeout')
        if gateway1_type == 'transfer':
            dialplan_detail_type = 'transfer'
        else:
            dialplan_detail_type = 'bridge'
            if self.account_code:
                etree.SubElement(
                    x_condition, 'action', application='set',
                    data='sip_h_X-accountcode=%s' % self.account_code
                    )
            else:
                etree.SubElement(
                    x_condition, 'action', application='set',
                    data='sip_h_X-accountcode=${accountcode}'
                    )

            etree.SubElement(x_condition, 'action', application='set', data='hangup_after_bridge=true')
            if self.number == '(^911$|^933$)' or self.number == '(^999$|^112$)':
                etree.SubElement(
                    x_condition, 'action', application='set',
                    data='effective_caller_id_name=${emergency_caller_id_name}'
                    )
                etree.SubElement(
                    x_condition, 'action', application='set',
                    data='effective_caller_id_number=${emergency_caller_id_number}'
                    )
            else:
                etree.SubElement(
                    x_condition, 'action', application='set',
                    data='effective_caller_id_name=${outbound_caller_id_name}'
                    )
                etree.SubElement(
                    x_condition, 'action', application='set',
                    data='effective_caller_id_number=${outbound_caller_id_number}'
                    )

            etree.SubElement(x_condition, 'action', application='set', data='inherit_codec=true')
            etree.SubElement(x_condition, 'action', application='set', data='ignore_display_updates=true')
            etree.SubElement(x_condition, 'action', application='set', data='callee_id_number=$1')
            etree.SubElement(x_condition, 'action', application='set', data='continue_on_fail=true')

        if gateway1_type == 'enum' or gateway2_type == 'enum':
            etree.SubElement(x_condition, 'action', application='enum', data='%s$1 e164.org' % self.prefix)

        if self.limit > 0:
            etree.SubElement(
                x_condition, 'action', application='limit',
                data='hash ${domain_name} outbound %s !USER_BUSY' % self.limit
                )
        if self.prefix:
            etree.SubElement(x_condition, 'action', application='set', data='outbound_prefix=%s' % self.prefix)
        if self.pin_numbers == 'true':
            etree.SubElement(x_condition, 'action', application='set', data='pin_number=database')
            etree.SubElement(x_condition, 'action', application='python', data='pin_number')
        etree.SubElement(x_condition, 'action', application='sleep', data='${sleep}')

        if gateway1_bridge_data:
            etree.SubElement(x_condition, 'action', application=dialplan_detail_type, data=gateway1_bridge_data)

        if gateway2_bridge_data:
            etree.SubElement(x_condition, 'action', application='bridge', data=gateway2_bridge_data)

        if gateway3_bridge_data:
            etree.SubElement(x_condition, 'action', application='bridge', data=gateway3_bridge_data)

        etree.indent(x_root)
        return str(etree.tostring(x_root), "utf-8").replace('&lt;', '<')
