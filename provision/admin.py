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
from django.urls import resolve
from .models import (
    DeviceVendors, DeviceVendorFunctions, DeviceVendorFunctionGroups,
    DeviceProfiles, DeviceProfileSettings, DeviceProfileKeys,
    Devices, DeviceLines, DeviceKeys, DeviceSettings,
    )
from tenants.models import Profile
from .forms import DeviceForm, DeviceLinesForm, DeviceKeysForm

from django.conf import settings
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from pbx.commonfunctions import DomainFilter, DomainUtils
from .provisionfunctions import ProvisionFunctions, DeviceVendorFunctionChoice


class DeviceVendorFunctionsInLine(admin.TabularInline):
    model = DeviceVendorFunctions
    extra = 10
    fieldsets = [
        (None,          {'fields': ['name', 'value', 'description', 'enabled']}),
    ]
    ordering = [
        'name'
    ]


class DeviceVendorsResource(resources.ModelResource):
    class Meta:
        model = DeviceVendors
        import_id_fields = ('id', )


class DeviceVendorsAdmin(ImportExportModelAdmin):
    resource_class = DeviceVendorsResource

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['digits', 'action', 'data']
    fieldsets = [
        (None,  {'fields': ['name', 'description', 'enabled']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'description', 'enabled')
    list_filter = ('name', 'enabled')
    ordering = [
        'name'
    ]
    inlines = [DeviceVendorFunctionsInLine]

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


class DeviceVendorFunctionsResource(resources.ModelResource):
    class Meta:
        model = DeviceVendorFunctions
        import_id_fields = ('id', )


class DeviceVendorFunctionsAdmin(ImportExportModelAdmin):
    resource_class = DeviceVendorFunctionsResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'value', 'description']
    fieldsets = [
        (None,  {'fields': ['vendor_id', 'name', 'value', 'description', 'enabled']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'value', 'description', 'enabled')
    list_filter = ('name', 'value', 'enabled')
    ordering = [
        'vendor_id', 'name'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class DeviceVendorFunctionGroupsResource(resources.ModelResource):
    class Meta:
        model = DeviceVendorFunctionGroups
        import_id_fields = ('id', )


class DeviceVendorFunctionGroupsAdmin(ImportExportModelAdmin):
    resource_class = DeviceVendorFunctionGroupsResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['function_id', 'group_id']
    fieldsets = [
        (None,  {'fields': ['function_id', 'group_id']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('function_id', 'group_id')
    list_filter = ('function_id', 'group_id')
    ordering = [
        'function_id', 'group_id'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class DeviceProfileKeysInLine(admin.TabularInline):
    model = DeviceProfileKeys
    extra = 2

    form = DeviceKeysForm
    fieldsets = [
        (None,          {'fields': ['category', 'key_id', 'key_type', 'line', 'value', 'extension', 'label', 'icon']}),
    ]
    ordering = [
        'key_id'
    ]


class DeviceProfileSettingsInLine(admin.TabularInline):
    model = DeviceProfileSettings
    extra = 2
    fieldsets = [
        (None,          {'fields': ['name', 'value', 'description', 'enabled']}),
    ]
    ordering = [
        'name'
    ]



class DeviceProfilesResource(resources.ModelResource):
    class Meta:
        model = DeviceProfiles
        import_id_fields = ('id', )


class DeviceProfilesAdmin(ImportExportModelAdmin):
    resource_class = DeviceProfilesResource
    save_as = True

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'description']
    fieldsets = [
        (None,  {'fields': ['name', 'vendor', 'domain_id', 'enabled', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'description', 'enabled')
    list_filter = (DomainFilter, 'enabled')
    ordering = [
        'domain_id', 'name'
    ]
    #inlines = [DeviceProfileKeysInLine, DeviceProfileSettingsInLine]
    # Only show inlines once the device record has been created, then we know who the vendor is...
    def get_inlines(self, request, obj=None):
        if obj:
            return (DeviceProfileKeysInLine, DeviceProfileSettingsInLine)
        else:
            return ()

    def get_formsets_with_inlines(self, request, obj=None):
        if obj:
            dvfchoices = DeviceVendorFunctionChoice().choices(obj.vendor)
        else:
            dvfchoices = DeviceVendorFunctionChoice().choices()
        for inline in self.get_inline_instances(request, obj):
            if type(inline) is DeviceProfileKeysInLine:
                inline.form.Meta.widgets['key_type'].choices = dvfchoices
                yield inline.get_formset(request, obj), inline

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
        if not change:
            obj.domain_id = DomainUtils().domain_from_session(request)
        super().save_model(request, obj, form, change)


class DeviceProfileSettingsResource(resources.ModelResource):
    class Meta:
        model = DeviceProfileSettings
        import_id_fields = ('id', )


class DeviceProfileSettingsAdmin(ImportExportModelAdmin):
    resource_class = DeviceProfileSettingsResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'value', 'description']
    fieldsets = [
        (None,  {'fields': ['profile_id', 'name', 'value', 'description', 'enabled']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'value', 'description', 'enabled')
    list_filter = ('name', 'value', 'enabled')
    ordering = [
        'profile_id', 'name'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class DeviceProfileKeysResource(resources.ModelResource):
    class Meta:
        model = DeviceProfileKeys
        import_id_fields = ('id', )


class DeviceProfileKeysAdmin(ImportExportModelAdmin):
    resource_class = DeviceProfileKeysResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['value', 'extension', 'label']
    fieldsets = [
        (None,  {'fields': ['profile_id', 'category', 'key_id', 'key_type', 'line', 'value', 'extension',
            'protected', 'label', 'icon']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('category', 'key_id', 'key_type', 'line', 'value', 'label')
    list_filter = ('value', 'extension', 'label')
    ordering = [
        'key_id'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class DeviceLinesInLine(admin.TabularInline):
    model = DeviceLines
    extra = 1

    form = DeviceLinesForm
    fieldsets = [
        (None,          {'fields': ['line_number', 'server_address',
                    'server_address_primary', 'server_address_secondary',
                    'outbound_proxy_primary', 'outbound_proxy_secondary',
                    'display_name', 'user_id', 'auth_id', 'password',
                    'sip_port', 'sip_transport', 'register_expires', 'shared_line',
                    'enabled']}),
    ]
    ordering = [
        'line_number'
    ]


class DeviceKeysInLine(admin.TabularInline):
    model = DeviceKeys
    extra = 0

    form = DeviceKeysForm
    fieldsets = [
        (None,          {'fields': ['category', 'key_id', 'key_type', 'line', 'value', 'extension', 'label', 'icon']}),
    ]
    ordering = [
        'key_id'
    ]


class DeviceSettingsInLine(admin.TabularInline):
    model = DeviceSettings
    extra = 0
    fieldsets = [
        (None,          {'fields': ['name', 'value', 'description', 'enabled']}),
    ]
    ordering = [
        'name'
    ]


class DevicesResource(resources.ModelResource):
    class Meta:
        model = Devices
        import_id_fields = ('id', )


class DevicesAdmin(ImportExportModelAdmin):
    resource_class = DevicesResource
    save_as = True

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    form = DeviceForm
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['mac_address', 'label', 'model', 'template']
    fieldsets = [
        (None,  {'fields': [ 'mac_address', 'label', 'model',
                    'template', 'profile_id', 'user_id', ('username', 'password'),
                    'vendor', 'domain_id', 'enabled', 'description']}),
        ('provision Info',  {'fields': ['firmware_version', 'provisioned_date', 'provisioned_method', 'provisioned_ip'], 'classes': ['collapse']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('mac_address', 'label', 'template', 'profile_id', 'enabled', 'provisioned_date', 'provisioned_method', 'provisioned_ip', 'description')
    list_filter = (DomainFilter, 'vendor', 'template', 'enabled')

    ordering = [
        'domain_id', 'label', 'mac_address'
    ]
    #inlines = [DeviceLinesInLine, DeviceKeysInLine, DeviceSettingsInLine]
    # Only show inlines once the device record has been created, then we know who the vendor is...
    def get_inlines(self, request, obj=None):
        if obj:
            return (DeviceLinesInLine, DeviceKeysInLine, DeviceSettingsInLine)
        else:
            return ()

    def get_form(self, request, obj=None, change=False, **kwargs):
        self.form.Meta.widgets['template'].choices = ProvisionFunctions().get_template_list()
        return super().get_form(request, obj, change, **kwargs)

    def get_formsets_with_inlines(self, request, obj=None):
        if obj:
            dvfchoices = DeviceVendorFunctionChoice().choices(obj.vendor)
        else:
            dvfchoices = DeviceVendorFunctionChoice().choices()
        for inline in self.get_inline_instances(request, obj):
            if type(inline) is DeviceKeysInLine:
                inline.form.Meta.widgets['key_type'].choices = dvfchoices
            yield inline.get_formset(request, obj), inline


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user_id':
            kwargs["queryset"] = Profile.objects.filter(domain_id=DomainUtils().domain_from_session(request))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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
        if ':' not in obj.mac_address:
            obj.mac_address = ':'.join(obj.mac_address.upper()[i:i+2] for i in range(0,12,2))
        if not change:
            obj.domain_id = DomainUtils().domain_from_session(request)
        super().save_model(request, obj, form, change)


class DeviceLinesResource(resources.ModelResource):
    class Meta:
        model = DeviceLines
        import_id_fields = ('id', )


class DeviceLinesAdmin(ImportExportModelAdmin):
    resource_class = DeviceLinesResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['line_number', 'display_name', 'auth_id', 'server_address']
    fieldsets = [
        (None,  {'fields': ['device_id', 'line_number', 'server_address',
                    'server_address_primary', 'server_address_secondary',
                    'outbound_proxy_primary', 'outbound_proxy_secondary',
                    'display_name', 'user_id', 'auth_id', 'password',
                    'sip_port', 'sip_transport', 'register_expires', 'shared_line',
                    'enabled']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('device_id', 'line_number', 'server_address', 'display_name', 'user_id', 'auth_id', 'enabled')
    list_filter = ('server_address_primary', 'server_address_secondary',
                    'outbound_proxy_primary', 'outbound_proxy_secondary',
                    'sip_port', 'sip_transport', 'register_expires', 'enabled')
    ordering = [
        'device_id', 'line_number'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class DeviceKeysResource(resources.ModelResource):
    class Meta:
        model = DeviceKeys
        import_id_fields = ('id', )


class DeviceKeysAdmin(ImportExportModelAdmin):
    resource_class = DeviceKeysResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['value', 'extension', 'label']
    fieldsets = [
        (None,  {'fields': ['device_id', 'category', 'key_id', 'key_type', 'line', 'value', 'extension',
            'protected', 'label', 'icon']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('category', 'key_id', 'key_type', 'line', 'value', 'label')
    list_filter = ('value', 'extension', 'label')
    ordering = [
        'key_id'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class DeviceSettingsResource(resources.ModelResource):
    class Meta:
        model = DeviceSettings
        import_id_fields = ('id', )


class DeviceSettingsAdmin(ImportExportModelAdmin):
    resource_class = DeviceSettingsResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'value', 'description']
    fieldsets = [
        (None,  {'fields': ['device_id', 'name', 'value', 'description', 'enabled']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('device_id', 'name', 'value', 'description', 'enabled')
    list_filter = ('name', 'enabled')
    ordering = [
        'device_id', 'name'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)



admin.site.register(DeviceVendors, DeviceVendorsAdmin)
admin.site.register(DeviceProfiles, DeviceProfilesAdmin)
admin.site.register(Devices, DevicesAdmin)

if settings.PBX_ADMIN_SHOW_ALL:
    admin.site.register(DeviceLines, DeviceLinesAdmin)
    admin.site.register(DeviceKeys, DeviceKeysAdmin)
    admin.site.register(DeviceProfileSettings, DeviceProfileSettingsAdmin)
    admin.site.register(DeviceProfileKeys, DeviceProfileKeysAdmin)
    admin.site.register(DeviceSettings, DeviceSettingsAdmin)
    admin.site.register(DeviceVendorFunctions, DeviceVendorFunctionsAdmin)
    admin.site.register(DeviceVendorFunctionGroups, DeviceVendorFunctionGroupsAdmin)
