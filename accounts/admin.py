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

from time import sleep
from django.contrib.auth.base_user import BaseUserManager
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.cache import cache
from django.contrib import messages
from .models import (
    Extension, FollowMeDestination, ExtensionUser, Gateway, Bridge,
)
from tenants.models import Profile
from django.forms.widgets import Select
from django.forms import ModelForm
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from pbx.commonfunctions import DomainFilter, DomainUtils
from musiconhold.musiconholdfunctions import MohSource
from switch.switchfunctions import SipProfileChoice
from .accountfunctions import AccountFunctions, GatewayFunctions, ExtRelatedFunctions
from .extensionfunctions import ExtFeatureSyncFunctions
from voicemail.voicemailfunctions import VoicemailFunctions


class ExtensionAdminForm(ModelForm):
    class Meta:
        model = Extension
        widgets = {
            "hold_music": Select(choices=[('None', 'None')]),
        }
        fields = '__all__'


class GatewayAdminForm(ModelForm):
    class Meta:
        model = Gateway
        widgets = {
            "profile": Select(choices=[('None', 'None')]),
        }
        fields = '__all__'


class ExtensionUserResource(resources.ModelResource):
    class Meta:
        model = ExtensionUser
        import_id_fields = ('id', )


class ExtensionUserAdmin(ImportExportModelAdmin):
    resource_class = ExtensionUserResource
    save_as = True

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['user_uuid']

    list_display = ('user_uuid', 'default_user')
    list_filter = ('default_user',)

    fieldsets = (
        (None,  {'fields': ['user_uuid', 'default_user']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    )

    ordering = ['user_uuid']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user_uuid':
            kwargs["queryset"] = Profile.objects.filter(domain_id=DomainUtils().domain_from_session(request))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class ExtensionUserInLine(admin.TabularInline):
    model = ExtensionUser

    extra = 1
    fieldsets = [
        (None,          {'fields': ['user_uuid', 'default_user',]}),
    ]
    ordering = ['user_uuid']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user_uuid':
            kwargs["queryset"] = Profile.objects.filter(domain_id=DomainUtils().domain_from_session(request))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class FollowMeDestinationResource(resources.ModelResource):
    class Meta:
        model = FollowMeDestination
        import_id_fields = ('id', )


class FollowMeDestinationAdmin(ImportExportModelAdmin):
    resource_class = FollowMeDestinationResource
    save_as = True

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['destination']

    list_display = ('destination', 'delay', 'timeout', 'prompt')
    list_filter = ('delay', 'timeout', 'prompt')

    fieldsets = (
        (None,  {'fields': ['extension_id', 'destination', 'delay', 'timeout', 'prompt']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    )

    ordering = ['destination']

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class FollowMeDestinationInLine(admin.TabularInline):
    model = FollowMeDestination

    extra = 4
    fieldsets = [
        (None,          {'fields': ['destination', 'delay', 'timeout', 'prompt']}),
    ]
    ordering = ['destination']


class ExtensionResource(resources.ModelResource):
    class Meta:
        model = Extension
        import_id_fields = ('id', )


@admin.action(permissions=['change'], description=_('Create User for selected extensions'))
def create_user_for_extension(modeladmin, request, queryset):
    rc = 0
    extrf = ExtRelatedFunctions()
    for obj in queryset:
        r = extrf.create_user(obj, request)
        if r > 0:
            rc += r
    if rc > 0:
        messages.add_message(request, messages.INFO, _('%s user(s) created.' % rc))


@admin.action(permissions=['change'], description=_('Create Device for selected extensions'))
def create_device_for_extension(modeladmin, request, queryset):
    rc = 0
    extrf = ExtRelatedFunctions()
    for obj in queryset:
        r = extrf.create_device(obj, request)
        if r > 0:
            rc += r
    if rc > 0:
        messages.add_message(request, messages.INFO, _('%s device(s) created.' % rc))


class ExtensionAdmin(ImportExportModelAdmin):
    resource_class = ExtensionResource

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    form = ExtensionAdminForm
    save_on_top = True
    save_as = True
    change_list_template = "admin_changelist.html"

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = [
                        'extension', 'effective_caller_id_name', 'outbound_caller_id_name',
                        'effective_caller_id_number', 'outbound_caller_id_number', 'context'
                    ]

    list_display = (
                    'extension', 'effective_caller_id_name', 'outbound_caller_id_name',
                    'call_group', 'user_context', 'enabled', 'description'
                    )

    list_filter = (DomainFilter, 'toll_allow', 'call_group', 'user_context', 'enabled')

    fieldsets = (
        (None,  {'fields': ['extension',
                            'number_alias',
                            'domain_id',
                            'password',
                            'accountcode',
                            ('effective_caller_id_name', 'effective_caller_id_number'),
                            ('outbound_caller_id_name',   'outbound_caller_id_number'),
                            ('emergency_caller_id_name',  'emergency_caller_id_number'),
                            ('directory_first_name',      'directory_last_name'),
                            'directory_visible',
                            'directory_exten_visible',
                            ('limit_max',                 'limit_destination'),
                            ('missed_call_app',           'missed_call_data'),
                            'toll_allow',
                            'call_timeout',
                            'call_group',
                            'call_screen_enabled',
                            'user_record',
                            'hold_music',
                            'user_context',
                            'enabled',
                            'description',
                            ]}),

        ('Advanced',    {'fields': ['auth_acl',
                                    'cidr',
                                    'sip_force_contact',
                                    # 'nibble_account',
                                    'sip_force_expires',
                                    'mwi_account',
                                    'sip_bypass_media',
                                    # 'unique_id',
                                    'absolute_codec_string',
                                    'force_ping',
                                    'dial_string',
                                    ], 'classes': ['collapse']}),

        ('Call Routing',    {'fields': [('forward_all_enabled', 'forward_all_destination'),
                                        ('forward_busy_enabled', 'forward_busy_destination'),
                                        ('forward_no_answer_enabled', 'forward_no_answer_destination'),
                                        ('forward_user_not_registered_enabled',
                                            'forward_user_not_registered_destination'),
                                        # 'dial_user',
                                        # 'dial_domain',
                                        'forward_caller_id',
                                        # 'follow_me_uuid',
                                        'follow_me_enabled',
                                        # 'follow_me_destinations',
                                        'do_not_disturb',
                                        ], 'classes': ['collapse']}),

        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    )

    ordering = ['extension']
    actions = [create_user_for_extension, create_device_for_extension]
    inlines = [ExtensionUserInLine, FollowMeDestinationInLine]

    def get_form(self, request, obj=None, change=False, **kwargs):
        self.form.Meta.widgets['hold_music'].choices = MohSource().choices()
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields['password'].initial = BaseUserManager().make_random_password(12)
        return form

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            instance.updated_by = request.user.username
            instance.save()
        formset.save_m2m()

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        directory_cache_key = 'directory:%s@%s' % (obj.extension, request.session['domain_name'])
        cache.delete(directory_cache_key)
        if change:
            super().save_model(request, obj, form, change)
            efsf = ExtFeatureSyncFunctions(obj)
            efsf.sync_dnd()
            efsf.es_disconnect()
            # Uncomment as required below if you have any of the following
            # feature on/off codes programmed in your phones.
            # If you exclusively use TCP transport and have no concern about exceeding your MTU
            # You may also opt for using efsf.sync_all()
            #
            #efsf.sync_fwd_immediate()
            #efsf.sync_fwd_busy()
            #efsf.sync_fwd_no_answer()
            #efsf.sync_all()
        else:
            obj.domain_id = DomainUtils().domain_from_session(request)
            obj.user_context = request.session['domain_name']
            super().save_model(request, obj, form, change)
            VoicemailFunctions().create_vm_record(obj, request.user.username)


class GatewayResource(resources.ModelResource):
    class Meta:
        model = Gateway
        import_id_fields = ('id', )


@admin.action(permissions=['change'], description=_('Write static gateway.conf.xml file'))
def write_gateway_file(modeladmin, request, queryset):
    rc = 0
    for obj in queryset:
        r = AccountFunctions().write_gateway_xml(obj)
        if r > 0:
            rc += r
    if rc > 0:
        messages.add_message(request, messages.INFO, _('%s gateway file(s) written.' % rc))
    if r == -1:
        messages.add_message(request, messages.WARNING, _('Default setting does not exist: switch->conf'))
    if r == -2:
        messages.add_message(request, messages.WARNING, _('Configuration directory does not exist.'))
    if r == -3:
        messages.add_message(request, messages.WARNING, _('Error writing to file.'))


@admin.action(permissions=['change'], description=_('Reload gateway profile'))
def rescan_sofia_profile(modeladmin, request, queryset):
    rc = 0
    current_profile = ''
    gf = GatewayFunctions()
    for obj in queryset:
        if not current_profile == obj.profile:
            current_profile = obj.profile
            r = gf.rescan_sofia_profile(obj.profile)
            if r > 0:
                rc += r
    gf.es_disconnect()
    if rc > 0:
        messages.add_message(request, messages.INFO, _('%s gateway profil(s) rescanned.' % rc))
    if r == -1:
        messages.add_message(request, messages.WARNING, _('Event Socket Error'))


@admin.action(permissions=['change'], description=_('Stop gateway'))
def sofia_stop_gateway(modeladmin, request, queryset):
    rc = 0
    gf = GatewayFunctions()
    for obj in queryset:
        r = gf.sofia_stop_gateway(obj.profile, str(obj.id))
        sleep(0.1)
        if r > 0:
            rc += r
    gf.es_disconnect()
    if rc > 0:
        messages.add_message(request, messages.INFO, _('%s gateway(s) stopped.' % rc))
    if r == -1:
        messages.add_message(request, messages.WARNING, _('Event Socket Error'))


class GatewayAdmin(ImportExportModelAdmin):
    resource_class = GatewayResource
    form = GatewayAdminForm
    save_as = True

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['gateway', 'from_domain', 'proxy', 'realm', 'description']

    list_display = ('gateway', 'context', 'hostname', 'enabled', 'description')
    list_filter = (DomainFilter, 'from_domain', 'proxy', 'realm', 'enabled')

    fieldsets = (
        (None,  {'fields': ['gateway',
                            'username',
                            'password',
                            'domain_id',
                            'from_user',
                            'from_domain',
                            'proxy',
                            'realm',
                            'expire_seconds',
                            'register',
                            'retry_seconds',
                            'context',
                            'profile',
                            'enabled',
                            'description',
                            ]}),

        ('Advanced',    {'fields': ['distinct_to',
                                    'auth_username',
                                    'extension',
                                    'register_transport',
                                    'register_proxy',
                                    'outbound_proxy',
                                    'caller_id_in_from',
                                    'supress_cng',
                                    'sip_cid_type',
                                    'codec_prefs',
                                    'extension_in_contact',
                                    'ping',
                                    'channels',
                                    'hostname',
                                    ], 'classes': ['collapse']}),

        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    )

    ordering = ['gateway']
    actions = [write_gateway_file, rescan_sofia_profile, sofia_stop_gateway]

    def get_form(self, request, obj=None, change=False, **kwargs):
        self.form.Meta.widgets['profile'].choices = SipProfileChoice().choices()
        return super().get_form(request, obj, change, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        if not change:
            obj.domain_id = DomainUtils().domain_from_session(request)
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        gf = GatewayFunctions()
        gf.sofia_stop_gateway(obj.profile, str(obj.id))
        gf.es_disconnect()
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        gf = GatewayFunctions()
        for obj in queryset:
            gf.sofia_stop_gateway(obj.profile, str(obj.id))
            sleep(0.1)
        gf.es_disconnect()
        super().delete_queryset(request, queryset)


class BridgeResource(resources.ModelResource):
    class Meta:
        model = Bridge
        import_id_fields = ('id', )


class BridgeAdmin(ImportExportModelAdmin):
    resource_class = BridgeResource
    save_as = True

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'destination', 'description']

    list_display = ('name', 'destination', 'enabled', 'description')
    list_filter = (DomainFilter, 'enabled')

    fieldsets = (
        (None,  {'fields': ['name', 'destination', 'enabled', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    )

    ordering = ['name']

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        if not change:
            obj.domain_id = DomainUtils().domain_from_session(request)
        super().save_model(request, obj, form, change)


admin.site.register(Extension, ExtensionAdmin)
admin.site.register(Gateway, GatewayAdmin)
admin.site.register(Bridge, BridgeAdmin)

if settings.PBX_ADMIN_SHOW_ALL:
    admin.site.register(ExtensionUser, ExtensionUserAdmin)
    admin.site.register(FollowMeDestination, FollowMeDestinationAdmin)
