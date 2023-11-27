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

from .models import (
    RingGroup, RingGroupDestination, RingGroupUser
)
from tenants.models import Profile
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.conf import settings
from django.forms import ModelForm, Select
from switch.switchsounds import SwitchSounds
from pbx.commonwidgets import ListTextWidget

from pbx.commonfunctions import DomainFilter, DomainUtils
from pbx.commondestination import CommonDestAction
from .ringgroupfunctions import RgFunctions


class RingGroupUserResource(resources.ModelResource):
    class Meta:
        model = RingGroupUser
        import_id_fields = ('id', )


class RingGroupUserAdmin(ImportExportModelAdmin):
    resource_class = RingGroupUserResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['user_uuid']
    fieldsets = [
        (None,  {'fields': ['user_uuid', ]}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('ring_group_id', 'user_uuid',)
    list_filter = ()
    ordering = [
        'ring_group_id','user_uuid'
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user_uuid':
            kwargs["queryset"] = Profile.objects.filter(domain_id=DomainUtils().domain_from_session(request))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class RingGroupUserInLine(admin.TabularInline):
    model = RingGroupUser
    extra = 1
    fieldsets = [
        (None,          {'fields': ['user_uuid']}),
    ]
    ordering = [
        'user_uuid'
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user_uuid':
            kwargs["queryset"] = Profile.objects.filter(domain_id=DomainUtils().domain_from_session(request))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class RingGroupDestinationResource(resources.ModelResource):
    class Meta:
        model = RingGroupDestination
        import_id_fields = ('id', )


class RingGroupDestinationAdmin(ImportExportModelAdmin):
    resource_class = RingGroupDestinationResource
    save_as = True
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['number']
    fieldsets = [
        (None,  {'fields': ['number', 'delay', 'timeout', 'destination_prompt']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('ring_group_id', 'number')
    list_filter = ('ring_group_id', 'number')
    ordering = [
        'ring_group_id, number'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class RingGroupDestinationInLine(admin.TabularInline):
    model = RingGroupDestination
    extra = 3
    fieldsets = [
        (None,          {'fields': ['number', 'delay', 'timeout', 'destination_prompt']}),
    ]
    ordering = [
        'number'
    ]


class RingGroupAdminForm(ModelForm):

    class Meta:
        model = RingGroup
        widgets = {
            "greeting": ListTextWidget(choices=[('', 'List unavailable')], attrs={'size': '50'}),
            "timeout_data": Select(choices=[('', 'List unavailable')], attrs={'style': 'width:350px'}),
            "ring_group_ringback": Select(choices=[('', 'List unavailable')]),
        }
        fields = '__all__'


class RingGroupResource(resources.ModelResource):
    class Meta:
        model = RingGroup
        import_id_fields = ('id', )


class RingGroupAdmin(ImportExportModelAdmin):
    resource_class = RingGroupResource
    form = RingGroupAdminForm
    change_form_template = "admin_genhtml_changeform.html"
    save_as = True
    change_list_template = "admin_changelist.html"

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'extension', 'description']
    fieldsets = [
        (None,  {'fields': ['domain_id', 'name', 'extension', 'greeting', 'strategy', 
                            'timeout_data',
                            ('missed_call_app', 'missed_call_data'),
                            'call_timeout', 'forward_toll_allow',
                            ('forward_enabled', 'forward_destination'),
                            ('caller_id_name', 'caller_id_number'),
                            ('cid_name_prefix', 'cid_number_prefix'),
                            'distinctive_ring', 'ring_group_ringback', 'follow_me_enabled',
                            'context', 'enabled', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'extension', 'context', 'description', 'enabled')
    list_filter = (DomainFilter, 'enabled', 'forward_enabled')
    ordering = [
        'domain_id', 'name', 'extension'
    ]
    inlines = [RingGroupDestinationInLine, RingGroupUserInLine]

    def get_form(self, request, obj=None, change=False, **kwargs):
        ss = SwitchSounds()
        rga = CommonDestAction(request.session['domain_name'], request.session['domain_uuid'])
        # this is required for access to the request object so the domain_name session
        # variable can be passed to the chioces function
        self.form.Meta.widgets['greeting'].choices=ss.get_sounds_choices_list(request.session['domain_name'], True)
        self.form.Meta.widgets['timeout_data'].choices=rga.get_action_choices()
        self.form.Meta.widgets['ring_group_ringback'].choices=ss.get_ringback_choices_list(request.session['domain_name'])
        return super().get_form(request, obj, change, **kwargs)

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
        if "_generate-xml" in request.POST:
            rgf = RgFunctions(request.session['domain_uuid'], request.session['domain_name'], str(obj.id), request.user.username)
            obj.dialplan_id = rgf.generate_xml()
            obj.save()
            self.message_user(request, "XML Generated")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)


admin.site.register(RingGroup, RingGroupAdmin)

if settings.PBX_ADMIN_SHOW_ALL:
    admin.site.register(RingGroupDestination, RingGroupDestinationAdmin)
    admin.site.register(RingGroupUser, RingGroupUserAdmin)
