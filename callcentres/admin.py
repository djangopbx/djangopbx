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

from time import sleep
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect

from .models import (
    CallCentreAgents, CallCentreQueues, CallCentreTiers,
    CallCentreAgentStatusLog, get_agent_contact
)
from dialplans.models import Dialplan
from tenants.models import Profile
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.conf import settings
from django.forms import ModelForm, Select
from switch.switchsounds import SwitchSounds
from pbx.commonwidgets import ListTextWidget
from pbx.commonfunctions import DomainFilter, DomainUtils
from pbx.commondestination import CommonDestAction
from pbx.fseventsocket import EventSocket
from .callcentrefunctions import CcFunctions


class CallCentreTiersResource(resources.ModelResource):
    class Meta:
        model = CallCentreTiers
        import_id_fields = ('id', )


class CallCentreTiersAdmin(ImportExportModelAdmin):
    resource_class = CallCentreTiersResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['queue_id', 'agent_id']
    fieldsets = [
        (None,  {'fields': ['queue_id', 'agent_id', 'tier_level', 'tier_position']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('queue_id', 'agent_id', 'tier_level', 'tier_position')
    list_filter = ()
    ordering = [
        'queue_id','agent_id'
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'agent_id':
            kwargs["queryset"] = CallCentreAgents.objects.filter(domain_id=DomainUtils().domain_from_session(request))
        if db_field.name == 'queue_id':
            kwargs["queryset"] = CallCentreQueues.objects.filter(domain_id=DomainUtils().domain_from_session(request))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)
        self.fire_fs_events(obj, change)

    def delete_model(self, request, obj):
        self.fire_fs_events(obj, False, True)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.fire_fs_events(obj, False, True)
        super().delete_queryset(request, queryset)

    def fire_fs_events(self, obj, change, delete=False):
        ret = True
        s = 0.0001
        es = EventSocket()
        if not es.connect(*settings.EVSKT):
            return False

        if delete:
            # delete the tier
            cmd = 'api callcenter_config tier del %s %s' % (str(obj.queue_id.id), str(obj.agent_id.id))
            result = es.send(cmd)
            if '-ERR' in result:
                ret = False
            return ret

        if not change:
            # add the tier
            cmd = 'api callcenter_config tier add %s %s %s %s' % (str(obj.queue_id.id), str(obj.agent_id.id), str(obj.tier_level), str(obj.tier_position))
            result = es.send(cmd)
            if '-ERR' in result:
                ret = False
            sleep(s)

        # tier set level
        cmd = 'api callcenter_config tier set level %s %s %s' % (str(obj.queue_id.id), str(obj.agent_id.id), str(obj.tier_level))
        result = es.send(cmd)
        if '-ERR' in result:
            ret = False
        sleep(s)

        # tier set position
        cmd = 'api callcenter_config tier set position %s %s %s' % (str(obj.queue_id.id), str(obj.agent_id.id), str(obj.tier_position))
        result = es.send(cmd)
        if '-ERR' in result:
            ret = False
        sleep(s)
        return ret


class CallCentreTiersInLine(admin.TabularInline):
    model = CallCentreTiers
    extra = 2
    fieldsets = [
        (None,          {'fields': ['queue_id', 'agent_id', 'tier_level', 'tier_position']}),
    ]
    ordering = [
        'agent_id'
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'agent_id':
            kwargs["queryset"] = CallCentreAgents.objects.filter(domain_id=DomainUtils().domain_from_session(request))
        if db_field.name == 'queue_id':
            kwargs["queryset"] = CallCentreQueues.objects.filter(domain_id=DomainUtils().domain_from_session(request))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CallCentreAgentsResource(resources.ModelResource):
    class Meta:
        model = CallCentreAgents
        import_id_fields = ('id', )


class CallCentreAgentsAdminForm(ModelForm):

    class Meta:
        model = CallCentreAgents
        exclude = ()
        widgets = {
            "contact": ListTextWidget(choices=[('', 'List unavailable')], attrs={'size': '50'}),
        }


class CallCentreAgentsAdmin(ImportExportModelAdmin):
    resource_class = CallCentreAgentsResource
    form = CallCentreAgentsAdminForm
    save_as = True
    change_list_template = "admin_changelist.html"
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'agent_id']
    fieldsets = [
        (None,  {'fields': ['name', 'user_uuid', 'agent_type', 'call_timeout', 'agent_id',
                            'agent_pin', 'contact', 'status', 'no_answer_delay_time', 'max_no_answer',
                            'wrap_up_time', 'reject_delay_time', 'busy_delay_time', 'domain_id']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'agent_type', 'agent_id', 'contact', 'status')
    list_filter = (DomainFilter, 'status')
    ordering = [
        'name'
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user_uuid':
            kwargs["queryset"] = Profile.objects.filter(domain_id=DomainUtils().domain_from_session(request))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, change=False, **kwargs):
        cda = CommonDestAction(request.session['domain_name'], request.session['domain_uuid'])
        ## this is required for access to the request object so the domain_name session
        ## variable can be passed to the chioces function
        self.form.Meta.widgets['contact'].choices=cda.get_contact_choices()
        return super().get_form(request, obj, change, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        if not change:
            obj.domain_id = DomainUtils().domain_from_session(request)
        super().save_model(request, obj, form, change)
        if self.fire_fs_events(obj, change):
            self.message_user(request, "Callentre Configuration Updated")

    def delete_model(self, request, obj):
        self.fire_fs_events(obj, False, True)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.fire_fs_events(obj, False, True)
        super().delete_queryset(request, queryset)

    def fire_fs_events(self, obj, change, delete=False):
        ret = True
        s = 0.0001
        es = EventSocket()
        if not es.connect(*settings.EVSKT):
            return False

        if delete:
            # delete the agent
            cmd = 'api callcenter_config agent del %s' % str(obj.id)
            result = es.send(cmd)
            if '-ERR' in result:
                ret = False
            return ret

        if not change:
            # add the agent
            cmd = 'api callcenter_config agent add %s %s' % (str(obj.id), obj.agent_type)
            result = es.send(cmd)
            if '-ERR' in result:
                ret = False
            sleep(s)

        # agent set contact
        cmd = 'api callcenter_config agent set contact %s %s' % (str(obj.id), get_agent_contact(obj))
        result = es.send(cmd)
        if '-ERR' in result:
            ret = False
        sleep(s)

        # agent set status
        if obj.status:
            cmd = 'api callcenter_config agent set status %s %s' % (str(obj.id), obj.status)
            result = es.send(cmd)
            if '-ERR' in result:
                ret = False
            sleep(s)

        # agent set reject delay time
        cmd = 'api callcenter_config agent set reject_delay_time %s %s' % (str(obj.id), str(obj.reject_delay_time))
        result = es.send(cmd)
        if '-ERR' in result:
            ret = False
        sleep(s)

        # agent set busy delay time
        cmd = 'api callcenter_config agent set busy_delay_time %s %s' % (str(obj.id), str(obj.busy_delay_time))
        result = es.send(cmd)
        if '-ERR' in result:
            ret = False
        sleep(s)

        # agent set no answer delay time
        cmd = 'api callcenter_config agent set no_answer_delay_time %s %s' % (str(obj.id), str(obj.no_answer_delay_time))
        result = es.send(cmd)
        if '-ERR' in result:
            ret = False
        sleep(s)

        # agent set max no answer
        cmd = 'api callcenter_config agent set max_no_answer %s %s' % (str(obj.id), str(obj.max_no_answer))
        result = es.send(cmd)
        if '-ERR' in result:
            ret = False
        sleep(s)

        # agent set wrap up time
        cmd = 'api callcenter_config agent set wrap_up_time %s %s' % (str(obj.id), str(obj.wrap_up_time))
        result = es.send(cmd)
        if '-ERR' in result:
            ret = False
        sleep(s)
        return ret


class CallCentreQueuesResource(resources.ModelResource):
    class Meta:
        model = CallCentreQueues
        import_id_fields = ('id', )


class CallCentreQueuesAdminForm(ModelForm):

    class Meta:
        model = CallCentreAgents
        exclude = ()
        widgets = {
            "greeting": Select(choices=[('', 'List unavailable')], attrs={'style': 'width:350px'}),
            "moh_sound": Select(choices=[('', 'List unavailable')], attrs={'style': 'width:350px'}),
            "record_template": Select(choices=[('', 'False')]),
            "timeout_action": Select(choices=[('', 'List unavailable')], attrs={'style': 'width:350px'}),
        }


@admin.action(permissions=['change'], description=_('Reload selected Call Centre Queues'))
def cc_queue_reload(modeladmin, request, queryset):
    es = EventSocket()
    if not es.connect(*settings.EVSKT):
        messages.add_message(request, messages.ERR, _('Event Socket Connect Problem'))
        return
    rc = 0
    for obj in queryset:
        cmd = 'api callcenter_config queue reload %s' % str(obj.id)
        result = es.send(cmd)
        if '+OK' in result:
            rc += 1
    if rc > 0:
        messages.add_message(request, messages.INFO, _('%s Queue(s) reloaded.' % rc))


class CallCentreQueuesAdmin(ImportExportModelAdmin):
    resource_class = CallCentreQueuesResource
    form = CallCentreQueuesAdminForm
    save_as = True
    change_form_template = "admin_genhtml_changeform.html"
    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'extension', 'description']
    fieldsets = [
        (None,  {'fields': ['name',
                            'extension',
                            'greeting',
                            'strategy',
                            'moh_sound',
                            'record_template',
                            'time_base_score',
                            'max_wait_time',
                            'max_wait_time_na',
                            'max_wait_time_natr',
                            'timeout_action',
                            'tier_rules_apply',
                            'tier_rule_wait_sec',
                            'tier_rule_wm_level',
                            'tier_rule_nanw',
                            'discard_abndnd_after',
                            'abndnd_resume_allowed',
                            'cid_name_prefix',
                            'announce_sound',
                            'announce_frequency',
                            'cc_exit_keys',
                            'enabled',
                            'description',
                            'domain_id']}),
        ('wallboard settings',   {'fields': ['wb_wait_warn_level', 'wb_wait_crit_level', 'wb_aban_warn_level',
                            'wb_aban_crit_level', 'wb_show_agents', 'wb_agents_per_row'], 'classes': ['collapse']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'extension', 'strategy', 'tier_rules_apply', 'enabled', 'description')
    list_filter = (DomainFilter, 'enabled')
    ordering = [
        'name'
    ]
    inlines = [CallCentreTiersInLine]
    actions = [cc_queue_reload]

    def get_form(self, request, obj=None, change=False, **kwargs):
        ss = SwitchSounds()
        cda = CommonDestAction(request.session['domain_name'], request.session['domain_uuid'])
        ## this is required for access to the request object so the domain_name session
        ## variable can be passed to the chioces function
        self.form.Meta.widgets['greeting'].choices=ss.get_sounds_choices_list(request.session['domain_name'], False, 0b11111110)
        self.form.Meta.widgets['moh_sound'].choices=ss.get_ringback_choices_list(request.session['domain_name'])
        self.form.Meta.widgets['record_template'].choices=ss.get_cc_record(request.session['domain_name'])
        self.form.Meta.widgets['timeout_action'].choices=cda.get_action_choices(':', False, 0b1111111111111110)
        return super().get_form(request, obj, change, **kwargs)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            self.fire_fs_tier_events(obj, change, delete=True)
            obj.delete()
        for instance in instances:
            instance.updated_by = request.user.username
            instance.save()
            self.fire_fs_tier_events(instance, change)
        formset.save_m2m()

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        if not change:
            obj.domain_id = DomainUtils().domain_from_session(request)
        super().save_model(request, obj, form, change)
        self.fire_fs_queue_events(obj, change, False)

    def response_change(self, request, obj):
        if "_generate-xml" in request.POST:
            ccf = CcFunctions(request.session['domain_uuid'], request.session['domain_name'], str(obj.id), request.user.username)
            obj.dialplan_id = ccf.generate_xml()
            obj.save()
            self.message_user(request, "XML Generated")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    def delete_model(self, request, obj):
        if obj.dialplan_id:
            Dialplan.objects.get(pk=obj.dialplan_id).delete()
            self.fire_fs_tier_events(obj, True, True)
            self.fire_fs_queue_events(obj, True, True)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if obj.dialplan_id:
                Dialplan.objects.get(pk=obj.dialplan_id).delete()
                self.fire_fs_tier_events(obj, True, True)
                self.fire_fs_queue_events(obj, True, True)
        super().delete_queryset(request, queryset)

    def fire_fs_tier_events(self, obj, change, delete=False):
        ret = True
        s = 0.0001
        es = EventSocket()
        if not es.connect(*settings.EVSKT):
            return False

        if delete:
            # delete the tier
            cmd = 'api callcenter_config tier del %s %s' % (str(obj.queue_id.id), str(obj.agent_id.id))
            result = es.send(cmd)
            if '-ERR' in result:
                ret = False
            return ret

        # add the tier
        cmd = 'api callcenter_config tier add %s %s %s %s' % (str(obj.queue_id.id), str(obj.agent_id.id), str(obj.tier_level), str(obj.tier_position))
        result = es.send(cmd)
        if not '-ERR Tier already exist' in result:
            if '-ERR' in result:
                ret = False
        sleep(s)

        # tier set level
        cmd = 'api callcenter_config tier set level %s %s %s' % (str(obj.queue_id.id), str(obj.agent_id.id), str(obj.tier_level))
        result = es.send(cmd)
        if '-ERR' in result:
            ret = False
        sleep(s)

        # tier set position
        cmd = 'api callcenter_config tier set position %s %s %s' % (str(obj.queue_id.id), str(obj.agent_id.id), str(obj.tier_position))
        result = es.send(cmd)
        if '-ERR' in result:
            ret = False
        sleep(s)
        return ret

    def fire_fs_queue_events(self, obj, change, delete=False):
        ret = True
        es = EventSocket()
        if not es.connect(*settings.EVSKT):
            return False

        if delete:
            # unload the queue
            cmd = 'api callcenter_config queue unload %s' % str(obj.id)
            result = es.send(cmd)
            if '-ERR' in result:
                ret = False
            return ret

        if not change:
            # load the queue
            cmd = 'api callcenter_config queue load %s' % str(obj.id)
            result = es.send(cmd)
            if '-ERR' in result:
                ret = False

        # reload the queue
        cmd = 'api callcenter_config queue reload %s' % str(obj.id)
        result = es.send(cmd)
        if '-ERR' in result:
            ret = False
        return ret


class CallCentreAgentStatusLogResource(resources.ModelResource):
    class Meta:
        model = CallCentreAgentStatusLog
        import_id_fields = ('id', )


class CallCentreAgentStatusLogAdmin(ImportExportModelAdmin):
    resource_class = CallCentreAgentStatusLogResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['agent_id']
    fieldsets = [
        (None,  {'fields': ['agent_id', 'status']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('created', 'agent_id', 'status')
    list_filter = ('status',)
    ordering = [
        'created','agent_id'
    ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(CallCentreAgents, CallCentreAgentsAdmin)
admin.site.register(CallCentreQueues, CallCentreQueuesAdmin)
admin.site.register(CallCentreAgentStatusLog, CallCentreAgentStatusLogAdmin)

if settings.PBX_ADMIN_SHOW_ALL:
    admin.site.register(CallCentreTiers, CallCentreTiersAdmin)
