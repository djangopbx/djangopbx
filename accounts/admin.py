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
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib import messages
from .models import (
    Extension, FollowMeDestination, ExtensionUser, Gateway,
)
from voicemail.models import Voicemail
from django.forms.widgets import Select
from django.forms import ModelForm
from import_export.admin import ImportExportModelAdmin, ExportMixin
from import_export import resources
from pbx.commonfunctions import DomainFilter, DomainUtils
from musiconhold.musiconholdfunctions import MohSource
from switch.switchfunctions import SipProfileChoice
from .accountfunctions import AccountFunctions


class ExtensionAdminForm(ModelForm):
    class Meta:
        model = Extension
        widgets = {
            "hold_music": Select(choices=MohSource().choices()),
        }
        fields = '__all__'


class GatewayAdminForm(ModelForm):
    class Meta:
        model = Gateway
        widgets = {
            "profile": Select(choices=SipProfileChoice().choices()),
        }
        fields = '__all__'


class ExtensionUserInLine(admin.TabularInline):
    model = ExtensionUser

    extra = 1
    fieldsets = [
        (None,          {'fields': ['user_uuid', 'default_user',]}),
    ]
    ordering = ['user_uuid']


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


class ExtensionAdmin(ImportExportModelAdmin):
    resource_class = ExtensionResource
    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    form = ExtensionAdminForm
    save_on_top = True
    save_as = True

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['extension', 'effective_caller_id_name', 'outbound_caller_id_name', 'effective_caller_id_number', 'outbound_caller_id_number', 'context']

    list_display = ('extension', 'effective_caller_id_name', 'outbound_caller_id_name', 'call_group', 'user_context', 'enabled', 'description')
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

        ('Advanced',   {'fields': ['auth_acl',
                            'cidr',
                            'sip_force_contact',
                            #'nibble_account',
                            'sip_force_expires',
                            'mwi_account',
                            'sip_bypass_media',
                            #'unique_id',
                            'absolute_codec_string',
                            'force_ping',
                            'dial_string',
                ], 'classes': ['collapse']}),

        ('Call Routing',   {'fields': [('forward_all_enabled', 'forward_all_destination'),
                            ('forward_busy_enabled', 'forward_busy_destination'),
                            ('forward_no_answer_enabled', 'forward_no_answer_destination'),
                            ('forward_user_not_registered_enabled', 'forward_user_not_registered_destination'),
                            #'dial_user',
                            #'dial_domain',
                            'forward_caller_id',
                            #'follow_me_uuid',
                            'follow_me_enabled',
                            #'follow_me_destinations',
                            'do_not_disturb',
                ], 'classes': ['collapse']}),

        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    )

    ordering = ['extension']
    inlines = [ExtensionUserInLine, FollowMeDestinationInLine]

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
        if change:
            super().save_model(request, obj, form, change)
        else:
            obj.domain_id = DomainUtils().domain_from_session(request)
            obj.context = request.session['domain_name']
            super().save_model(request, obj, form, change)
            Voicemail.objects.create(
                extension_id = obj,
                enabled = 'false',
                updated_by = request.user.username
            )


class GatewayResource(resources.ModelResource):
    class Meta:
        model = Gateway
        import_id_fields = ('id', )


@admin.action(permissions=['change'], description='Write gateway.conf.xml file')
def write_gateway_file(modeladmin, request, queryset):
    rc = 0
    for obj in queryset:
        r = AccountFunctions().write_gateway_xml(obj)
        if r > 0:
            rc += r
    if rc > 0:
        messages.add_message(request, messages.INFO, _('%s gateway file(s) written.' % rc))
    if r == -1:
        messages.add_message(request, messages.WARN, _('Default setting does not exist: switch->conf'))
    if r == -2:
        messages.add_message(request, messages.WARN, _('Configuration directory does not exist.'))
    if r == -3:
        messages.add_message(request, messages.WARN, _('Error writing to file.'))


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

        ('Advanced',   {'fields': ['distinct_to',
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
    actions = [write_gateway_file]


    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        if not change:
            obj.domain_id = DomainUtils().domain_from_session(request)
        super().save_model(request, obj, form, change)



admin.site.register(Extension, ExtensionAdmin)
admin.site.register(Gateway, GatewayAdmin)
