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
    Phrases, PhraseDetails
)
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.conf import settings
from django.forms import ModelForm
from switch.switchsounds import SwitchSounds
from pbx.commonwidgets import ListTextWidget

from pbx.commonfunctions import DomainFilter, DomainUtils


class PhraseDetailsResource(resources.ModelResource):
    class Meta:
        model = PhraseDetails
        import_id_fields = ('id', )


class PhraseDetailsAdminForm(ModelForm):

    class Meta:
        model = PhraseDetails
        widgets = {
            "data": ListTextWidget(choices=[('', 'List unavailable')], attrs={'size': '50'}),
        }
        fields = '__all__'


class PhraseDetailsAdmin(ImportExportModelAdmin):
    resource_class = PhraseDetailsResource
    form = PhraseDetailsAdminForm
    save_as = True
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['pfunction', 'data']
    fieldsets = [
        (None,  {'fields': ['phrase_id', 'pfunction', 'data', 'sequence']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('phrase_id', 'pfunction', 'data', 'sequence')
    list_filter = ('phrase_id', 'pfunction')
    ordering = [
        'phrase_id, sequence'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class PhraseDetailsInlineAdminForm(ModelForm):
    class Meta:
        model = PhraseDetails
        widgets = {
#            "pfunction": TextInput(attrs={'size': '60'}),
            "data": ListTextWidget(choices=[('', 'List unavailable')], attrs={'size': '50'}),
#            "sequence": NumberInput(attrs={'size': '8'}),
        }
        fields = '__all__'


class PhraseDetailsInLine(admin.TabularInline):
    model = PhraseDetails
    form = PhraseDetailsInlineAdminForm

    extra = 2
    fieldsets = [
        (None,          {'fields': ['pfunction', 'data', 'sequence']}),
    ]
    ordering = [
        'sequence'
    ]


class PhrasesResource(resources.ModelResource):
    class Meta:
        model = Phrases
        import_id_fields = ('id', )


class PhrasesAdmin(ImportExportModelAdmin):
    resource_class = PhrasesResource
    save_as = True

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'description']
    fieldsets = [
        (None,  {'fields': ['domain_id', 'name', 'language', 'enabled', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'language', 'description', 'enabled')
    list_filter = (DomainFilter, 'enabled')
    ordering = [
        'domain_id', 'name'
    ]
    inlines = [PhraseDetailsInLine]

    def get_formsets_with_inlines(self, request, obj=None):
        data_choices = SwitchSounds().get_sounds_choices_list(request.session['domain_name'], 2)
        for inline in self.get_inline_instances(request, obj):
            inline.form.Meta.widgets['data'].choices=data_choices
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
            obj.context = request.session['domain_name']
        super().save_model(request, obj, form, change)


admin.site.register(Phrases, PhrasesAdmin)

if settings.PBX_ADMIN_SHOW_ALL:
    admin.site.register(PhraseDetails, PhraseDetailsAdmin)
