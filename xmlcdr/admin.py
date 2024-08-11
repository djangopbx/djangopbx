#
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

from django.contrib import admin
from pbx.commonfunctions import DomainFilter, DomainUtils
from import_export.admin import ImportExportModelAdmin
from import_export import resources
import json
from django.forms import ModelForm
from django_ace import AceWidget
from .models import XmlCdr, CallTimeline
from .listfilters import (
    MosScoreListFilter, CallDurationListFilter, CallDirectionListFilter, HangupCauseListFilter,
    EventNameListFilter, EventSubclassListFilter
)

class PrettyJSONWidget(AceWidget):
    def format_value(self, value):
        value = json.dumps(json.loads(value), indent=4, sort_keys=True)
        return value


class JsonEditAdminForm(ModelForm):
    class Meta:
        model = XmlCdr
        widgets = {
            "xml": AceWidget(
                    usesofttabs=False, showprintmargin=False, width="800px",
                    height="400px", mode='xml', theme='cobalt', readonly=True
                    ),
            "json": PrettyJSONWidget(
                    usesofttabs=False, showprintmargin=False, width="800px",
                    height="400px", mode=None, theme='cobalt', readonly=True
                    ),
        }
        fields = '__all__'


class XmlCdrResource(resources.ModelResource):
    class Meta:
        model = XmlCdr
        import_id_fields = ('id', )


class XmlCdrAdmin(ImportExportModelAdmin):
    show_facets = admin.ShowFacets.NEVER
    resource_class = XmlCdrResource
    search_fields = ['caller_id_name', 'caller_id_number', 'destination_number']
    form = JsonEditAdminForm

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    fieldsets = [
        (None,  {'fields': [
                        'domain_id',
                        'extension_id',
                        'core_uuid',
                        'domain_name',
                        'accountcode',
                        'direction',
                        'context',
                        'caller_id_name',
                        'caller_id_number',
                        'caller_destination',
                        'source_number',
                        'destination_number',
                        'start_epoch',
                        'start_stamp',
                        'answer_epoch',
                        'answer_stamp',
                        'end_epoch',
                        'end_stamp',
                        'duration',
                        'mduration',
                        'billsec',
                        'billmsec',
                        'bridge_uuid',
                        'read_codec',
                        'read_rate',
                        'write_codec',
                        'write_rate',
                        'remote_media_ip',
                        'network_addr',
                        'record_path',
                        'record_name',
                        'leg',
                        'pdd_ms',
                        'rtp_audio_in_mos',
                        'last_app',
                        'last_arg',
                        'missed_call',
                        # 'digits_dialed',
                        'pin_number',
                        'hangup_cause',
                        'hangup_cause_q850',
                        'sip_hangup_disposition'
                        ]}),

        ('Conference',   {'fields': [
                            'conference_name', 'conference_uuid', 'conference_member_id'
                            ], 'classes': ['collapse']}),
        ('Call Centre',   {'fields': [
                        'cc_side',
                        'cc_member_uuid',
                        'cc_queue_joined_epoch',
                        'cc_queue',
                        'cc_member_session_uuid',
                        'cc_agent_uuid',
                        'cc_agent',
                        'cc_agent_type',
                        'cc_agent_bridged',
                        'cc_queue_answered_epoch',
                        'cc_queue_terminated_epoch',
                        'cc_queue_canceled_epoch',
                        'cc_cancel_reason',
                        'cc_cause',
                        'waitsec'
                        ], 'classes': ['collapse']}),
        ('JSON',   {'fields': ['json'], 'classes': ['collapse']}),
        ('XML',   {'fields': ['xml'], 'classes': ['collapse']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = (
        'extension_id', 'caller_id_name', 'caller_id_number', 'caller_destination',
        'destination_number', 'start_stamp', 'duration', 'rtp_audio_in_mos', 'hangup_cause'
        )
    list_filter = ('created', DomainFilter, CallDirectionListFilter, HangupCauseListFilter, MosScoreListFilter, CallDurationListFilter)

    ordering = [
        '-start_stamp', 'extension_id'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        if not change:
            obj.domain_id = DomainUtils().domain_from_session(request)
        super().save_model(request, obj, form, change)


class CallTimelineResource(resources.ModelResource):
    class Meta:
        model = CallTimeline
        import_id_fields = ('id', )


class CallTimelineAdmin(ImportExportModelAdmin):
    show_facets = admin.ShowFacets.NEVER
    resource_class = CallTimelineResource

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    fieldsets = [
        (None,  {'fields': [
                        'domain_id',
                        'core_uuid',
                        'hostname',
                        'switchame',
                        'switch_ipv4',
                        'switch_ipv6',
                        'call_uuid',
                        'event_name',
                        'event_subclass',
                        'event_date_local',
                        'event_epoch',
                        'event_sequence',
                        'event_calling_file',
                        'event_calling_function',
                        'direction',
                        'other_leg_direction',
                        'context',
                        'other_leg_context',
                        'hit_dialplan',
                        'caller_user_name',
                        'caller_ani',
                        'other_leg_user_name',
                        'caller_uuid',
                        'other_leg_caller_uuid',
                        'channel_name',
                        'channel_state',
                        'channel_call_state',
                        'answer_state',
                        'bridge_channel',
                        'caller_id_name',
                        'other_leg_caller_id_name',
                        'caller_id_number',
                        'other_leg_caller_id_number',
                        'caller_destination',
                        'other_leg_caller_destination',
                        'network_addr',
                        'other_leg_network_addr',
                        'created_time',
                        'other_leg_created_time',
                        'answered_time',
                        'other_leg_answered_time',
                        'progress_time',
                        'other_leg_progress_time',
                        'progress_media_time',
                        'other_leg_progress_media_time',
                        'hangup_time',
                        'other_leg_hangup_time',
                        'transfer_time',
                        'other_leg_transfer_time',
                        'resurrect_time',
                        'other_leg_resurrect_time',
                        'bridged_time',
                        'other_leg_bridged_time',
                        'last_hold_time',
                        'other_leg_last_hold_time',
                        'hold_accu_time',
                        'other_leg_hold_accu_time',
                        'application',
                        'application_uuid',
                        'application_data',
                        'application_status',
                        'application_file_path',
                        'application_seconds',
                        'transfer_source',
                        'cc_side',
                        'cc_queue',
                        'cc_action',
                        'cc_count',
                        'cc_member_joining_time',
                        'cc_member_leaving_time',
                        'cc_cause',
                        'cc_hangup_cause',
                        'cc_cancel_reason',
                        'cc_member_uuid',
                        'cc_member_session_uuid',
                        'cc_member_caller_id_name',
                        'cc_member_caller_id_number',
                        'cc_agent',
                        'cc_agent_uuid',
                        'cc_agent_system',
                        'cc_agent_type',
                        'cc_agent_state',
                        'cc_agent_called_time',
                        'cc_agent_answered_time',
                        'dtmf_digit',
                        'dtmf_duration',
                        'dtmf_source',
                        'cf_name',
                        'cf_action',
                        'cf_uuid',
                        'cf_domain',
                        'cf_size',
                        'cf_ghosts',
                        'cf_profile_name',
                        'cf_member_type',
                        'cf_member_id'
                ]}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = (
        'hostname', 'event_name', 'event_subclass', 'event_date_local', 'call_uuid',
        'caller_id_number'
        )
    list_filter = ('created', DomainFilter, EventNameListFilter, EventSubclassListFilter)

    ordering = [
        'event_epoch', 'event_sequence'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        if not change:
            obj.domain_id = DomainUtils().domain_from_session(request)
        super().save_model(request, obj, form, change)


admin.site.register(XmlCdr, XmlCdrAdmin)
admin.site.register(CallTimeline, CallTimelineAdmin)
