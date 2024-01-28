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
from django.db.models import Case, Value, When
from django.forms.widgets import TextInput, NumberInput, Select
from django.forms import ModelForm
from django_ace import AceWidget
from pbx.commonwidgets import ListTextWidget
from pbx.commonfunctions import DomainFilter, DomainUtils

from .dialplanfunctions import SwitchDp, DpApps

from .models import (
    Dialplan, DialplanDetail
)

from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.http import HttpResponseRedirect


class XmlEditAdminForm(ModelForm):
    class Meta:
        model = Dialplan
        widgets = {
            "category": Select(choices=DpApps().get_dp_apps_choices()),
            "xml": AceWidget(
                usesofttabs=False, showprintmargin=False,
                width="800px", height="400px", mode='xml', theme='cobalt'
                ),
        }
        fields = '__all__'


class DialplanDetailsInlineAdminForm(ModelForm):
    class Meta:
        model = DialplanDetail
        widgets = {
            "type": ListTextWidget(choices=SwitchDp().tag_type_choices, attrs={'size': '30'}),
            "data": TextInput(attrs={'size': '60'}),
            "group": NumberInput(attrs={'size': '8'}),
            "sequence": NumberInput(attrs={'size': '8'}),
        }
        fields = '__all__'


class DialplanDetailResource(resources.ModelResource):
    class Meta:
        model = DialplanDetail
        import_id_fields = ('id', )


class DialplanDetailAdmin(ImportExportModelAdmin):
    resource_class = DialplanDetailResource

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    list_display = ('tag', 'type', 'data', 'dp_break', 'inline', 'group', 'sequence')
    list_filter = ('dialplan_id__domain_id', 'dialplan_id__name', 'group')
    fieldsets = [
        (None,  {'fields': ['tag', 'type', 'data', 'dp_break', 'inline', 'group', 'sequence']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    ordering = [
        'group',
        Case(
         When(tag='condition', then=Value(1)),
         When(tag='action', then=Value(2)),
         When(tag='anti-action', then=Value(3)),
         default=Value(100)
        ),
        'sequence'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class DialplanDetailsInLine(admin.TabularInline):
    model = DialplanDetail
    form = DialplanDetailsInlineAdminForm
    classes = ['collapse']

    extra = 4
    fieldsets = [
        (None,          {'fields': ['tag', 'type', 'data', 'dp_break', 'inline', 'group', 'sequence']}),
    ]
    ordering = [
        'group',
        Case(
         When(tag='condition', then=Value(1)),
         When(tag='action', then=Value(2)),
         When(tag='anti-action', then=Value(3)),
         default=Value(100)
        ),
        'sequence'
    ]


class DialplanResource(resources.ModelResource):

    class Meta:
        model = Dialplan
        import_id_fields = ('id', )


class DialplanAdmin(ImportExportModelAdmin):
    resource_class = DialplanResource

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    form = XmlEditAdminForm
    change_form_template = "dialplans/dialplan_changeform.html"
    save_on_top = True
    save_as = True

    readonly_fields = ['app_id', 'created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'number', 'category', 'xml']

    list_display = ('name', 'number', 'context', 'sequence', 'enabled')
    list_filter = (DomainFilter, 'category', 'context', 'enabled', 'destination')

    fieldsets = (
        (None,  {'fields': [
            'category', ('name', 'sequence'), ('number', 'destination'),
            ('hostname', 'domain_id'), ('context', 'enabled'), ('description', 'dp_continue')
            ]}),
        ('XML', {'fields': ['xml', 'app_id',]}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    )

    ordering = ['sequence', 'name']

    inlines = [DialplanDetailsInLine]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            instance.updated_by = request.user.username
            instance.save()
        formset.save_m2m()

    def response_change(self, request, obj):
        if "_generate-xml" in request.POST:
            obj.xml = SwitchDp().generate_xml(obj.id, request.session['domain_uuid'], request.session['domain_name'])
            obj.save()
            self.message_user(request, "XML Generated")
            return HttpResponseRedirect(".")
        if "_generate-dd-xml" in request.POST:
            SwitchDp().create_dpd_from_xml(obj.id, request.user.username)
            obj.save()
            self.message_user(request, "Dialplan Details Generated")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    def save_model(self, request, obj, form, change):
        app_uuids = DpApps().get_dp_apps_uuids()
        obj.updated_by = request.user.username
        if obj.category not in ['Default', 'Default Modified']:
            obj.app_id = app_uuids[obj.category]
        if not change:
            obj.domain_id = DomainUtils().domain_from_session(request)
            obj.context = request.session['domain_name']
        super().save_model(request, obj, form, change)


admin.site.register(Dialplan, DialplanAdmin)

if settings.PBX_ADMIN_SHOW_ALL:
    admin.site.register(DialplanDetail, DialplanDetailAdmin)
