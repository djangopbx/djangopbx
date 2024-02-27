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
    CallFlows
)
from dialplans.models import Dialplan
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.conf import settings
from django.contrib import messages
from django.forms import ModelForm, Select
from switch.switchsounds import SwitchSounds
from pbx.commonwidgets import ListTextWidget

from pbx.commonfunctions import DomainFilter, DomainUtils
from pbx.commondestination import CommonDestAction
from .callflowfunctions import CfFunctions
from pbx.commonevents import PresenceIn


class CallFlowsAdminForm(ModelForm):

    class Meta:
        model = CallFlows
        widgets = {
            "sound": ListTextWidget(choices=[('', 'List unavailable')], attrs={'size': '50'}),
            "data": Select(choices=[('', 'List unavailable')]),
            "alternate_sound": ListTextWidget(choices=[('', 'List unavailable')], attrs={'size': '50'}),
            "alternate_data": Select(choices=[('', 'List unavailable')]),
        }
        fields = '__all__'


class CallFlowsResource(resources.ModelResource):
    class Meta:
        model = CallFlows
        import_id_fields = ('id', )


class CallFlowsAdmin(ImportExportModelAdmin):
    resource_class = CallFlowsResource
    form = CallFlowsAdminForm
    change_form_template = "admin_genhtml_changeform.html"
    save_as = True

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'extension', 'description']
    fieldsets = [
        (None,  {'fields': ['domain_id', 'name', 'extension', 'feature_code', 'status', 'pin_number',
                            'label', 'sound', 'data',
                            'alternate_label', 'alternate_sound', 'alternate_data',
                            'context', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'extension', 'context', 'description')
    list_filter = (DomainFilter, )
    ordering = [
        'domain_id', 'name', 'extension'
    ]

    def get_form(self, request, obj=None, change=False, **kwargs):
        ss = SwitchSounds()
        cda = CommonDestAction(request.session['domain_name'], request.session['domain_uuid'])
        # this is required for access to the request object so the domain_name session
        # variable can be passed to the chioces function
        sound_choices = ss.get_sounds_choices_list(request.session['domain_name'], True)
        action_choices = cda.get_action_choices()
        self.form.Meta.widgets['sound'].choices=sound_choices
        self.form.Meta.widgets['data'].choices=action_choices
        self.form.Meta.widgets['alternate_sound'].choices=sound_choices
        self.form.Meta.widgets['alternate_data'].choices=action_choices
        return super().get_form(request, obj, change, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        pe = PresenceIn()
        pe.send(str(obj.id), obj.status, obj.feature_code, request.session['domain_name'])
        if not change:
            obj.domain_id = DomainUtils().domain_from_session(request)
            obj.context = request.session['domain_name']
        super().save_model(request, obj, form, change)

    def response_change(self, request, obj):
        if "_generate-xml" in request.POST:
            cff = CfFunctions(obj, request.user.username)
            dp_id = cff.generate_xml()
            if dp_id:
                obj.dialplan_id = dp_id
                obj.save()
                self.message_user(request, "XML Generated")
            else:
                self.message_user(request, "XML Failed", level=messages.ERROR)
            return HttpResponseRedirect(".")
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


admin.site.register(CallFlows, CallFlowsAdmin)

