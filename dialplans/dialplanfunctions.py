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


class DpFunctions():
    def string_to_regex(string, prefix=''):
        # add prefix
        if len(prefix) > 0:
            if len(prefix) > 0 and len(prefix) < 4:
                if string[0] == "+":
                    prefix = prefix + "?"
                else:
                    prefix = "\+?" + prefix + "?"
            else:
                prefix = "(?:" + prefix + ")?"

        # escape the plus
        if string[0] == "+":
            string = "^\+(" + string[1:] + ")$"

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

    def valid_uuid4(self, uuid):
        regex = re.compile('[0-9A-F]{8}-[0-9A-F]{4}-[4][0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}', re.I)
        match = regex.match(uuid)
        return bool(match)


class SwitchDp():
    tag_type_choices = [
        ('context', 'Cnd/Rxp. Context'),
        ('username', 'Cnd/Rxp. Username'),
        ('rdnis', 'Cnd/Rxp. RDNIS'),
        ('destination_number', 'Cnd/Rxp. Destination Number'),
        ('dialplan', 'Cnd/Rxp. Dialplan'),
        ('caller_id_name', 'Cnd/Rxp. Caller ID Name'),
        ('caller_id_number', 'Cnd/Rxp. Caller ID Number'),
        ('ani', 'Cnd/Rxp. ANI'),
        ('ani2', 'Cnd/Rxp. ANI2'),
        ('uuid', 'Cnd/Rxp. UUID'),
        ('source', 'Cnd/Rxp. Source'),
        ('chan_name', 'Cnd/Rxp. Channel Name'),
        ('network_addr', 'Cnd/Rxp. Network Address'),
        ('${number_alias}', 'Cnd/Rxp. ${number_alias}'),
        ('${sip_from_uri}', 'Cnd/Rxp. ${sip_from_uri}'),
        ('${sip_from_user}', 'Cnd/Rxp. ${sip_from_user}'),
        ('${sip_from_host}', 'Cnd/Rxp. ${sip_from_host}'),
        ('${sip_contact_uri}', 'Cnd/Rxp. ${sip_contact_uri}'),
        ('${sip_contact_user}', 'Cnd/Rxp. ${sip_contact_user}'),
        ('${sip_contact_host}', 'Cnd/Rxp. ${sip_contact_host}'),
        ('${sip_to_uri}', 'Cnd/Rxp. ${sip_to_uri}'),
        ('${sip_to_user}', 'Cnd/Rxp. ${sip_to_user}'),
        ('${sip_to_host}', 'Cnd/Rxp. ${sip_to_host}'),
        ('${toll_allow}', 'Cnd/Rxp. ${toll_allow}'),
        ('${sip_h_Diversion}', 'Cnd/Rxp. ${sip_h_Diversion}'),
        ('', '---------------'),
        ('acknowledge_call', 'App. acknowledge_call'),
        ('answer', 'App. answer'),
        ('att_xfer', 'App. att_xfer'),
        ('bgsystem', 'App. bgsystem'),
        ('bind_digit_action', 'App. bind_digit_action'),
        ('bind_meta_app', 'App. bind_meta_app'),
        ('block_dtmf', 'App. block_dtmf'),
        ('break', 'App. break'),
        ('bridge', 'App. bridge'),
        ('bridge_export', 'App. bridge_export'),
        ('broadcast', 'App. broadcast'),
        ('callcenter', 'App. callcenter'),
        ('callcenter_track', 'App. callcenter_track'),
        ('capture', 'App. capture'),
        ('capture_text', 'App. capture_text'),
        ('check_acl', 'App. check_acl'),
        ('clear_digit_action', 'App. clear_digit_action'),
        ('clear_speech_cache', 'App. clear_speech_cache'),
        ('cng_plc', 'App. cng_plc'),
        ('conference', 'App. conference'),
        ('conference_set_auto_outcall', 'App. conference_set_auto_outcall'),
        ('db', 'App. db'),
        ('decode_video', 'App. decode_video'),
        ('deduplicate_dtmf', 'App. deduplicate_dtmf'),
        ('deflect', 'App. deflect'),
        ('delay_echo', 'App. delay_echo'),
        ('detect_audio', 'App. detect_audio'),
        ('detect_silence', 'App. detect_silence'),
        ('detect_speech', 'App. detect_speech'),
        ('digit_action_set_realm', 'App. digit_action_set_realm'),
        ('displace_session', 'App. displace_session'),
        ('early_hangup', 'App. early_hangup'),
        ('eavesdrop', 'App. eavesdrop'),
        ('echo', 'App. echo'),
        ('enable_heartbeat', 'App. enable_heartbeat'),
        ('enable_keepalive', 'App. enable_keepalive'),
        ('endless_playback', 'App. endless_playback'),
        ('enum', 'App. enum'),
        ('eval', 'App. eval'),
        ('event', 'App. event'),
        ('execute_extension', 'App. execute_extension'),
        ('export', 'App. export'),
        ('fax_detect', 'App. fax_detect'),
        ('fifo', 'App. fifo'),
        ('fifo_track_call', 'App. fifo_track_call'),
        ('filter_codecs', 'App. filter_codecs'),
        ('fire', 'App. fire'),
        ('flush_dtmf', 'App. flush_dtmf'),
        ('gentones', 'App. gentones'),
        ('group', 'App. group'),
        ('hangup', 'App. hangup'),
        ('hash', 'App. hash'),
        ('hold', 'App. hold'),
        ('info', 'App. info'),
        ('intercept', 'App. intercept'),
        ('ivr', 'App. ivr'),
        ('jitterbuffer', 'App. jitterbuffer'),
        ('limit', 'App. limit'),
        ('limit_execute', 'App. limit_execute'),
        ('limit_hash', 'App. limit_hash'),
        ('limit_hash_execute', 'App. limit_hash_execute'),
        ('log', 'App. log'),
        ('loop_playback', 'App. loop_playback'),
        ('media_reset', 'App. media_reset'),
        ('mkdir', 'App. mkdir'),
        ('msrp_recv_file', 'App. msrp_recv_file'),
        ('msrp_send_file', 'App. msrp_send_file'),
        ('multiset', 'App. multiset'),
        ('multiunset', 'App. multiunset'),
        ('mutex', 'App. mutex'),
        ('native_eavesdrop', 'App. native_eavesdrop'),
        ('novideo', 'App. novideo'),
        ('park', 'App. park'),
        ('park_state', 'App. park_state'),
        ('phrase', 'App. phrase'),
        ('pickup', 'App. pickup'),
        ('play_and_detect_speech', 'App. play_and_detect_speech'),
        ('play_and_get_digits', 'App. play_and_get_digits'),
        ('play_fsv', 'App. play_fsv'),
        ('play_yuv', 'App. play_yuv'),
        ('playback', 'App. playback'),
        ('pre_answer', 'App. pre_answer'),
        ('preprocess', 'App. preprocess'),
        ('presence', 'App. presence'),
        ('privacy', 'App. privacy'),
        ('push', 'App. push'),
        ('python', 'App. python'),
        ('queue_dtmf', 'App. queue_dtmf'),
        ('read', 'App. read'),
        ('record', 'App. record'),
        ('record_fsv', 'App. record_fsv'),
        ('record_session', 'App. record_session'),
        ('record_session_mask', 'App. record_session_mask'),
        ('record_session_unmask', 'App. record_session_unmask'),
        ('recovery_refresh', 'App. recovery_refresh'),
        ('redirect', 'App. redirect'),
        ('remove_bugs', 'App. remove_bugs'),
        ('rename', 'App. rename'),
        ('reply', 'App. reply'),
        ('respond', 'App. respond'),
        ('ring_ready', 'App. ring_ready'),
        ('rxfax', 'App. rxfax'),
        ('say', 'App. say'),
        ('sched_broadcast', 'App. sched_broadcast'),
        ('sched_cancel', 'App. sched_cancel'),
        ('sched_hangup', 'App. sched_hangup'),
        ('sched_heartbeat', 'App. sched_heartbeat'),
        ('sched_transfer', 'App. sched_transfer'),
        ('send', 'App. send'),
        ('send_display', 'App. send_display'),
        ('send_dtmf', 'App. send_dtmf'),
        ('send_info', 'App. send_info'),
        ('session_loglevel', 'App. session_loglevel'),
        ('set', 'App. set'),
        ('set_audio_level', 'App. set_audio_level'),
        ('set_global', 'App. set_global'),
        ('set_media_stats', 'App. set_media_stats'),
        ('set_mute', 'App. set_mute'),
        ('set_name', 'App. set_name'),
        ('set_profile_var', 'App. set_profile_var'),
        ('set_user', 'App. set_user'),
        ('set_zombie_exec', 'App. set_zombie_exec'),
        ('sleep', 'App. sleep'),
        ('socket', 'App. socket'),
        ('sofia_sla', 'App. sofia_sla'),
        ('soft_hold', 'App. soft_hold'),
        ('sound_test', 'App. sound_test'),
        ('spandsp_detect_tdd', 'App. spandsp_detect_tdd'),
        ('spandsp_inject_tdd', 'App. spandsp_inject_tdd'),
        ('spandsp_send_tdd', 'App. spandsp_send_tdd'),
        ('spandsp_start_dtmf', 'App. spandsp_start_dtmf'),
        ('spandsp_start_fax_detect', 'App. spandsp_start_fax_detect'),
        ('spandsp_start_tone_detect', 'App. spandsp_start_tone_detect'),
        ('spandsp_stop_detect_tdd', 'App. spandsp_stop_detect_tdd'),
        ('spandsp_stop_dtmf', 'App. spandsp_stop_dtmf'),
        ('spandsp_stop_fax_detect', 'App. spandsp_stop_fax_detect'),
        ('spandsp_stop_inject_tdd', 'App. spandsp_stop_inject_tdd'),
        ('spandsp_stop_tone_detect', 'App. spandsp_stop_tone_detect'),
        ('speak', 'App. speak'),
        ('start_dtmf', 'App. start_dtmf'),
        ('start_dtmf_generate', 'App. start_dtmf_generate'),
        ('stop', 'App. stop'),
        ('stop_displace_session', 'App. stop_displace_session'),
        ('stop_dtmf', 'App. stop_dtmf'),
        ('stop_dtmf_generate', 'App. stop_dtmf_generate'),
        ('stop_record_session', 'App. stop_record_session'),
        ('stop_tone_detect', 'App. stop_tone_detect'),
        ('stop_video_write_overlay', 'App. stop_video_write_overlay'),
        ('stopfax', 'App. stopfax'),
        ('strftime', 'App. strftime'),
        ('t38_gateway', 'App. t38_gateway'),
        ('three_way', 'App. three_way'),
        ('tone_detect', 'App. tone_detect'),
        ('transfer', 'App. transfer'),
        ('transfer_vars', 'App. transfer_vars'),
        ('txfax', 'App. txfax'),
        ('unbind_meta_app', 'App. unbind_meta_app'),
        ('unblock_dtmf', 'App. unblock_dtmf'),
        ('unhold', 'App. unhold'),
        ('unloop', 'App. unloop'),
        ('unset', 'App. unset'),
        ('unshift', 'App. unshift'),
        ('vad_test', 'App. vad_test'),
        ('valet_park', 'App. valet_park'),
        ('verbose_events', 'App. verbose_events'),
        ('video_decode', 'App. video_decode'),
        ('video_refresh', 'App. video_refresh'),
        ('video_write_overlay', 'App. video_write_overlay'),
        ('wait_for_answer', 'App. wait_for_answer'),
        ('wait_for_silence', 'App. wait_for_silence'),
        ('wait_for_video_ready', 'App. wait_for_video_ready'),
    ]


    def generate_xml(self, dp_uuid, domain_uuid, domain_name):

        dp = dialplans.models.Dialplan.objects.get(pk=dp_uuid)

        root = etree.Element("extension", name= dp.name)
        root.set('continue', dp.dp_continue)
        root.set('uuid', str(dp.id))


        ddList = dialplans.models.DialplanDetail.objects.filter(dialplan_id = dp.id).order_by(
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
            # clear flag pass
            dppass = False
            if dd.data is None:
                dd_data  = ''
            else:
                dd_data  = dd.data
            if dd.type is None:
                dd_type  = ''
            else:
                dd_type  = dd.type

            if dd.tag == "condition":
                #determine the type of condition
                if dd_type == "hour":
                    condition_type = 'time'
                elif dd_type == "minute":
                    condition_type = 'time'
                elif dd_type == "minute-of-day":
                    condition_type = 'time'
                elif dd_type == "mday":
                    condition_type = 'time'
                elif dd_type == "mweek":
                    condition_type = 'time'
                elif dd_type == "mon":
                    condition_type = 'time'
                elif dd_type == "time-of-day":
                    condition_type = 'time'
                elif dd_type == "yday":
                    condition_type = 'time'
                elif dd_type == "year":
                    condition_type = 'time'
                elif dd_type == "wday":
                    condition_type = 'time'
                elif dd_type == "week":
                    condition_type = 'time'
                elif dd_type == "date-time":
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
                        last_condition_type = 'time'

                if dd.dp_break:
                    if len(dd.dp_break) > 0:
                        condition.set('break', dd.dp_break)

            if dp.context == "public" or dp.context[0:7] == "public@" or dp.context[-7:] == ".public":
                if dd.tag == "action":
                    if first_action:
                        first_action = False
                        if dp.category == 'Inbound route':
                            etree.SubElement(condition, dd.tag, application="export", data="call_direction=inbound", inline="true")
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
        regex = re.compile('expression=\"(.*)\"',re.MULTILINE)
        # FreeSWITCH doesn't seem to mind < and > in an XML attribute although technically wrong, but lxml does mind.
        xml = regex.sub(lambda m: m.group().replace('<',"&lt;").replace('>',"&gt;"), dp.xml)
        parser = etree.XMLParser(remove_comments=True)
        tree   = etree.parse(StringIO(xml), parser)
        extension = tree.getroot()

        if not etree.iselement(extension):
            return False

        if len(extension):  # check root has children
            if extension.tag == 'extension':
                dialplans.models.DialplanDetail.objects.filter(dialplan_id = dp_uuid).delete()

                ddgroup = 0
                ddorder = 10
                for extchild in extension:
                    if extchild.tag == 'condition':
                        if extchild.get('break'):
                            ddbreak = extchild.get('break')
                        else:
                            ddbreak = ''

                        self.dp_detail_add(dp,
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

                                self.dp_detail_add(dp,
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


    def import_xml(self, domain_name, dp_remove = False, domain_uuid = ''):
        sval = PbxSettings().default_settings('security', 'pin_length', 'numeric', 8)
        if sval:
            try:
                pin_length = int(sval[0])
            except ValueError:
                # Handle the exception
                pin_length = 8

        path_of_xml = settings.BASE_DIR / 'dialplans/resources/switch/conf/dialplan'
        ext = ('.xml')
        for files in os.listdir(path_of_xml):
            if files.endswith(ext):
                pin = BaseUserManager().make_random_password(pin_length, '1234567890')
                with open(path_of_xml / files) as f:
                    xml = f.read()

                xml = xml.replace('{v_context}', domain_name)
                xml = xml.replace('{v_pin_number}', pin)
                self.create_dp_from_xml(xml, dp_remove)

            else:
                continue


    def create_dp_from_xml(self, xml, dp_remove = False):
        parser = etree.XMLParser(remove_comments=True)
        tree   = etree.parse(StringIO(xml), parser)
        root = tree.getroot()
        #root = etree.fromstring(xml) # Using method above so comments are removed.



        if len(root):  # check root has children
            extension = root[0]

            context_attributes = root.attrib
            dp_context = context_attributes['name']
            d_uuid = ''
            d = None
            if not ((dp_context == 'public') or (dp_context == '${domain_name}')):
                if not Domain.objects.filter(name = dp_context).exists():
                    return False

                d = Domain.objects.get(name = dp_context)
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
                    app_id = dp_app_uuid,
                    name = dp_name,
                    number = dp_number,
                    destination = 'false',
                    context = dp_context,
                    dp_continue = xml_dp_continue,
                    sequence = dp_order,
                    enabled = dp_enabled,
                    updated_by = 'system'
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

                        self.dp_detail_add(dp,
                            'condition',
                            extchild.get('field'),
                            extchild.get('expression'),
                            ddbreak,
                            '',
                            ddgroup,
                            ddorder
                        )
                        ddorder += 5
                        if len(extchild):  # check element has children
                            for actchild in extchild:
                                if actchild.get('inline'):
                                    ddinline = actchild.get('inline')
                                else:
                                    ddinline = ''

                                self.dp_detail_add(dp,
                                    actchild.tag,
                                    actchild.get('application'),
                                    actchild.get('data'),
                                    '',
                                    ddinline,
                                    ddgroup,
                                    ddorder
                                )
                                ddorder += 5
                            ddgroup += 1

                dp.xml = self.generate_xml(dp.id, '', '')
                dp.save()


    def dp_add(self, domain_id, dp_app_uuid, dp_name, dp_number, dp_destination, dp_context, dp_category, dp_continue, dp_order, dp_enabled, dp_description, dp_updated_by):
        d = Domain.objects.get(pk = uuid.UUID(domain_id))

        dp = dialplans.models.Dialplan.objects.create(
            domain_id = d,
            app_id = dp_app_uuid,
            name = dp_name,
            number = dp_number,
            destination = dp_destination,
            context = dp_context,
            category = dp_category,
            dp_continue = dp_continue,
            sequence = dp_order,
            enabled = dp_enabled,
            description = dp_description,
            updated_by = dp_updated_by
        )
        return dp


    def dp_detail_add(self, dddp, ddtag, ddtype, dddata, ddbreak, ddinline, ddgroup, ddorder, username = 'system'):
        dpd = dialplans.models.DialplanDetail.objects.create(
            dialplan_id = dddp,
            tag = ddtag,
            type = ddtype,
            data = dddata,
            dp_break = ddbreak,
            inline = ddinline,
            group = ddgroup,
            sequence = ddorder,
            updated_by = username
        )
        return dpd


    def dp_app_exists(self, dp_domain_uuid, dp_app_uuid):
        if not DpFunctions().valid_uuid4(dp_app_uuid):
            return True # Better to return True than create a dialplan with an invalid uuid

        if DpFunctions().valid_uuid4(dp_domain_uuid):
            dpextist = dialplans.models.Dialplan.objects.filter((Q(domain_id = dp_domain_uuid) | Q(domain_id__isnull=True)), app_id = dp_app_uuid).exists()
        else:
            dpextist = dialplans.models.Dialplan.objects.filter(domain_id__isnull=True, app_id = dp_app_uuid).exists()
        return dpextist


    def dp_app_remove(self, dp_domain_uuid, dp_app_uuid):
        if not DpFunctions().valid_uuid4(dp_app_uuid):
            return False

        if DpFunctions().valid_uuid4(dp_domain_uuid): # do not remove global dialplans
            dialplans.models.Dialplan.objects.filter(domain_id = dp_domain_uuid, app_id = dp_app_uuid).delete()
        else:
            return False
        return True


    def dpd_order_max(self, dp_uuid):
        dpd_max = dialplans.models.DialplanDetail.objects.filter(dialplan_id = dp_uuid).aggregate(Max('sequence'))
        if not dpd_max:
            return 10
        if dpd_max.get('sequence__max') < 10:
            return 10
        return dpd_max.get('sequence__max')



class DpApps():

    def get_dp_apps_choices(self):
        dp_category_choices = [('Outbound route', _('Outbound route')),
                                ('Inbound route', _('Inbound route')),
        ]
        for acnf in apps.get_app_configs():
            if hasattr(acnf, 'pbx_dialplan'):
                dp_category_choices.append((acnf.pbx_dialplan_category, _(acnf.pbx_dialplan_category)))

        return dp_category_choices


    def get_dp_apps_uuids(self,):
        dp_category_uuids = {'Outbound route': '8c914ec3-9fc0-8ab5-4cda-6c9288bdc9a3',
                            'Inbound route': 'c03b422e-13a8-bd1b-e42b-b6b9b4d27ce4',
        }
        for acnf in apps.get_app_configs():
            if hasattr(acnf, 'pbx_dialplan'):
                dp_category_uuids[acnf.pbx_dialplan_category] = acnf.pbx_uuid

        return dp_category_uuids


class DpDestAction():

    def get_dp_action_choices(self, domain_uuid):
        dp_actions = []
        e_list = []
        v_list = []
        es = Extension.objects.select_related('domain_id').prefetch_related('voicemail').filter(domain_id = uuid.UUID(domain_uuid),enabled = 'true').order_by('extension')
        for e in es:
            e_list.append(('transfer:%s XML %s' % (e.extension, e.domain_id), '%s %s' % (e.extension, e.description)))
            v = e.voicemail.filter(enabled = 'true').first()
            if v:
                v_list.append(('transfer:99%s XML %s' % (e.extension, e.domain_id), '%s(VM) %s' % (e.extension, e.description)))

        if len(e_list) > 0:
            dp_actions.append((_('Extensions'), e_list))
        if len(v_list) > 0:
            dp_actions.append((_('Voicemails'), v_list))

        t_list = []
        sv = SwitchVariable.objects.filter(category = 'Tones', enabled = 'true').order_by('name')
        for t in sv:
            t_list.append(('playback:tone_stream://%s' % t.value, t.name))

        if len(t_list) > 0:
            dp_actions.append((_('Tones'), t_list))

        return dp_actions
