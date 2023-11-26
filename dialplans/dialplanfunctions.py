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
import uuid
import re
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.conf import settings
from django.db.models import Case, Value, When, Max
from django.contrib.auth.base_user import BaseUserManager
from django.db.models import Q
from lxml import etree
from io import StringIO
import dialplans.models
from tenants.models import Domain
from tenants.pbxsettings import PbxSettings
from accounts.models import Extension
from switch.models import SwitchVariable
from pbx.commonvalidators import valid_uuid4

class DpFunctions():

    def string_to_regex(string, prefix=''):
        # add prefix
        if len(prefix) > 0:
            if len(prefix) > 0 and len(prefix) < 4:
                if string[0] == "+":
                    prefix = prefix + "?"
                else:
                    prefix = "\\+?" + prefix + "?"
            else:
                prefix = "(?:" + prefix + ")?"

        # escape the plus
        if string[0] == "+":
            string = "^\\+(" + string[1:] + ")$"

        # convert N,X,Z syntax to regex
        string.replace("N", "[2-9]")
        string.replace("X", "[0-9]")
        string.replace("Z", "[1-9]")

        # add ^ to the start of the string if missing
        if string[0] != "^":
            string = "^" + string

        # add $ to the end of the string if missing
        if string[-1] != "$":
            string = string + "$"

        # add the round brackets
        if string.find('(') == -1:
            if string.find('^') > -1:
                string.replace("^", "^" + prefix + "(")
            else:
                string = "^(" + string
            if string.find('$') > -1:
                string.replace("$", ")$")
            else:
                string = string + ")$"

        # return the result
        return string


class SwitchDp():
     #optgroups dont currently work with datalist in the browser - html looks fine, just doesn't display the options
#    tag_type_choices = [('cmd/Rxp',[
#            ('context', 'Context'),
#            ('username', 'Username'),
#        ]),
#            ('fred',[('hello', 'hello')])
#        ]

    tag_type_choices = [
        ('--- Condition or Regex -------', [
        ('context', 'Context'),
        ('username', 'Username'),
        ('rdnis', 'RDNIS'),
        ('destination_number', 'Destination Number'),
        ('dialplan', 'Dialplan'),
        ('caller_id_name', 'Caller ID Name'),
        ('caller_id_number', 'Caller ID Number'),
        ('ani', 'ANI'),
        ('ani2', 'ANI2'),
        ('uuid', 'UUID'),
        ('source', 'Source'),
        ('chan_name', 'Channel Name'),
        ('network_addr', 'Network Address'),
        ('${number_alias}', '${number_alias}'),
        ('${sip_from_uri}', '${sip_from_uri}'),
        ('${sip_from_user}', '${sip_from_user}'),
        ('${sip_from_host}', '${sip_from_host}'),
        ('${sip_contact_uri}', '${sip_contact_uri}'),
        ('${sip_contact_user}', '${sip_contact_user}'),
        ('${sip_contact_host}', '${sip_contact_host}'),
        ('${sip_to_uri}', '${sip_to_uri}'),
        ('${sip_to_user}', '${sip_to_user}'),
        ('${sip_to_host}', '${sip_to_host}'),
        ('${toll_allow}', '${toll_allow}'),
        ('${sip_h_Diversion}', '${sip_h_Diversion}')]
        ),
        ('--- Applications -------------', [
        ('acknowledge_call', 'acknowledge_call'),
        ('answer', 'answer'),
        ('att_xfer', 'att_xfer'),
        ('bgsystem', 'bgsystem'),
        ('bind_digit_action', 'bind_digit_action'),
        ('bind_meta_app', 'bind_meta_app'),
        ('block_dtmf', 'block_dtmf'),
        ('break', 'break'),
        ('bridge', 'bridge'),
        ('bridge_export', 'bridge_export'),
        ('broadcast', 'broadcast'),
        ('callcenter', 'callcenter'),
        ('callcenter_track', 'callcenter_track'),
        ('capture', 'capture'),
        ('capture_text', 'capture_text'),
        ('check_acl', 'check_acl'),
        ('clear_digit_action', 'clear_digit_action'),
        ('clear_speech_cache', 'clear_speech_cache'),
        ('cng_plc', 'cng_plc'),
        ('conference', 'conference'),
        ('conference_set_auto_outcall', 'conference_set_auto_outcall'),
        ('db', 'db'),
        ('decode_video', 'decode_video'),
        ('deduplicate_dtmf', 'deduplicate_dtmf'),
        ('deflect', 'deflect'),
        ('delay_echo', 'delay_echo'),
        ('detect_audio', 'detect_audio'),
        ('detect_silence', 'detect_silence'),
        ('detect_speech', 'detect_speech'),
        ('digit_action_set_realm', 'digit_action_set_realm'),
        ('displace_session', 'displace_session'),
        ('early_hangup', 'early_hangup'),
        ('eavesdrop', 'eavesdrop'),
        ('echo', 'echo'),
        ('enable_heartbeat', 'enable_heartbeat'),
        ('enable_keepalive', 'enable_keepalive'),
        ('endless_playback', 'endless_playback'),
        ('enum', 'enum'),
        ('eval', 'eval'),
        ('event', 'event'),
        ('execute_extension', 'execute_extension'),
        ('export', 'export'),
        ('fax_detect', 'fax_detect'),
        ('fifo', 'fifo'),
        ('fifo_track_call', 'fifo_track_call'),
        ('filter_codecs', 'filter_codecs'),
        ('fire', 'fire'),
        ('flush_dtmf', 'flush_dtmf'),
        ('gentones', 'gentones'),
        ('group', 'group'),
        ('hangup', 'hangup'),
        ('hash', 'hash'),
        ('hold', 'hold'),
        ('info', 'info'),
        ('intercept', 'intercept'),
        ('ivr', 'ivr'),
        ('jitterbuffer', 'jitterbuffer'),
        ('limit', 'limit'),
        ('limit_execute', 'limit_execute'),
        ('limit_hash', 'limit_hash'),
        ('limit_hash_execute', 'limit_hash_execute'),
        ('log', 'log'),
        ('loop_playback', 'loop_playback'),
        ('media_reset', 'media_reset'),
        ('mkdir', 'mkdir'),
        ('msrp_recv_file', 'msrp_recv_file'),
        ('msrp_send_file', 'msrp_send_file'),
        ('multiset', 'multiset'),
        ('multiunset', 'multiunset'),
        ('mutex', 'mutex'),
        ('native_eavesdrop', 'native_eavesdrop'),
        ('novideo', 'novideo'),
        ('park', 'park'),
        ('park_state', 'park_state'),
        ('phrase', 'phrase'),
        ('pickup', 'pickup'),
        ('play_and_detect_speech', 'play_and_detect_speech'),
        ('play_and_get_digits', 'play_and_get_digits'),
        ('play_fsv', 'play_fsv'),
        ('play_yuv', 'play_yuv'),
        ('playback', 'playback'),
        ('pre_answer', 'pre_answer'),
        ('preprocess', 'preprocess'),
        ('presence', 'presence'),
        ('privacy', 'privacy'),
        ('push', 'push'),
        ('python', 'python'),
        ('queue_dtmf', 'queue_dtmf'),
        ('read', 'read'),
        ('record', 'record'),
        ('record_fsv', 'record_fsv'),
        ('record_session', 'record_session'),
        ('record_session_mask', 'record_session_mask'),
        ('record_session_unmask', 'record_session_unmask'),
        ('recovery_refresh', 'recovery_refresh'),
        ('redirect', 'redirect'),
        ('remove_bugs', 'remove_bugs'),
        ('rename', 'rename'),
        ('reply', 'reply'),
        ('respond', 'respond'),
        ('ring_ready', 'ring_ready'),
        ('rxfax', 'rxfax'),
        ('say', 'say'),
        ('sched_broadcast', 'sched_broadcast'),
        ('sched_cancel', 'sched_cancel'),
        ('sched_hangup', 'sched_hangup'),
        ('sched_heartbeat', 'sched_heartbeat'),
        ('sched_transfer', 'sched_transfer'),
        ('send', 'send'),
        ('send_display', 'send_display'),
        ('send_dtmf', 'send_dtmf'),
        ('send_info', 'send_info'),
        ('session_loglevel', 'session_loglevel'),
        ('set', 'set'),
        ('set_audio_level', 'set_audio_level'),
        ('set_global', 'set_global'),
        ('set_media_stats', 'set_media_stats'),
        ('set_mute', 'set_mute'),
        ('set_name', 'set_name'),
        ('set_profile_var', 'set_profile_var'),
        ('set_user', 'set_user'),
        ('set_zombie_exec', 'set_zombie_exec'),
        ('sleep', 'sleep'),
        ('socket', 'socket'),
        ('sofia_sla', 'sofia_sla'),
        ('soft_hold', 'soft_hold'),
        ('sound_test', 'sound_test'),
        ('spandsp_detect_tdd', 'spandsp_detect_tdd'),
        ('spandsp_inject_tdd', 'spandsp_inject_tdd'),
        ('spandsp_send_tdd', 'spandsp_send_tdd'),
        ('spandsp_start_dtmf', 'spandsp_start_dtmf'),
        ('spandsp_start_fax_detect', 'spandsp_start_fax_detect'),
        ('spandsp_start_tone_detect', 'spandsp_start_tone_detect'),
        ('spandsp_stop_detect_tdd', 'spandsp_stop_detect_tdd'),
        ('spandsp_stop_dtmf', 'spandsp_stop_dtmf'),
        ('spandsp_stop_fax_detect', 'spandsp_stop_fax_detect'),
        ('spandsp_stop_inject_tdd', 'spandsp_stop_inject_tdd'),
        ('spandsp_stop_tone_detect', 'spandsp_stop_tone_detect'),
        ('speak', 'speak'),
        ('start_dtmf', 'start_dtmf'),
        ('start_dtmf_generate', 'start_dtmf_generate'),
        ('stop', 'stop'),
        ('stop_displace_session', 'stop_displace_session'),
        ('stop_dtmf', 'stop_dtmf'),
        ('stop_dtmf_generate', 'stop_dtmf_generate'),
        ('stop_record_session', 'stop_record_session'),
        ('stop_tone_detect', 'stop_tone_detect'),
        ('stop_video_write_overlay', 'stop_video_write_overlay'),
        ('stopfax', 'stopfax'),
        ('strftime', 'strftime'),
        ('t38_gateway', 't38_gateway'),
        ('three_way', 'three_way'),
        ('tone_detect', 'tone_detect'),
        ('transfer', 'transfer'),
        ('transfer_vars', 'transfer_vars'),
        ('txfax', 'txfax'),
        ('unbind_meta_app', 'unbind_meta_app'),
        ('unblock_dtmf', 'unblock_dtmf'),
        ('unhold', 'unhold'),
        ('unloop', 'unloop'),
        ('unset', 'unset'),
        ('unshift', 'unshift'),
        ('vad_test', 'vad_test'),
        ('valet_park', 'valet_park'),
        ('verbose_events', 'verbose_events'),
        ('video_decode', 'video_decode'),
        ('video_refresh', 'video_refresh'),
        ('video_write_overlay', 'video_write_overlay'),
        ('wait_for_answer', 'wait_for_answer'),
        ('wait_for_silence', 'wait_for_silence'),
        ('wait_for_video_ready', 'wait_for_video_ready')]),
    ]

    time_condition_attrib = ['year', 'mon', 'mday', 'wday', 'week', 'mweek', 'hour', 'minute-of-day', 'date-time']

    def generate_xml(self, dp_uuid, domain_uuid, domain_name, ddList=None):

        dp = dialplans.models.Dialplan.objects.get(pk=dp_uuid)

        root = etree.Element("extension", name=dp.name)
        root.set('continue', dp.dp_continue)
        root.set('uuid', str(dp.id))

        if not ddList:
            ddList = dialplans.models.DialplanDetail.objects.filter(dialplan_id=dp.id).order_by(
                    'group',
                    Case(
                     When(tag='condition', then=Value(1)),
                     When(tag='action', then=Value(2)),
                     When(tag='anti-action', then=Value(3)),
                     default=Value(100)
                    ),
                    'sequence'
                    )

        last_condition_type = 'default'
        first_action = True

        for dd in ddList:
            if dd.data is None:
                dd_data = ''
            else:
                dd_data = dd.data
            if dd.type is None:
                dd_type = ''
            else:
                dd_type = dd.type

            if dd.tag == "condition":
                # determine the type of condition
                if dd_type in self.time_condition_attrib:
                    condition_type = 'time'
                else:
                    condition_type = 'default'

                if condition_type == 'default':
                    condition = etree.SubElement(root, "condition", field=dd_type, expression=dd_data)
                    last_condition_type = 'default'

                if condition_type == 'time':
                    if last_condition_type == 'time':
                        condition.set(dd_type, dd_data)
                    else:
                        condition = etree.SubElement(root, "condition")
                        condition.set(dd_type, dd_data)
                        last_condition_type = 'time'

                if dd.dp_break:
                    if len(dd.dp_break) > 0:
                        condition.set('break', dd.dp_break)

            if dp.context == "public" or dp.context[0:7] == "public@" or dp.context[-7:] == ".public":
                if dd.tag == "action":
                    if first_action:
                        first_action = False
                        if dp.category == 'Inbound route':
                            etree.SubElement(
                                condition, dd.tag, application='export',
                                data="call_direction=inbound", inline='true'
                                )
                            firstaction = etree.SubElement(condition, dd.tag)
                            firstaction.set('application', 'set')
                            firstaction.set('data', 'domain_uuid=' + str(domain_uuid))
                            firstaction.set('inline', 'true')
                            firstaction = etree.SubElement(condition, dd.tag)
                            firstaction.set('application', 'set')
                            firstaction.set('data', 'domain_name=' + domain_name)
                            firstaction.set('inline', 'true')

            if dd.tag == "action" or dd.tag == "anti-action":
                last_condition_type = 'default'
                actionanti = etree.SubElement(condition, dd.tag, application=dd_type, data=dd_data)

                if dd.inline:
                    if len(dd.inline) > 0:
                        actionanti.set('inline', dd.inline)

        etree.indent(root)
        return str(etree.tostring(root), "utf-8").replace('&lt;', '<').replace('&gt;', '>')

    def create_dpd_from_xml(self, dp_uuid, username):
        dp = dialplans.models.Dialplan.objects.get(pk=dp_uuid)
        regex = re.compile('expression=\"(.*)\"', re.MULTILINE)
        # FreeSWITCH doesn't seem to mind < and > in an XML attribute although technically wrong, but lxml does mind.
        xml = regex.sub(lambda m: m.group().replace('<', "&lt;").replace('>', "&gt;"), dp.xml)
        parser = etree.XMLParser(remove_comments=True)
        tree = etree.parse(StringIO(xml), parser)
        extension = tree.getroot()

        if not etree.iselement(extension):
            return False

        if len(extension):  # check root has children
            if extension.tag == 'extension':
                dialplans.models.DialplanDetail.objects.filter(dialplan_id=dp_uuid).delete()

                ddgroup = 0
                ddorder = 10
                for extchild in extension:
                    if extchild.tag == 'condition':
                        if extchild.get('break'):
                            ddbreak = extchild.get('break')
                        else:
                            ddbreak = ''

                        add_non_time_condition = True
                        for m in extchild.attrib:
                            if m in self.time_condition_attrib:
                                add_non_time_condition = False
                                self.dp_detail_add(
                                    dp,
                                    'condition',
                                    m,
                                    extchild.get(m),
                                    ddbreak,
                                    '',
                                    ddgroup,
                                    ddorder,
                                    username
                                    )

                        if add_non_time_condition:
                            self.dp_detail_add(
                                dp,
                                'condition',
                                extchild.get('field'),
                                extchild.get('expression'),
                                ddbreak,
                                '',
                                ddgroup,
                                ddorder,
                                username
                                )
                        ddorder += 10
                        if len(extchild):  # check element has children
                            for actchild in extchild:
                                if actchild.get('inline'):
                                    ddinline = actchild.get('inline')
                                else:
                                    ddinline = ''

                                self.dp_detail_add(
                                    dp,
                                    actchild.tag,
                                    actchild.get('application'),
                                    actchild.get('data'),
                                    '',
                                    ddinline,
                                    ddgroup,
                                    ddorder,
                                    username
                                    )
                                ddorder += 10
                            ddgroup += 1

    def import_xml(self, domain_name, dp_remove=False, domain_uuid=''):
        dp_details = False
        pbxsettings = PbxSettings()
        sval = pbxsettings.default_settings('dialplan', 'dialplan_details', 'boolean', 'false', True)[0]
        if sval == 'true':
            dp_details = True
        sval = pbxsettings.default_settings('security', 'pin_length', 'numeric', '8', True)
        if sval:
            try:
                pin_length = int(sval[0])
            except ValueError:
                # Handle the exception
                pin_length = 8

        httapi_url = pbxsettings.default_settings('dialplan', 'httapi_url', 'text', 'http://127.0.0.1:8008', True)[0]
        path_of_xml = settings.BASE_DIR / 'dialplans/resources/switch/conf/dialplan'
        ext = ('.xml')
        for files in os.listdir(path_of_xml):
            if files.endswith(ext):
                pin = BaseUserManager().make_random_password(pin_length, '1234567890')
                with open(path_of_xml / files) as f:
                    xml = f.read()

                xml = xml.replace('{v_context}', domain_name)
                xml = xml.replace('{v_pin_number}', pin)
                xml = xml.replace('{v_httapi_url}', httapi_url)
                self.create_dp_from_xml(xml, dp_remove, dp_details)

            else:
                continue

    def create_dp_from_xml(self, xml, dp_remove=False, dp_details=True):
        parser = etree.XMLParser(remove_comments=True)
        tree = etree.parse(StringIO(xml), parser)
        root = tree.getroot()
        # root = etree.fromstring(xml) # Using method above so comments are removed.
        ddlist = []

        if len(root):  # check root has children
            extension = root[0]

            context_attributes = root.attrib
            dp_context = context_attributes['name']
            d_uuid = ''
            d = None
            if not ((dp_context == 'public') or (dp_context == '${domain_name}')):
                if not Domain.objects.filter(name=dp_context).exists():
                    return False

                d = Domain.objects.get(name=dp_context)
                d_uuid = str(d.id)

            if extension.tag == 'extension':
                attributes = extension.attrib

                if 'global' in attributes:
                    dp_global = attributes['global']
                else:
                    dp_global = 'false'

                if dp_global == 'true':
                    d_uuid = ''

                if 'app_uuid' in attributes:
                    dp_app_uuid = attributes['app_uuid']
                else:
                    dp_app_uuid = 'f17e714e-d7a2-4783-947b-8cc3bb2337af'

                if dp_remove:
                    self.dp_app_remove(d_uuid, dp_app_uuid)

                if self.dp_app_exists(d_uuid, dp_app_uuid):
                    return False

                if 'enabled' in attributes:
                    dp_enabled = attributes['enabled']
                else:
                    dp_enabled = 'true'

                try:
                    dp_order = int(attributes['order'])
                except ValueError:
                    # Handle the exception
                    dp_order = 10

                if 'continue' in attributes:
                    xml_dp_continue = attributes['continue']
                else:
                    xml_dp_continue = 'true'

                if 'number' in attributes:
                    dp_number = attributes['number']
                else:
                    dp_number = 'N/A'

                if 'name' in attributes:
                    dp_name = attributes['name']
                else:
                    dp_name = 'No Name'

                dp = dialplans.models.Dialplan.objects.create(
                    app_id=dp_app_uuid,
                    name=dp_name,
                    number=dp_number,
                    destination='false',
                    context=dp_context,
                    dp_continue=xml_dp_continue,
                    sequence=dp_order,
                    enabled=dp_enabled,
                    updated_by='system'
                )
                if dp_global == 'false':
                    dp.domain_id = d
                    dp.save()

                ddgroup = 0
                ddorder = 5
                for extchild in extension:
                    if extchild.tag == 'condition':
                        if extchild.get('break'):
                            ddbreak = extchild.get('break')
                        else:
                            ddbreak = ''

                        if dp_details:
                            self.dp_detail_add(
                                dp,
                                'condition',
                                extchild.get('field'),
                                extchild.get('expression'),
                                ddbreak,
                                '',
                                ddgroup,
                                ddorder
                                )
                        ddlist.append(DialplanDetailStruct(
                            str(dp.id),
                            'condition',
                            extchild.get('field'),
                            extchild.get('expression'),
                            ddbreak,
                            '',
                            ddgroup,
                            ddorder
                            ))
                        ddorder += 5
                        if len(extchild):  # check element has children
                            for actchild in extchild:
                                if actchild.get('inline'):
                                    ddinline = actchild.get('inline')
                                else:
                                    ddinline = ''

                                if dp_details:
                                    self.dp_detail_add(
                                        dp,
                                        actchild.tag,
                                        actchild.get('application'),
                                        actchild.get('data'),
                                        '',
                                        ddinline,
                                        ddgroup,
                                        ddorder
                                        )
                                ddlist.append(DialplanDetailStruct(
                                    str(dp.id),
                                    actchild.tag,
                                    actchild.get('application'),
                                    actchild.get('data'),
                                    '',
                                    ddinline,
                                    ddgroup,
                                    ddorder
                                    ))

                                ddorder += 5
                            ddgroup += 1

                dp.xml = self.generate_xml(dp.id, '', '', ddlist)
                dp.save()

    def dp_add(
            self, domain_id, dp_app_uuid, dp_name, dp_number, dp_destination, dp_context,
            dp_category, dp_continue, dp_order, dp_enabled, dp_description, dp_updated_by
            ):

        d = Domain.objects.get(pk=uuid.UUID(domain_id))

        dp = dialplans.models.Dialplan.objects.create(
            domain_id=d,
            app_id=dp_app_uuid,
            name=dp_name,
            number=dp_number,
            destination=dp_destination,
            context=dp_context,
            category=dp_category,
            dp_continue=dp_continue,
            sequence=dp_order,
            enabled=dp_enabled,
            description=dp_description,
            updated_by=dp_updated_by
        )
        return dp

    def dp_detail_add(self, dddp, ddtag, ddtype, dddata, ddbreak, ddinline, ddgroup, ddorder, username='system'):
        dpd = dialplans.models.DialplanDetail.objects.create(
            dialplan_id=dddp,
            tag=ddtag,
            type=ddtype,
            data=dddata,
            dp_break=ddbreak,
            inline=ddinline,
            group=ddgroup,
            sequence=ddorder,
            updated_by=username
        )
        return dpd

    def dp_app_exists(self, dp_domain_uuid, dp_app_uuid):
        if not valid_uuid4(dp_app_uuid):
            return True  # Better to return True than create a dialplan with an invalid uuid

        if valid_uuid4(dp_domain_uuid):
            dpextist = dialplans.models.Dialplan.objects.filter(
                (Q(domain_id=dp_domain_uuid) | Q(domain_id__isnull=True)),
                app_id=dp_app_uuid
                ).exists()
        else:
            dpextist = dialplans.models.Dialplan.objects.filter(domain_id__isnull=True, app_id=dp_app_uuid).exists()
        return dpextist

    def dp_app_remove(self, dp_domain_uuid, dp_app_uuid):
        if not valid_uuid4(dp_app_uuid):
            return False

        if valid_uuid4(dp_domain_uuid):  # do not remove global dialplans
            dialplans.models.Dialplan.objects.filter(domain_id=dp_domain_uuid, app_id=dp_app_uuid).delete()
        else:
            return False
        return True

    def dpd_order_max(self, dp_uuid):
        dpd_max = dialplans.models.DialplanDetail.objects.filter(dialplan_id=dp_uuid).aggregate(Max('sequence'))
        if not dpd_max:
            return 10
        if dpd_max.get('sequence__max') < 10:
            return 10
        return dpd_max.get('sequence__max')


class DpApps():

    def get_dp_apps_choices(self):
        dp_category_choices = [
            ('Outbound route',  _('Outbound route')),
            ('Inbound route',   _('Inbound route')),
            ('Time condition',  _('Time condition')),
            ]
        for acnf in apps.get_app_configs():
            if hasattr(acnf, 'pbx_dialplan'):
                dp_category_choices.append((acnf.pbx_dialplan_category, _(acnf.pbx_dialplan_category)))

        return dp_category_choices

    def get_dp_apps_uuids(self,):
        dp_category_uuids = {
            'Outbound route': '8c914ec3-9fc0-8ab5-4cda-6c9288bdc9a3',
            'Inbound route': 'c03b422e-13a8-bd1b-e42b-b6b9b4d27ce4',
            'Time condition': '4b821450-926b-175a-af93-a03c441818b1',
            }
        for acnf in apps.get_app_configs():
            if hasattr(acnf, 'pbx_dialplan'):
                dp_category_uuids[acnf.pbx_dialplan_category] = acnf.pbx_uuid

        return dp_category_uuids


class DialplanDetailStruct():

    def __init__(self, dddp, ddtag, ddtype, dddata, ddbreak, ddinline, ddgroup, ddorder):
        self.dialplan_id  = dddp      # noqa: E221
        self.tag          = ddtag     # noqa: E221
        self.type         = ddtype    # noqa: E221
        self.data         = dddata    # noqa: E221
        self.dp_break     = ddbreak   # noqa: E221
        self.inline       = ddinline  # noqa: E221
        self.group        = ddgroup   # noqa: E221
        self.sequence     = ddorder   # noqa: E221
