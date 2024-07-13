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
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.conf import settings
from django.forms import ModelForm
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from utilities.clearcache import ClearCache
from .models import (
    ConferenceControls, ConferenceControlDetails, ConferenceProfiles, ConferenceProfileParams,
    ConferenceRoomUser, ConferenceRooms, ConferenceCentres, ConferenceSessions,
)
from dialplans.models import Dialplan
from switch.switchsounds import SwitchSounds
from tenants.pbxsettings import PbxSettings
from pbx.commonwidgets import ListTextWidget
from pbx.commonfunctions import DomainFilter, DomainUtils
from .conferencefunctions import CnfFunctions


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


class ConferenceRoomUserResource(resources.ModelResource):
    class Meta:
        model = ConferenceRoomUser
        import_id_fields = ('id', )


class ConferenceRoomUserAdmin(ImportExportModelAdmin):
    resource_class = ConferenceRoomUserResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['user_uuid']
    fieldsets = [
        (None,  {'fields': ['user_uuid', ]}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('c_room_id', 'user_uuid',)
    list_filter = ()
    ordering = [
        'c_room_id','user_uuid'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class ConferenceRoomUserInLine(admin.TabularInline):
    model = ConferenceRoomUser
    extra = 1
    fieldsets = [
        (None,          {'fields': ['user_uuid']}),
    ]
    ordering = [
        'user_uuid'
    ]


class ConferenceRoomsResource(resources.ModelResource):
    class Meta:
        model = ConferenceRooms
        import_id_fields = ('id', )


class ConferenceRoomsAdmin(ImportExportModelAdmin):
    resource_class = ConferenceRoomsResource
    save_as = True

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'descrption']
    fieldsets = [
        (None,  {'fields': ['c_centre_id', 'name', 'c_profile_id', 'moderator_pin', 'participant_pin',
                    'max_members', ('start_time', 'stop_time'),
                    'record', 'wait_mod', 'announce', 'sounds', 'mute',
                    'enabled', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'participant_pin', 'moderator_pin', 'enabled', 'description')
    list_filter = ('enabled', )
    ordering = [
        'name'
    ]
    inlines = [ConferenceRoomUserInLine]

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


class ConferenceCentresAdminForm(ModelForm):

    class Meta:
        model = ConferenceCentres
        widgets = {
            "greeting": ListTextWidget(choices=[('', 'List unavailable')], attrs={'style': 'width:350px'}),
        }
        fields = '__all__'


class ConferenceCentresResource(resources.ModelResource):
    class Meta:
        model = ConferenceCentres
        import_id_fields = ('id', )


class ConferenceCentresAdmin(ImportExportModelAdmin):
    resource_class = ConferenceCentresResource
    form = ConferenceCentresAdminForm
    change_form_template = "admin_genhtml_changeform.html"
    save_as = True

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'descrption']
    fieldsets = [
        (None,  {'fields': ['domain_id', 'name', 'extension', 'greeting',
                    'enabled', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'extension', 'enabled', 'description')
    list_filter = (DomainFilter, 'enabled')
    ordering = [
        'name'
    ]

    def get_form(self, request, obj=None, change=False, **kwargs):
        ss = SwitchSounds()
        # this is required for access to the request object so the domain_name session
        # variable can be passed to the chioces function
        self.form.Meta.widgets['greeting'].choices=ss.get_sounds_choices_list(request.session['domain_name'], True)
        return super().get_form(request, obj, change, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        if change:
            pbxsettings = PbxSettings()
            if (pbxsettings.default_settings('dialplan', 'auto_generate_xml', 'boolean', 'true', True)[0]) == 'true':
                cnf = CnfFunctions(obj, request.user.username)
                cnf.generate_xml()
            if (pbxsettings.default_settings('dialplan', 'auto_flush_cache', 'boolean', 'true', True)[0]) == 'true':
                cc = ClearCache()
                cc.dialplan(request.session['domain_name'])
                cc.configuration()
        else:
            obj.domain_id = DomainUtils().domain_from_session(request)
        super().save_model(request, obj, form, change)

    def response_change(self, request, obj):
        if '_generate-xml' in request.POST:
            cnf = CnfFunctions(obj, request.user.username)
            dp_id = cnf.generate_xml()
            if dp_id:
                obj.dialplan_id = dp_id
                obj.save()
                self.message_user(request, 'XML Generated')
            else:
                self.message_user(request, 'XML Failed', level=messages.ERROR)
            return HttpResponseRedirect('.')
        if '_clear-cache' in request.POST:
            cc = ClearCache()
            cc.dialplan(request.session['domain_name'])
            cc.configuration()
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


class ConferenceSessionsAdmin(admin.ModelAdmin):

    readonly_fields = ['id', 'c_room_id', 'caller_id_name', 'caller_id_number', 'profile',
                        'recording', 'start', 'end', 'created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['c_room_id', 'caller_id_name', 'caller_id_number']
    fieldsets = [
        (None,  {'fields': ['id', 'c_room_id', 'caller_id_name', 'caller_id_number',
                    'profile', 'live', 'recording', 'start', 'end']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('c_room_id', 'caller_id_name', 'caller_id_number', 'profile', 'start', 'end')
    list_filter = ('c_room_id', 'live')
    ordering = [
        '-created'
    ]


admin.site.register(ConferenceCentres, ConferenceCentresAdmin)
admin.site.register(ConferenceRooms, ConferenceRoomsAdmin)
admin.site.register(ConferenceControls, ConferenceControlsAdmin)
admin.site.register(ConferenceProfiles, ConferenceProfilesAdmin)
admin.site.register(ConferenceSessions, ConferenceSessionsAdmin)

if settings.PBX_ADMIN_SHOW_ALL:
    admin.site.register(ConferenceControlDetails, ConferenceControlDetailsAdmin)
    admin.site.register(ConferenceProfileParams, ConferenceProfileParamsAdmin)
