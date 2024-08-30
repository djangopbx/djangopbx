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
from django.forms.widgets import TextInput, NumberInput, Select
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from pbx.fileabslayer import FileAbsLayer
from pbx.commondestination import CommonDestAction
from pbx.commonwidgets import PlayerAdminFileFieldWidget, ListTextWidget
from .filters import VoicemailDomainFilter
from .models import (
    Voicemail, VoicemailGreeting, VoicemailOptions, VoicemailMessages,
    VoicemailDestinations
)
from.voicemailfunctions import VoicemailFunctions


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
    classes = ['collapse']
    extra = 1
    fieldsets = [
        (None,          {'fields': ['name', 'filename', 'filestore']}),
    ]
    ordering = [
        'filename'
    ]


class VoicemailMessagesInlineAdminForm(ModelForm):

    class Meta:
        model = VoicemailMessages
        widgets = {
            "name": TextInput(attrs={'size': '40'}),
            "filename": PlayerAdminFileFieldWidget(),
            "filestore": TextInput(attrs={'size': '10'}),
            "caller_id_number": TextInput(attrs={'size': '20'}),
            "status": TextInput(attrs={'size': '5'}),
            "duration": NumberInput(attrs={'size': '7'}),
        }
        fields = '__all__'


class VoicemailMessagesInLine(admin.TabularInline):
    model = VoicemailMessages
    form = VoicemailMessagesInlineAdminForm

    extra = 0
    fieldsets = [
        (None,          {'fields': ['name', 'filename', 'filestore', 'caller_id_number', 'status', 'read', 'duration']}),
    ]
    ordering = [
        '-created'
    ]


class VoicemailOptionsInlineAdminForm(ModelForm):

    class Meta:
        model = VoicemailOptions
        widgets = {
            "option_param": ListTextWidget(choices=[('', 'List unavailable')], attrs={'size': '50'}),
        }
        fields = '__all__'


class VoicemailOptionsInLine(admin.TabularInline):
    model = VoicemailOptions
    form = VoicemailOptionsInlineAdminForm
    classes = ['collapse']

    extra = 1
    fieldsets = [
        (None,          {'fields': ['option_digits', 'option_param', 'sequence', 'description']}),
    ]
    ordering = [
        'option_digits', 'sequence'
    ]


class VoicemailDestinationsInlineAdminForm(ModelForm):

    class Meta:
        model = VoicemailDestinations
        widgets = {
            "voicemail_dest": Select(choices=[('', 'List unavailable')]),
        }
        fields = '__all__'


class VoicemailDestinationsInLine(admin.TabularInline):
    model = VoicemailDestinations
    form = VoicemailDestinationsInlineAdminForm
    classes = ['collapse']

    extra = 1
    fieldsets = [
        (None,          {'fields': ['voicemail_dest']}),
    ]
    ordering = [

    ]


class VoicemailResource(resources.ModelResource):
    class Meta:
        model = Voicemail
        import_id_fields = ('id', )


@admin.action(permissions=['change'], description='Sync. greeting files on disk with database.')
def sync_greeting_files(modeladmin, request, queryset):  # Only applicable if using mod_voicemail
    vf = VoicemailFunctions()                            # See get_actions below.
    vf.sync_greetings(request.session['domain_uuid'])

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
                    'mail_to', 'sms_to', 'attach_file', 'local_after_email', 'enabled', 'description'
                    ]}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('extension_id', 'mail_to', 'attach_file', 'local_after_email', 'enabled', 'description')
    list_filter = (VoicemailDomainFilter, 'enabled')

    ordering = [
        'extension_id__extension'
    ]
    actions = [sync_greeting_files]
    inlines = [VoicemailGreetingInLine, VoicemailOptionsInLine, VoicemailDestinationsInLine, VoicemailMessagesInLine]

    def get_actions(self, request):
        actns = super().get_actions(request)
        if not settings.PBX_USE_MOD_VOICEMAIL:
            del actns['sync_greeting_files']
        return actns

    def has_add_permission(self, request):
        return False

    def get_formsets_with_inlines(self, request, obj=None):
        vma = CommonDestAction(request.session['domain_name'], request.session['domain_uuid'])
        option_param_choices = vma.get_action_choices(' ', True, 0b1011111111111111)
        vm_destination_choices = [('', '------')]
        qs = Voicemail.objects.filter(enabled='true', extension_id__domain_id_id=request.session['domain_uuid']).order_by('extension_id')
        for q in qs:
            vm_destination_choices.append((str(q.id), q.extension_id))
        for inline in self.get_inline_instances(request, obj):
            if type(inline) is VoicemailOptionsInLine:
                inline.form.Meta.widgets['option_param'].choices=option_param_choices
            if type(inline) is VoicemailDestinationsInLine:
                inline.form.Meta.widgets['voicemail_dest'].choices=vm_destination_choices
            yield inline.get_formset(request, obj), inline

    def save_formset(self, request, form, formset, change):
        if not settings.PBX_FREESWITCH_LOCAL:
            fal = FileAbsLayer()
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            if type(obj) is VoicemailGreeting or type(obj) is VoicemailMessages:
                if not settings.PBX_FREESWITCH_LOCAL:
                    fal.delete('/home/django-pbx/media/%s' % obj.filename.name, request.session['home_switch'])
                obj.filename.delete(save=False)
            obj.delete()
        for instance in instances:
            instance.updated_by = request.user.username
            instance.save()
            if type(instance) is VoicemailGreeting or type(instance) is VoicemailMessages:
                if not settings.PBX_FREESWITCH_LOCAL and settings.PBX_USE_MOD_VOICEMAIL:
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

    # This is a workaround to allow the admin action to be run without selecting any objects.
    # super checks for a valid UUID, so we pass a meaningless one because it is not actually used.
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and request.POST['action'] == 'sync_greeting_files':
            post = request.POST.copy()
            post.update({ACTION_CHECKBOX_NAME: 'cc30bc83-ccb8-4f27-a1d6-9340ae7de325'})
            request._set_post(post)
        return super(VoicemailAdmin, self).changelist_view(request, extra_context)


admin.site.register(Voicemail, VoicemailAdmin)
