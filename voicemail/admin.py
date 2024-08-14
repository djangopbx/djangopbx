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
from django.forms import ModelForm
from django.forms.widgets import TextInput
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from pbx.fileabslayer import FileAbsLayer
from pbx.commonwidgets import PlayerAdminFileFieldWidget

from .models import (
    Voicemail, VoicemailGreeting,
)


class VoicemailGreetingInlineAdminForm(ModelForm):

    class Meta:
        model = VoicemailGreeting
        widgets = {
            "name": TextInput(attrs={'size': '60'}),
            "filename": PlayerAdminFileFieldWidget(),
        }
        fields = '__all__'


class VoicemailGreetingInLine(admin.TabularInline):
    model = VoicemailGreeting
    form = VoicemailGreetingInlineAdminForm

    extra = 1
    fieldsets = [
        (None,          {'fields': ['name', 'filename', 'filestore']}),
    ]
    ordering = [
        'filename'
    ]


class VoicemailResource(resources.ModelResource):
    class Meta:
        model = Voicemail
        import_id_fields = ('id', )


class VoicemailAdmin(ImportExportModelAdmin):
    resource_class = VoicemailResource

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    fieldsets = [
        # Voicemail records are automatically created when an extension is added.
        # To allow adding a voicemail record maually:
        # 1. Add extension_id to the field set below, just before password.
        # 2. Comment out the def has_add_permission.
        (None,  {'fields': [
                    'password', 'greeting_id', 'alternate_greeting_id',
                    'mail_to', 'sms_to', 'cc', 'attach_file', 'local_after_email', 'enabled', 'description'
                    ]}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('extension_id', 'mail_to', 'attach_file', 'local_after_email', 'enabled', 'description')
    list_filter = ('extension_id__domain_id', 'enabled',)

    ordering = [
        'extension_id__extension'
    ]
    inlines = [VoicemailGreetingInLine]

    def has_add_permission(self, request):
        return False

    def save_formset(self, request, form, formset, change):
        if not settings.PBX_FREESWITCH_LOCAL:
            fal = FileAbsLayer()
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            if not settings.PBX_FREESWITCH_LOCAL:
                fal.delete('/home/django-pbx/media/%s' % obj.filename.name, request.session['home_switch'])
            obj.filename.delete(save=False)
            obj.delete()
        for instance in instances:
            instance.updated_by = request.user.username
            instance.save()
            if not settings.PBX_FREESWITCH_LOCAL:
                path = '/home/django-pbx/media/fs/voicemail/default/{0}/{1}'.format(
                        instance.voicemail_id.extension_id.domain_id.name,
                        instance.voicemail_id.extension_id.extension)
                instance.filename.open(mode='rb')
                if not fal.exists(path, request.session['home_switch']):
                    fal.mkdir(path, request.session['home_switch'])
                fal.putfo(instance.filename, '/home/django-pbx/media/%s' % instance.filename.name, request.session['home_switch'])
                instance.filename.close()
        formset.save_m2m()

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


admin.site.register(Voicemail, VoicemailAdmin)
