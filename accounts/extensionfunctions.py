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

import math
from django.core.cache import cache
from accounts.models import Extension, FollowMeDestination
from switch.models import SwitchVariable
from django.conf import settings
from pbx.fscmdabslayer import FsCmdAbsLayer
from tenants.pbxsettings import PbxSettings
from pbx.devicecfgevent import DeviceCfgEvent


class ExtFeatureSyncFunctions():
    vendor = 'none'
    feature_sync = False

    def __init__(self, obj=None, **kwargs):
        self.__dict__.update(kwargs)
        self.es_connected = False
        pbxs = PbxSettings()
        if not self.get_extension_object(obj):
            return
        self.ext_user = self.ext.extensionuser.filter(default_user='true').first()
        self.vendor_sync_status = pbxs.feature_sync_vendor_settings(self.ext_user, self.ext.domain_id)
        if not self.vendor_sync_status.get('_any_set', False):
            return
        self.sip_user = '%s@%s' % (self.ext.extension, self.ext.user_context)
        self.es = FsCmdAbsLayer()
        if not self.es.connect():
            return
        self.es_connected = True
        if not self.get_sofia_contact():
            return
        self.es.clear_responses()
        sspu_detail = self.es.send('api sofia status profile %s user %s' % (self.sip_profile, self.sip_user))
        self.es.process_events()
        self.es.get_responses()
        user_found = False
        for resp in self.es.responses:
            if self.parse_sofia_status_profile_user(resp):
                user_found = True
        if not user_found:
            return
        agent = self.user_info.get('Agent', 'none').lower()
        for v, s in self.vendor_sync_status.items():
            if v in agent:
                self.vendor = v
        self.feature_sync = self.vendor_sync_status.get(self.vendor, False)
        self.init_ok = True

    def es_disconnect(self):
        if self.es_connected:
            self.es.disconnect()

    def get_sofia_contact(self):
        if not self.es_connected:
            return False
        ret = False
        self.es.clear_responses()
        self.es.send('api sofia_contact */%s' % self.sip_user)
        self.es.process_events()
        self.es.get_responses()
        for resp in self.es.responses:
            if resp.endswith('user_not_registered'):
                continue
            try:
                self.sip_profile = resp.split('/')[1]
            except:
                self.sip_profile = 'none'
                continue
            self.contact = resp
            ret = True
        return ret

    def clear_extension_cache(self):
        directory_cache_key = 'directory:%s@%s' % (self.ext.extension, self.ext.user_context)
        cache.delete(directory_cache_key)

    def get_extension_object(self, obj):
        if isinstance(obj, Extension):
            self.ext = obj
            return True
        elif isinstance(obj, str):
            try:
                self.ext = Extension.objects.get(pk=obj)
            except:
                return False
            return True
        else:
            return False

    def parse_sofia_status_profile_user(self, sspu_detail):
        lines = sspu_detail.splitlines()
        i = 1
        self.user_info = {}
        for line in lines:
            if i > 3 and i < 17:
                if ':' in line:
                    data = line.split(':', 1)
                    self.user_info[data[0]] = data[1].strip()
            i += 1
        if i < 17:
            return False
        return True

    def sync_dnd(self):
        if not self.es_connected:
            return
        if not self.feature_sync:
            return
        dce = DeviceCfgEvent()
        cmd = dce.buildfeatureevent(self.ext.extension, self.ext.user_context, self.sip_profile, 'DoNotDisturbEvent', DoNotDisturbOn=self.ext.do_not_disturb)
        self.es.clear_responses()
        self.es.send(cmd)
        self.es.process_events()
        self.es.get_responses()

    def sync_fwd_immediate(self):
        if not self.es_connected:
            return
        if not self.feature_sync:
            return
        dce = DeviceCfgEvent()
        cmd = dce.buildfeatureevent(self.ext.extension, self.ext.user_context, self.sip_profile, 'ForwardingEvent',
                forward_immediate_enabled=self.ext.forward_all_enabled,
                forward_immediate=(self.ext.forward_all_destination if self.ext.forward_all_destination else '0')
                )
        self.es.clear_responses()
        self.es.send(cmd)
        self.es.process_events()
        self.es.get_responses()

    def sync_fwd_busy(self):
        if not self.es_connected:
            return
        if not self.feature_sync:
            return
        dce = DeviceCfgEvent()
        cmd = dce.buildfeatureevent(self.ext.extension, self.ext.user_context, self.sip_profile, 'ForwardingEvent',
                forward_busy_enabled=self.ext.forward_busy_enabled,
                forward_busy=(self.ext.forward_busy_destination if self.ext.forward_busy_destination else '0')
                )
        self.es.clear_responses()
        self.es.send(cmd)
        self.es.process_events()
        self.es.get_responses()

    def sync_fwd_no_answer(self):
        if not self.es_connected:
            return
        if not self.feature_sync:
            return
        dce = DeviceCfgEvent()
        cmd = dce.buildfeatureevent(self.ext.extension, self.ext.user_context, self.sip_profile, 'ForwardingEvent',
                forward_no_answer_enabled=self.ext.forward_no_answer_enabled,
                forward_no_answer=(self.ext.forward_no_answer_destination if self.ext.forward_no_answer_destination else '0'),
                ringCount=math.ceil(self.ext.call_timeout / 6)
                )
        self.es.clear_responses()
        self.es.send(cmd)
        self.es.process_events()
        self.es.get_responses()

    def sync_all(self):
        # Warning, if you predominantly use UDP, using this function will almost certainly exceed your MTU.
        if not self.es_connected:
            return
        if not self.feature_sync:
            return
        dce = DeviceCfgEvent()
        cmd = dce.buildfeatureevent(self.ext.extension, self.ext.user_context, self.sip_profile, 'init',
                forward_immediate_enabled=self.ext.forward_all_enabled,
                forward_immediate=(self.ext.forward_all_destination if self.ext.forward_all_destination else '0'),
                forward_busy_enabled=self.ext.forward_busy_enabled,
                forward_busy=(self.ext.forward_busy_destination if self.ext.forward_busy_destination else '0'),
                forward_no_answer_enabled=self.ext.forward_no_answer_enabled,
                forward_no_answer=(self.ext.forward_no_answer_destination if self.ext.forward_no_answer_destination else '0'),
                ringCount=math.ceil(self.ext.call_timeout / 6),
                DoNotDisturbOn=self.ext.do_not_disturb
            )
        print(cmd)
        self.es.clear_responses()
        self.es.send(cmd)
        self.es.process_events()
        self.es.get_responses()


class ExtFollowMeFunctions():

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
