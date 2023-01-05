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
from .models import (
    ConferenceControls, ConferenceControlDetails, ConferenceProfiles, ConferenceProfileParams
)
from import_export.admin import ImportExportModelAdmin, ExportMixin
from import_export import resources


class ConferenceControlDetailsResource(resources.ModelResource):
    class Meta:
        model = ConferenceControlDetails
        import_id_fields = ('id', )


class ConferenceControlDetailsAdmin(ImportExportModelAdmin):
    resource_class = ConferenceControlDetailsResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['digits', 'action', 'data']
    fieldsets = [
        (None,  {'fields': ['conf_ctrl_id', 'digits', 'action', 'data', 'enabled']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('digits', 'action', 'data', 'enabled')
    list_filter = ('conf_ctrl_id', 'enabled')
    ordering = [
        'digits'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class ConferenceControlDetailsInLine(admin.TabularInline):
    model = ConferenceControlDetails
    #classes = ['collapse']
    extra = 1
    fieldsets = [
        (None,          {'fields': ['digits', 'action', 'data', 'enabled']}),
    ]
    ordering = [
        'digits'
    ]


class ConferenceControlsResource(resources.ModelResource):
    class Meta:
        model = ConferenceControls
        import_id_fields = ('id', )


class ConferenceControlsAdmin(ImportExportModelAdmin):
    resource_class = ConferenceControlsResource
    save_as = True
    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'descrption']
    fieldsets = [
        (None,  {'fields': ['name', 'enabled', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'enabled', 'description')
    ordering = [
        'name'
    ]
    inlines = [ConferenceControlDetailsInLine]

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


class ConferenceProfileParamsResource(resources.ModelResource):
    class Meta:
        model = ConferenceProfileParams
        import_id_fields = ('id', )


class ConferenceProfileParamsAdmin(ImportExportModelAdmin):
    resource_class = ConferenceProfileParamsResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'value', 'description']
    fieldsets = [
        (None,  {'fields': ['conf_profile_id', 'name', 'value', 'enabled', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'value', 'enabled', 'description')
    list_filter = ('conf_profile_id', 'enabled')
    ordering = [
        'name'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class ConferenceProfileParamsInLine(admin.TabularInline):
    model = ConferenceProfileParams
    #classes = ['collapse']
    extra = 1
    fieldsets = [
        (None,          {'fields': ['name', 'value', 'enabled', 'description']}),
    ]
    ordering = [
        'name'
    ]


class ConferenceProfilesResource(resources.ModelResource):
    class Meta:
        model = ConferenceProfiles
        import_id_fields = ('id', )


class ConferenceProfilesAdmin(ImportExportModelAdmin):
    resource_class = ConferenceProfilesResource
    save_as = True
    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'descrption']
    fieldsets = [
        (None,  {'fields': ['name', 'enabled', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'enabled', 'description')
    ordering = [
        'name'
    ]
    inlines = [ConferenceProfileParamsInLine]

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


admin.site.register(ConferenceControls, ConferenceControlsAdmin)
admin.site.register(ConferenceControlDetails, ConferenceControlDetailsAdmin)
admin.site.register(ConferenceProfiles, ConferenceProfilesAdmin)
admin.site.register(ConferenceProfileParams, ConferenceProfileParamsAdmin)
