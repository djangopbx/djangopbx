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
from django.http import HttpResponseRedirect
from pbx.commonfunctions import DomainFilter, DomainUtils
from switch.switchsounds import SwitchSounds
from utilities.clearcache import ClearCache
from pbx.commonwidgets import ListTextWidget
from pbx.commondestination import CommonDestAction
from django.forms import ModelForm, Select
from .ivrmenufunctions import IvrFunctions

from .models import (
    IvrMenus, IvrMenuOptions
)
from dialplans.models import Dialplan
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.conf import settings
from django.contrib import messages
from django.forms import ModelForm


class IvrMenuOptionsResource(resources.ModelResource):
    class Meta:
        model = IvrMenuOptions
        import_id_fields = ('id', )


class IvrMenuOtionsAdminForm(ModelForm):

    class Meta:
        model = IvrMenuOptions
        widgets = {
            "option_param": ListTextWidget(choices=[('', 'List unavailable')], attrs={'size': '50'}),
        }
        fields = '__all__'


class IvrMenuOptionsAdmin(ImportExportModelAdmin):
    resource_class = IvrMenuOptionsResource
    form = IvrMenuOtionsAdminForm
    save_as = True
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['option_param', 'description']
    fieldsets = [
        (None,  {'fields': ['ivr_menu_id', 'option_digits', 'option_action', 'option_param', 'sequence', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('ivr_menu_id', 'option_digits', 'sequence', 'description')
    list_filter = ('ivr_menu_id',)
    ordering = [
        'ive_menu_id, option_digits, sequence'
    ]

    def get_form(self, request, obj=None, change=False, **kwargs):
        ivra = CommonDestAction(request.session['domain_name'], request.session['domain_uuid'])
        # this is required for access to the request object so the domain_name session
        # variable can be passed to the chioces function
        self.form.Meta.widgets['option_param'].choices=ivra.get_action_choices(' ', True)
        return super().get_form(request, obj, change, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class IvrMenuOptionsInLine(admin.TabularInline):
    model = IvrMenuOptions
    form = IvrMenuOtionsAdminForm

    extra = 2
    fieldsets = [
        (None,          {'fields': ['option_digits', 'option_param', 'sequence', 'description']}),
    ]
    ordering = [
        'option_digits', 'sequence'
    ]


class IvrMenusAdminForm(ModelForm):

    class Meta:
        model = IvrMenus
        widgets = {
            "language": Select(choices=[('', 'List unavailable')]),
            "greet_long": ListTextWidget(choices=[('', 'List unavailable')], attrs={'size': '50'}),
            "greet_short": ListTextWidget(choices=[('', 'List unavailable')], attrs={'size': '50'}),
            "exit_data": Select(choices=[('', 'List unavailable')], attrs={'style': 'width:350px'}),
            "ringback": Select(choices=[('', 'List unavailable')]),
            "invalid_sound": ListTextWidget(choices=[('', 'List unavailable')], attrs={'size': '50'}),
            "exit_sound": ListTextWidget(choices=[('', 'List unavailable')], attrs={'size': '50'}),
        }
        fields = '__all__'


class IvrMenusResource(resources.ModelResource):
    class Meta:
        model = IvrMenus
        import_id_fields = ('id', )


class IvrMenusAdmin(ImportExportModelAdmin):
    resource_class = IvrMenusResource
    form = IvrMenusAdminForm
    change_form_template = "admin_genhtml_changeform.html"
    save_as = True

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'extension', 'description']
    fieldsets = [
        (None,  {'fields': [
                    'name',
                    'extension',
                    'language',
                    'greet_long',
                    'greet_short',
                    'timeout',
                    'exit_data',
                    'direct_dial',
                    'ringback',
                    'cid_prefix',
                    'context',
                    'enabled',
                    'description'
                ]}),
        ('Advanced',  {'fields': [
                    'invalid_sound',
                    'exit_sound',
                    'confirm_macro',
                    'confirm_key',
                    'tts_engine',
                    'tts_voice',
                    'confirm_attempts',
                    'inter_digit_timeout',
                    'max_failiures',
                    'max_timeouts',
                    'digit_len',
                    'domain_id'
                ], 'classes': ['collapse']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'extension', 'description', 'enabled')
    list_filter = (DomainFilter, 'enabled',)
    ordering = [
        'name'
    ]
    inlines = [IvrMenuOptionsInLine]

    def get_form(self, request, obj=None, change=False, **kwargs):
        ss = SwitchSounds()
        ivra = CommonDestAction(request.session['domain_name'], request.session['domain_uuid'])
        # this is required for access to the request object so the domain_name session
        # variable can be passed to the chioces function
        sound_choices_list = ss.get_sounds_choices_list(request.session['domain_name'], True)
        self.form.Meta.widgets['language'].choices = ss.get_languages()
        self.form.Meta.widgets['greet_long'].choices = sound_choices_list
        self.form.Meta.widgets['greet_short'].choices = sound_choices_list
        self.form.Meta.widgets['exit_data'].choices = ivra.get_action_choices()
        self.form.Meta.widgets['ringback'].choices = ss.get_ringback_choices_list(request.session['domain_name'])
        self.form.Meta.widgets['invalid_sound'].choices = sound_choices_list
        self.form.Meta.widgets['exit_sound'].choices = sound_choices_list
        return super().get_form(request, obj, change, **kwargs)

    def get_formsets_with_inlines(self, request, obj=None):
        ivra = CommonDestAction(request.session['domain_name'], request.session['domain_uuid'])
        option_param_choices = ivra.get_action_choices(' ', True, 0b1011111111111111)
        for inline in self.get_inline_instances(request, obj):
            inline.form.Meta.widgets['option_param'].choices=option_param_choices
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

    def response_change(self, request, obj):
        if '_generate-xml' in request.POST:
            ivrf = IvrFunctions(obj, request.user.username)
            dp_id = ivrf.generate_xml()
            if dp_id:
                obj.dialplan_id = dp_id
                obj.save()
                self.message_user(request, 'XML Generated')
            else:
                self.message_user(request, 'XML Failed', level=messages.ERROR)
            return HttpResponseRedirect('.')
        if '_clear-cache' in request.POST:
            cc = ClearCache()
            cc.dialplan(request.session['domain_name'], request.session['domain_uuid'])
            cc.configuration(request.session['domain_uuid'])
            self.message_user(request, 'Cache flushed')
            return HttpResponseRedirect('.')
        return super().response_change(request, obj)

    def delete_model(self, request, obj):
        if obj.dialplan_id:
            Dialplan.objects.get(pk=obj.dialplan_id).delete()
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if obj.dialplan_id:
                Dialplan.objects.get(pk=obj.dialplan_id).delete()
        super().delete_queryset(request, queryset)


admin.site.register(IvrMenus, IvrMenusAdmin)

if settings.PBX_ADMIN_SHOW_ALL:
    admin.site.register(IvrMenuOptions, IvrMenuOptionsAdmin)
