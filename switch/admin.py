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
from django.conf import settings

from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from .models import (
    SipProfile, SipProfileSetting, SipProfileDomain, SwitchVariable,
    AccessControl, AccessControlNode, EmailTemplate, Modules, IpRegister,
)
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from switch.switchfunctions import SwitchFunctions
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from pbx.commonfunctions import shcommand
from pbx.amqpcmdevent import AmqpCmdEvent
from .ipregisterfunctions import IpRegisterFunctions


class SipProfileDomainResource(resources.ModelResource):

    class Meta:
        model = SipProfileDomain
        import_id_fields = ('id', )


class SipProfileDomainAdmin(ImportExportModelAdmin):
    resource_class = SipProfileDomainResource
    readonly_fields = ['name', 'created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'alias', 'parse']
    fieldsets = [
        (None,  {'fields': ['sip_profile_id', 'name', 'alias', 'parse']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'alias', 'parse')
    list_filter = ('sip_profile_id', )
    ordering = [
        'name'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class SipProfileDomainInLine(admin.TabularInline):
    model = SipProfileDomain
    classes = ['collapse']
    extra = 1
    fieldsets = [
        (None,          {'fields': ['name', 'alias', 'parse']}),
    ]
    ordering = [
        'name'
    ]


class SipProfileSettingResource(resources.ModelResource):

    class Meta:
        model = SipProfileSetting
        import_id_fields = ('id', )


class SipProfileSettingAdmin(ImportExportModelAdmin):
    resource_class = SipProfileSettingResource
    readonly_fields = ['name', 'created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'value', 'description']
    fieldsets = [
        (None,  {'fields': ['sip_profile_id', 'name', 'value', 'enabled', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'value', 'enabled', 'description')
    list_filter = ('sip_profile_id', 'enabled')
    ordering = [
        'name'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class SipProfileSettingInLine(admin.TabularInline):
    model = SipProfileSetting
    classes = ['collapse']
    extra = 2
    fieldsets = [
        (None,          {'fields': ['name', 'value', 'enabled', 'description']}),
    ]
    ordering = [
        'name'
    ]


class SipProfileResource(resources.ModelResource):

    class Meta:
        model = SipProfile
        import_id_fields = ('id', )


@admin.action(permissions=['change'], description='Write Sip profile files')
def write_sip_profile_files(modeladmin, request, queryset):
    r = SwitchFunctions().write_sip_profiles()
    if r == 0:
        messages.add_message(request, messages.INFO, _('sip profile files written.'))
    if r == 1:
        messages.add_message(request, messages.WARNING, _('Default setting does not exist:') + ' switch->sip_profiles')
    if r == 2:
        messages.add_message(request, messages.WARNING, _('Configuration directory could not be created.'))
    if r == 3:
        messages.add_message(request, messages.WARNING, _('Error writing to file.'))


class SipProfileAdmin(ImportExportModelAdmin):
    resource_class = SipProfileResource
    save_as = True

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    readonly_fields = ['name', 'created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'hostname', 'descrption']
    fieldsets = [
        (None,  {'fields': ['name', 'hostname', 'enabled', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'hostname', 'enabled', 'description')
    ordering = [
        'name'
    ]
    inlines = [SipProfileDomainInLine, SipProfileSettingInLine]
    actions = [write_sip_profile_files]

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
        super().save_model(request, obj, form, change)

    # This is a workaround to allow the admin action to be run without selecting any objects.
    # super checks for a valid UUID, so we pass a meaningless one because it is not actually used.
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and request.POST['action'] == 'write_sip_profile_files':
            post = request.POST.copy()
            post.update({ACTION_CHECKBOX_NAME: 'eb30bc83-ccb8-4f27-a1d6-9340ae7de325'})
            request._set_post(post)
        return super(SipProfileAdmin, self).changelist_view(request, extra_context)


class SwitchVariableResource(resources.ModelResource):

    class Meta:
        model = SwitchVariable
        import_id_fields = ('id', )


@admin.action(permissions=['change'], description='Write Switch vars.xml file')
def write_switch_vars_file(modeladmin, request, queryset):
    r = SwitchFunctions().save_var_xml()
    if r == 0:
        messages.add_message(request, messages.INFO, _('vars.xml file written.'))
    if r == 1:
        messages.add_message(request, messages.WARNING, _('Default setting does not exist:') + ' switch->conf')
    if r == 2:
        messages.add_message(request, messages.WARNING, _('Configuration directory does not exist.'))
    if r == 3:
        messages.add_message(request, messages.WARNING, _('Error writing to file.'))


class SwitchVariableAdmin(ImportExportModelAdmin):
    resource_class = SwitchVariableResource
    save_as = True
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['category', 'name', 'value', 'descrption']
    fieldsets = [
        (None,  {'fields': [
            'category', 'name', 'value', 'command', 'hostname', 'enabled', 'sequence', 'description'
            ]}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('category', 'name', 'value', 'hostname', 'enabled', 'description')
    list_filter = ('category', 'enabled')

    ordering = [
        'category', 'sequence', 'name'
    ]

    actions = [write_switch_vars_file]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)

    # This is a workaround to allow the admin action to be run without selecting any objects.
    # super checks for a valid UUID, so we pass a meaningless one because it is not actually used.
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and request.POST['action'] == 'write_switch_vars_file':
            post = request.POST.copy()
            post.update({ACTION_CHECKBOX_NAME: 'eb30bc83-ccb8-4f27-a1d6-9340ae7de325'})
            request._set_post(post)
        return super(SwitchVariableAdmin, self).changelist_view(request, extra_context)


class AccessControlNodeInLine(admin.TabularInline):
    model = AccessControlNode
    extra = 1
    fieldsets = [
        (None,          {'fields': ['type', 'cidr', 'domain', 'description']}),
    ]
    ordering = [
        'description'
    ]


class AccessControlResource(resources.ModelResource):

    class Meta:
        model = AccessControl
        import_id_fields = ('id', )


@admin.action(permissions=['change'], description='Write acl.conf.xml file')
def write_acl_file(modeladmin, request, queryset):
    r = SwitchFunctions().write_acl_xml()
    if r == 0:
        messages.add_message(request, messages.INFO, _('acl.conf.xml file written.'))
    if r == 1:
        messages.add_message(request, messages.WARNING, _('Default setting does not exist:') + ' switch->conf')
    if r == 2:
        messages.add_message(request, messages.WARNING, _('Configuration directory does not exist.'))
    if r == 3:
        messages.add_message(request, messages.WARNING, _('Error writing to file.'))


class AccessControlAdmin(ImportExportModelAdmin):
    resource_class = AccessControlResource

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'default', 'descrption']
    fieldsets = [
        (None,  {'fields': ['name', 'default', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'default', 'description')
    ordering = [
        'name'
    ]
    inlines = [AccessControlNodeInLine]
    actions = [write_acl_file]

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
        super().save_model(request, obj, form, change)

    # This is a workaround to allow the admin action to be run without selecting any objects.
    # super checks for a valid UUID, so we pass a meaningless one because it is not actually used.
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and request.POST['action'] == 'write_acl_file':
            post = request.POST.copy()
            post.update({ACTION_CHECKBOX_NAME: 'eb30bc83-ccb8-4f27-a1d6-9340ae7de325'})
            request._set_post(post)
        return super(AccessControlAdmin, self).changelist_view(request, extra_context)


class EmailTemplateResource(resources.ModelResource):

    class Meta:
        model = EmailTemplate
        import_id_fields = ('id', )


class EmailTemplateAdmin(ImportExportModelAdmin):
    resource_class = EmailTemplateResource

    save_as = True
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['language', 'category', 'subcategory', 'descrption']
    fieldsets = [
        (None,  {'fields': [
                'domain_id', 'language', 'category', 'subcategory', 'subject', 'type', 'body', 'enabled',
                'description'
                ]}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('language', 'category', 'subcategory', 'subject', 'type', 'enabled', 'description')
    list_filter = ('domain_id', 'language', 'category', 'type', 'enabled')

    ordering = [
        'language', 'category', 'subcategory',
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class ModulesResource(resources.ModelResource):

    class Meta:
        model = Modules
        import_id_fields = ('id', )


@admin.action(permissions=['change'], description='Write Switch moduls.conf.xml file')
def write_switch_modules_file(modeladmin, request, queryset):
    r = SwitchFunctions().save_modules_xml()
    if r == 0:
        messages.add_message(request, messages.INFO, _('modules.conf.xml file written.'))
    if r == 1:
        messages.add_message(request, messages.WARNING, _('Default setting does not exist:') + ' switch->conf')
    if r == 2:
        messages.add_message(request, messages.WARNING, _('Configuration directory does not exist.'))
    if r == 3:
        messages.add_message(request, messages.WARNING, _('Error writing to file.'))


class ModulesAdmin(ImportExportModelAdmin):
    resource_class = ModulesResource
    save_as = True
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['category', 'name', 'category', 'description']
    fieldsets = [
        (None,  {'fields': ['category', 'label', 'sequence', 'name', 'enabled', 'default_enabled', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('category', 'label', 'name', 'sequence', 'enabled', 'default_enabled', 'description')
    list_filter = ('category', 'enabled', 'default_enabled')

    ordering = [
        'category', 'sequence', 'name'
    ]

    actions = [write_switch_modules_file]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)

    # This is a workaround to allow the admin action to be run without selecting any objects.
    # super checks for a valid UUID, so we pass a meaningless one because it is not actually used.
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and request.POST['action'] == 'write_switch_modules_file':
            post = request.POST.copy()
            post.update({ACTION_CHECKBOX_NAME: 'cc30bc83-ccb8-4f27-a1d6-9340ae7de325'})
            request._set_post(post)
        return super(ModulesAdmin, self).changelist_view(request, extra_context)


class IpRegisterResource(resources.ModelResource):
    class Meta:
        model = IpRegister
        import_id_fields = ('id', )


@admin.action(permissions=['change'], description='Re-instate SIP Customer Firewall List')
def reinstate_sip_customer_list(modeladmin, request, queryset):
    iprf = IpRegisterFunctions()
    iprf.reinstate_fw_sip_customer_list()


class IpRegisterAdmin(ImportExportModelAdmin):
    resource_class = IpRegisterResource
    save_as = True

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['address']
    fieldsets = [
        (None,  {'fields': ['address', 'status']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('address', 'status', 'created', 'updated')
    list_filter = ('status', )
    ordering = [
        'address'
    ]

    actions = [reinstate_sip_customer_list]
    firewall_event_template = '{\"Event-Name\":\"FIREWALL\", \"Action\":\"%s\", \"IP-Type\":\"%s\",\"Fw-List\":\"sip-customer\", \"IP-Address\":\"%s\"}' # noqa: E501

    # This is a workaround to allow the admin action to be run without selecting any objects.
    # super checks for a valid UUID, so we pass a meaningless one because it is not actually used.
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and request.POST['action'] == 'reinstate_sip_customer_list':
            post = request.POST.copy()
            post.update({ACTION_CHECKBOX_NAME: 'dd30bc83-ccb8-4f27-a1d6-9340ae7de325'})
            request._set_post(post)
        return super(IpRegisterAdmin, self).changelist_view(request, extra_context)

    def connect_broker(self):
        broker = AmqpCmdEvent()
        broker.connect()
        return broker

    def fw_update(self, broker, action, ip_address):
        ip_type = 'ipv4'
        if ':' in ip_address:
            ip_type = 'ipv6'
        shcommand(['/usr/local/bin/fw-%s-%s-sip-customer-list.sh' % (action, ip_type), ip_address])
        routing = 'DjangoPBX.%s.FIREWALL.%s.%s' % (broker.hostname, action, ip_type)
        payload = self.firewall_event_template % (action, ip_type, ip_address)
        broker.adhoc_publish(payload, routing, 'TAP.Firewall')
        return

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        if change:
            messages.add_message(request, messages.WARNING, _('A changed IP will not be added to Firewall automatically'))
        else:
            broker = self.connect_broker()
            self.fw_update(broker, 'add', obj.address)
            broker.disconnect()
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        broker = self.connect_broker()
        self.fw_update(broker, 'delete', obj.address)
        broker.disconnect()
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        broker = self.connect_broker()
        for obj in queryset:
            self.fw_update(broker, 'delete', obj.address)
        broker.disconnect()
        super().delete_queryset(request, queryset)


admin.site.register(SipProfile, SipProfileAdmin)
admin.site.register(SwitchVariable, SwitchVariableAdmin)
admin.site.register(AccessControl, AccessControlAdmin)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(Modules, ModulesAdmin)
admin.site.register(IpRegister, IpRegisterAdmin)
if settings.PBX_ADMIN_SHOW_ALL:
    admin.site.register(SipProfileSetting, SipProfileSettingAdmin)
    admin.site.register(SipProfileDomain, SipProfileDomainAdmin)
