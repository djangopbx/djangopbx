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

from django.contrib import admin

from .models import (
    NumberTranslations, NumberTranslationDetails
)
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.conf import settings
from django.forms import ModelForm


class NumberTranslationDetailsResource(resources.ModelResource):
    class Meta:
        model = NumberTranslationDetails
        import_id_fields = ('id', )


class NumberTranslationDetailsAdmin(ImportExportModelAdmin):
    resource_class = NumberTranslationDetailsResource
    save_as = True
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['td_regex', 'td_replace']
    fieldsets = [
        (None,  {'fields': ['phrase_id', 'pfunction', 'data', 'sequence']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('number_translation_id', 'td_regex', 'td_replace', 'td_order')
    list_filter = ('number_translation_id',)
    ordering = [
        'number_translation_id, td_order'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class NumberTranslationDetailsInLine(admin.TabularInline):
    model = NumberTranslationDetails

    extra = 2
    fieldsets = [
        (None,          {'fields': ['td_regex', 'td_replace', 'td_order']}),
    ]
    ordering = [
        'td_order'
    ]


class NumberTranslationsResource(resources.ModelResource):
    class Meta:
        model = NumberTranslations
        import_id_fields = ('id', )


class NumberTranslationsAdmin(ImportExportModelAdmin):
    resource_class = NumberTranslationsResource
    save_as = True

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'description']
    fieldsets = [
        (None,  {'fields': ['name', 'enabled', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'description', 'enabled')
    list_filter = ('enabled',)
    ordering = [
        'name'
    ]
    inlines = [NumberTranslationDetailsInLine]

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


admin.site.register(NumberTranslations, NumberTranslationsAdmin)

if settings.PBX_ADMIN_SHOW_ALL:
    admin.site.register(NumberTranslationDetails, NumberTranslationDetailsAdmin)
