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
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.forms.widgets import TextInput
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from .musiconholdfunctions import MohFunctions

from .models import (
    MusicOnHold, MohFile,
)


class MusicOnHoldFileInlineAdminForm(ModelForm):

    class Meta:
        model = MohFile
        widgets = {
            "file_name": TextInput(attrs={'size': '60'}),
        }
        fields = '__all__'


class MusicOnHoldFileInLine(admin.TabularInline):
    model = MohFile
    form = MusicOnHoldFileInlineAdminForm

    extra = 1
    fieldsets = [
        (None,          {'fields': ['file_name', 'filename']}),
    ]
    ordering = [
        'file_name'
    ]


class MusicOnHoldResource(resources.ModelResource):
    class Meta:
        model = MusicOnHold
        import_id_fields = ('id', )


@admin.action(permissions=['change'], description='Write local_strem.conf.xml file')
def write_local_stream_file(modeladmin, request, queryset):
    r = MohFunctions().write_local_stream_xml()
    if r == 0:
        messages.add_message(request, messages.INFO, _('acl.conf.xml file written.'))
    if r == 1:
        messages.add_message(request, messages.WARNING, _('Default setting does not exist:') + ' switch->conf')
    if r == 2:
        messages.add_message(request, messages.WARNING, _('Configuration directory does not exist.'))
    if r == 3:
        messages.add_message(request, messages.WARNING, _('Error writing to file.'))


class MusicOnHoldAdmin(ImportExportModelAdmin):
    resource_class = MusicOnHoldResource

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    fieldsets = [
        (None,  {'fields': [
                    'domain_id', 'name', 'rate', 'path',
                    'shuffle', 'channels', 'interval', 'timer_name',
                    'chime_list', 'chime_freq', 'chime_max'
                    ]}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'rate', 'path')
    list_filter = ('name', 'rate')

    ordering = [
        'name',
        'rate'
    ]
    inlines = [MusicOnHoldFileInLine]
    actions = [write_local_stream_file]

    # This is a workaround to allow the admin action to be run without selecting any objects.
    # super checks for a valid UUID, so we pass a meaningless one because it is not actually used.
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and request.POST['action'] == 'write_local_stream_file':
            post = request.POST.copy()
            post.update({ACTION_CHECKBOX_NAME: 'eb30bc83-ccb8-4f27-a1d6-9340ae7de325'})
            request._set_post(post)
        return super(MusicOnHoldAdmin, self).changelist_view(request, extra_context)

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


admin.site.register(MusicOnHold, MusicOnHoldAdmin)
