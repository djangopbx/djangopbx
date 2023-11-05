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

import uuid
from django.utils.translation import gettext_lazy as _
from lxml import etree
from dialplans.models import Dialplan
from tenants.models import Domain
from accounts.models import Extension, FollowMeDestination
from .models import RingGroup, RingGroupDestination
from switch.models import SwitchVariable


class RgDestAction():

    def __init__(self, domain_name, domain_uuid):
        self.domain_uuid = domain_uuid
        self.domain_name = domain_name


    def get_rg_action_choices(self):
        rg_actions = []
        e_list = []
        v_list = []
        es = Extension.objects.select_related('domain_id').prefetch_related('voicemail').filter(
                domain_id=uuid.UUID(self.domain_uuid),
                enabled='true'
                ).order_by('extension')
        for e in es:
            e_list.append(('transfer:%s XML %s' % (e.extension, e.domain_id), '%s %s' % (e.extension, e.description)))
            v = e.voicemail.filter(enabled='true').first()
            if v:
                v_list.append(
                    ('transfer:99%s XML %s' % (e.extension, e.domain_id), '%s(VM) %s' % (e.extension, e.description))
                    )

        if len(e_list) > 0:
            rg_actions.append((_('Extensions'), e_list))
        if len(v_list) > 0:
            rg_actions.append((_('Voicemails'), v_list))

        rg_list = []
        rgs = Dialplan.objects.filter(domain_id=uuid.UUID(self.domain_uuid),
                category='Ring group',
                enabled='true'
                ).order_by('name')
        for rg in rgs:
            rg_list.append(('transfer:%s XML %s' % (rg.number, self.domain_name), '%s-%s' % (rg.name, rg.number)))

        if len(rg_list) > 0:
            rg_actions.append((_('Ring groups'), rg_list))

        t_list = []
        sv = SwitchVariable.objects.filter(category='Tones', enabled='true').order_by('name')
        for t in sv:
            t_list.append(('playback:tone_stream://%s' % t.value, t.name))

        if len(t_list) > 0:
            rg_actions.append((_('Tones'), t_list))

        o_list = []
        o_list.append(('transfer:98 XML %s' % self.domain_name, _('Check Voicemail')))
        o_list.append(('transfer:411 XML %s' % self.domain_name, _('Company Directory')))
        o_list.append(('transfer:732 XML %s' % self.domain_name, _('Record')))
        o_list.append(('hangup', _('Hangup')))
        rg_actions.append((_('Other'), o_list))

        return rg_actions


class RgFunctions():

    def __init__(self, domain_uuid, domain_name, ringgroup_uuid=None, user_name='system'):
        self.domain_uuid = domain_uuid
        self.domain_name = domain_name
        self.user_name = user_name
        self.ringgroup_uuid = ringgroup_uuid
        self.ext_dict = {}
        exts = Extension.objects.filter(domain_id=self.domain_uuid, enabled='true')
        for ext in exts:
            self.ext_dict[ext.extension] = (str(ext.id), ext.follow_me_enabled)

        self.rg = RingGroup.objects.get(pk=ringgroup_uuid)

        if ringgroup_uuid:
            try:
                self.rg = RingGroup.objects.get(pk=ringgroup_uuid)
            except:
                self.rg = False
        else:
            self.rg = False

    def add_dialplan(self):
        d = Domain.objects.get(pk=self.domain_uuid)

        dp = Dialplan.objects.create(
            domain_id=d,
            app_id='77578687-8eb7-4bb7-a00a-ddf3e8b7169f',
            name=self.rg.name,
            number=self.rg.extension,
            destination='true',
            context=self.domain_name,
            category='Ring group',
            dp_continue='false',
            sequence=101,
            enabled=self.rg.enabled,
            description=self.rg.description,
            updated_by=self.user_name
        )
        return dp

    def generate_xml(self):
        if not self.rg:
            return None
        try:
            dp = Dialplan.objects.get(pk=self.rg.dialplan_id)
        except:
            dp = self.add_dialplan()

        dp.enabled = self.rg.enabled
        dp.name = self.rg.name
        dp.number=self.rg.extension

        x_root = etree.Element("extension", name=dp.name)
        x_root.set('continue', dp.dp_continue)
        x_root.set('uuid', str(dp.id))

        # Group 0
        x_condition = etree.SubElement(x_root, "condition", field='destination_number', expression='^%s$' % self.rg.extension)
        x_condition = etree.SubElement(x_root, "condition", field='${call_direction}', expression='^inbound$',)
        x_condition.set('break', 'never')

        if self.rg.caller_id_name:
            etree.SubElement(x_condition, "action", application='set', data='rg_ob_caller_id_name=%s' % self.rg.caller_id_name)
        else:
            etree.SubElement(x_condition, "action", application='set', data='rg_ob_caller_id_name=${caller_id_name}')

        if self.rg.caller_id_number:
            etree.SubElement(x_condition, "action", application='set', data='rg_ob_caller_id_number=%s' % self.rg.caller_id_number)
        else:
            etree.SubElement(x_condition, "action", application='set', data='rg_ob_caller_id_number=${caller_id_number}')

        if self.rg.caller_id_name:
            etree.SubElement(x_condition, "anti-action", application='set', data='rg_ob_caller_id_name=%s' % self.rg.caller_id_name)
        else:
            etree.SubElement(x_condition, "anti-action", application='set', data='rg_ob_caller_id_name=${outbound_caller_id_name}')
        if self.rg.caller_id_number:
            etree.SubElement(x_condition, "anti-action", application='set', data='rg_ob_caller_id_number=%s' % self.rg.caller_id_number)
        else:
            etree.SubElement(x_condition, "anti-action", application='set', data='rg_ob_caller_id_number=${outbound_caller_id_number}')


        # Group 1
        x_condition = etree.SubElement(x_root, "condition", field='destination_number', expression='^%s$' % self.rg.extension)
        etree.SubElement(x_condition, "action", application='set', data='ring_group_uuid=%s' % str(self.rg.id), inline='true')
        etree.SubElement(x_condition, "action", application='set', data='ring_back=%s' % self.rg.ring_group_ringback)
        etree.SubElement(x_condition, "action", application='set', data='hangup_after_bridge=true')
        if self.rg.missed_call_app:
            etree.SubElement(x_condition, "action", application='set', data='missed_call_app=%s' % self.rg.missed_call_app)
            etree.SubElement(x_condition, "action", application='set', data='missed_call_data=%s' % self.rg.missed_call_data)
            etree.SubElement(x_condition, "action", application='set', data='api_hangup_hook=lua eh_hangup.lua')

        if self.rg.distinctive_ring:
            etree.SubElement(x_condition, "action", application='export', data='sip_h_Alert-Info=%s' % self.rg.distinctive_ring)
        if self.rg.cid_name_prefix:
            etree.SubElement(x_condition, "action", application='set', data='effective_caller_id_name=%s${caller_id_name}' % self.rg.cid_name_prefix)
        if self.rg.cid_number_prefix:
            etree.SubElement(x_condition, "action", application='set', data='effective_caller_id_number=%s${caller_id_number}' % self.rg.cid_number_prefix)

        if self.rg.forward_enabled == 'true':
            etree.SubElement(x_condition, "action", application='set', data='ring_group_uuid=%s' % str(self.rg.id))
            if self.rg.forward_destination in self.ext_dict:
                etree.SubElement(x_condition, "action", application='set', data='dialed_extension=%s' % self.rg.forward_destination)
                etree.SubElement(x_condition, "action", application='set', data='extension_uuid=%s' % self.ext_dict[self.rg.forward_destination][0])
                etree.SubElement(x_condition, "action", application='bridge', data='user/%s' % self.rg.forward_destination)
            else:
                etree.SubElement(x_condition, "action", application='set', data='toll_allow=%s' % self.rg.forward_toll_allow)
                etree.SubElement(x_condition, "action", application='set', data='origination_caller_id_name=${rg_ob_caller_id_name}')
                etree.SubElement(x_condition, "action", application='set', data='origination_caller_id_number=${rg_ob_caller_id_number}')
                etree.SubElement(x_condition, "action", application='bridge', data='loopback/%s' % self.rg.forward_destination)
        else:
            etree.SubElement(x_condition, "action", application='set', data='call_timeout=%s' % self.rg.call_timeout)
            etree.SubElement(x_condition, "action", application='set', data='continue_on_fail=true')
            etree.SubElement(x_condition, "action", application='ring_ready', data='')
            if len(self.rg.greeting) > 4:
                etree.SubElement(x_condition, "action", application='playback', data=self.rg.greeting)

            if self.rg.follow_me_enabled == 'true':
                etree.SubElement(x_condition, "action", application='httapi', data='{httapi_profile=full,url=http://127.0.0.1:8080/httapihandler/ringgroup/}')
            else:
                etree.SubElement(x_condition, "action", application='bridge', data=self.generate_bridge())
                app_data_list = self.rg.timeout_data.split(':')
                etree.SubElement(x_condition, "action", application=app_data_list[0], data=app_data_list[1])

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8").replace('&lt;', '<').replace('&gt;', '>')
        dp.xml = xml
        dp.save()
        return dp.id

    def generate_bridge(self):
        if not self.rg:
            return False
        sep = '|'
        if self.rg.strategy == 'simultaneous':
            sep = ','
        elif self.rg.strategy == 'enterprise':
            sep = '_'

        bridge_list = []
        var_list = []
        rgds = RingGroupDestination.objects.filter(ring_group_id=self.rg.id)
        for rgd in rgds:
            if not rgd.number in self.ext_dict:
                var_list.append('toll_allow=%s' % (self.rg.forward_toll_allow if self.rg.forward_toll_allow else ''))
                var_list.append('origination_caller_id_name=${rg_ob_caller_id_name}')
                var_list.append('origination_caller_id_number=${rg_ob_caller_id_number}')
            else:
                var_list.append('dialed_extension=%s' % rgd.number)
                var_list.append('extension_uuid=%s' % self.ext_dict[rgd.number][0])
            var_list.append('sip_invite_domain=%s' % self.domain_name)
            if rgd.destination_prompt==0:
                var_list.append('confirm=false')
            else:
                var_list.append('confirm=true')
                var_list.append('group_confirm_file=ivr/ivr-accept_reject.wav')
                var_list.append('group_confirm_key=1')
            var_list.append('leg_timeout=%s' % str(rgd.timeout))
            var_list.append('leg_delay_start=%s' % str(rgd.delay))

            if rgd.number in self.ext_dict:
                if self.rg.follow_me_enabled == 'true' and self.ext_dict[rgd.number][1] == 'true':
                    var_list = []
                    efmds = FollowMeDestination.objects.filter(
                                extension_id=self.ext_dict[rgd.number][0]).order_by('sequence')
                    for efmd in efmds:
                        if not efmd.destination in self.ext_dict:
                            var_list.append('ignore_early_media=true')
                            var_list.append('toll_allow=%s' % (self.rg.forward_toll_allow if self.rg.forward_toll_allow else ''))
                            var_list.append('origination_caller_id_name=${rg_ob_caller_id_name}')
                            var_list.append('origination_caller_id_number=${rg_ob_caller_id_number}')
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

                else:
                    bridge_list.append('[%s]%s' % (','.join(var_list), 'user/%s@%s' % (rgd.number, self.domain_name)))
            else:
                bridge_list.append('[%s]%s' % (','.join(var_list), 'loopback/%s' % (rgd.number)))
            var_list = []

        return '<ignore_early_media=true>%s' % sep.join(bridge_list)

    def generate_timeout_action(self):
        return self.rg.timeout_data.split(':')
