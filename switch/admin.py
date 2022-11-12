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

from django.db import models
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib import messages
from .models import (
    SipProfile, SipProfileSetting, SipProfileDomain, SwitchVariable, AccessControl, AccessControlNode,
)
from import_export.admin import ImportExportModelAdmin, ExportMixin
from import_export import resources
from switch.switchfunctions import SwitchFunctions
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME

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


class SipProfileDomainInLine(admin.TabularInline):
    model = SipProfileDomain
    classes = ['collapse']
    extra = 1
    fieldsets = [
        (None,          {'fields': ['name', 'alias', 'parse' ]}),
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


class SipProfileSettingInLine(admin.TabularInline):
    model = SipProfileSetting
    classes = ['collapse']
    extra = 1
    fieldsets = [
        (None,          {'fields': ['name', 'value', 'enabled', 'description' ]}),
    ]
    ordering = [
        'name'
    ]


class SipProfileResource(resources.ModelResource):
    class Meta:
        model = SipProfile
        import_id_fields = ('id', )


class SipProfileAdmin(ImportExportModelAdmin):
    resource_class = SipProfileResource
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


class SwitchVariableResource(resources.ModelResource):
    class Meta:
        model = SwitchVariable
        import_id_fields = ('id', )


@admin.action(permissions=['change'], description='Write Switch vars.xml file')
def write_switch_vars_file(modeladmin, request, queryset):
    r = SwitchFunctions().save_var_xml()
    if r == 0:
        messages.add_message(request, messages.INFO, _('vars.xml file written'))
    if r == 1:
        messages.add_message(request, messages.WARN, _('Default setting does not exist:') + ' switch->conf')
    if r == 2:
        messages.add_message(request, messages.WARN, _('Configuration directory does not exist:'))


class SwitchVariableAdmin(ImportExportModelAdmin):
    resource_class = SwitchVariableResource
    save_as = True
    readonly_fields = ['name', 'created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['category', 'name', 'value', 'descrption']
    fieldsets = [
        (None,  {'fields': ['category', 'name', 'value', 'command', 'hostname', 'enabled', 'sequence', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('category', 'name', 'value', 'hostname', 'enabled', 'description')
    list_filter = ('category', 'enabled')

    ordering = [
        'category', 'sequence', 'name'
    ]

    actions = [write_switch_vars_file]

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
        (None,          {'fields': ['type', 'cidr', 'domain', 'description' ]}),
    ]
    ordering = [
        'description'
    ]


class AccessControlResource(resources.ModelResource):
    class Meta:
        model = AccessControl
        import_id_fields = ('id', )


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



admin.site.register(SipProfile, SipProfileAdmin)
admin.site.register(SipProfileSetting, SipProfileSettingAdmin)
admin.site.register(SipProfileDomain, SipProfileDomainAdmin)
admin.site.register(SwitchVariable, SwitchVariableAdmin)
admin.site.register(AccessControl, AccessControlAdmin)

