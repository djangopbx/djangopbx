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

from accounts.models import Extension, FollowMeDestination
from switch.models import SwitchVariable


class ExtFunctions():

    def __init__(self, domain_uuid, domain_name, call_direction='local', extension_uuid=None):
        self.domain_uuid = domain_uuid
        self.domain_name = domain_name
        self.call_direction = call_direction
        self.extension_uuid = extension_uuid
        self.ext_dict = {}
        exts = Extension.objects.filter(domain_id=self.domain_uuid, enabled='true')
        for ext in exts:
            self.ext_dict[ext.extension] = (str(ext.id), ext.follow_me_enabled)

        if extension_uuid:
            try:
                self.ext = Extension.objects.get(pk=extension_uuid)
            except:
                self.ext = False
        else:
            self.ext = False

    def generate_bridge(self):
        if not self.ext:
            return False

        bridge_list = []
        var_list = []
        efmds = FollowMeDestination.objects.filter(extension_id=self.ext.id).order_by('sequence')
        for efmd in efmds:
            if not efmd.destination in self.ext_dict:
                var_list.append('ignore_early_media=true')
                var_list.append('toll_allow=%s' % (self.ext.forward_toll_allow if self.ext.toll_allow else ''))
                if self.call_direction == 'inbound':
                    var_list.append('origination_caller_id_name=${caller_id_name}')
                    var_list.append('origination_caller_id_number=${caller_id_number}')
                else:
                    var_list.append('origination_caller_id_name=%s' % self.ext.outbound_caller_id_name)
                    var_list.append('origination_caller_id_number=%s' % self.ext.outbound_caller_id_number)
            else:
                var_list.append('dialed_extension=%s' % efmd.destination)
                var_list.append('extension_uuid=%s' % self.ext_dict[efmd.destination][0])
            var_list.append('sip_invite_domain=%s' % self.domain_name)
            if efmd.prompt == '1':
                var_list.append('confirm=true')
                var_list.append('group_confirm_file=ivr/ivr-accept_reject.wav')
                var_list.append('group_confirm_key=1')
            else:
                var_list.append('confirm=false')
            var_list.append('leg_timeout=%s' % str(efmd.timeout))
            var_list.append('leg_delay_start=%s' % str(efmd.delay))
            if efmd.destination in self.ext_dict:
                bridge_list.append('[%s]%s' % (','.join(var_list), 'user/%s@%s' % (efmd.destination, self.domain_name)))
            else:
                bridge_list.append('[%s]%s' % (','.join(var_list), 'loopback/%s' % (efmd.destination)))
            var_list = []
        return '<ignore_early_media=true>%s' % ','.join(bridge_list)
