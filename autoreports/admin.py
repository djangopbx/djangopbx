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
    AutoReports, AutoReportSections
)
from django.forms import ModelForm
from django_ace import AceWidget
from django.forms.widgets import TextInput, Textarea, NumberInput
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.conf import settings

from pbx.commonfunctions import DomainFilter, DomainUtils


class AutoReportSectionsResource(resources.ModelResource):
    class Meta:
        model = AutoReportSections
        import_id_fields = ('id', )


class AutoReportSectionsAdminForm(ModelForm):
    class Meta:
        model = AutoReportSections
        widgets = {
            "title": TextInput(attrs={'size': '20'}),
            "sql": AceWidget(
                usesofttabs=False, showprintmargin=False,
                width="700px", height="300px", mode='sql', theme='cobalt'
                ),
            "message": Textarea(attrs={'size': '20'}),
            "sequence": NumberInput(attrs={'size': '8'}),
        }
        fields = '__all__'


class AutoReportSectionsAdmin(ImportExportModelAdmin):
    resource_class = AutoReportSectionsResource
    save_as = True
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['title', 'description', 'sql']
    fieldsets = [
        (None,  {'fields': ['auto_report_id', 'title', 'sequence', 'sql', 'message', 'enabled', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('auto_report_id', 'title', 'sequence', 'sql', 'enabled', 'description')
    list_filter = ('auto_report_id', 'enabled')
    ordering = [
        'auto_report_id, sequence'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class AutoReportSectionsInLine(admin.TabularInline):
    model = AutoReportSections
    form = AutoReportSectionsAdminForm

    extra = 1
    fieldsets = [
        (None,          {'fields': ['title', 'sql', 'message', 'sequence', 'enabled']}),
    ]
    ordering = [
        'sequence'
    ]


class AutoReportsResource(resources.ModelResource):
    class Meta:
        model = AutoReports
        import_id_fields = ('id', )


class AutoReportsAdmin(ImportExportModelAdmin):
    resource_class = AutoReportsResource
    save_on_top = True
    save_as = True

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'title', 'recipients', 'description']
    fieldsets = [
        (None,  {'fields': ['domain_id', 'name', 'title', 'message', 'footer', 'recipients', 'frequency',
                    'enabled', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'title', 'description', 'enabled', 'view_report')
    list_filter = (DomainFilter, 'enabled')
    ordering = [
        'domain_id', 'name'
    ]
    inlines = [AutoReportSectionsInLine]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            instance.sql = instance.sql.replace('{{ domain_uuid }}', request.session.get('domain_uuid'))
            instance.sql = instance.sql.replace('{{ domain_name }}', request.session.get('domain_name'))
            instance.updated_by = request.user.username
            instance.save()
        formset.save_m2m()

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        if not change:
            obj.domain_id = DomainUtils().domain_from_session(request)
            obj.context = request.session['domain_name']
        super().save_model(request, obj, form, change)


admin.site.register(AutoReports, AutoReportsAdmin)

if settings.PBX_ADMIN_SHOW_ALL:
    admin.site.register(AutoReportSections, AutoReportSectionsAdmin)
