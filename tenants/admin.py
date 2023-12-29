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

from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.template.response import TemplateResponse

from .models import (
    Profile, ProfileSetting, Domain, DomainSetting, DefaultSetting,
)
from .forms import CopySettingsToDomainForm
from import_export.admin import (
    ExportActionModelAdmin, ImportExportModelAdmin,
    ImportExportMixin, ExportMixin
    )
from import_export import resources

# includes for log entry
from django.contrib.admin.models import LogEntry, DELETION
from django.utils.html import escape
from django.urls import reverse
from django.utils.safestring import mark_safe

# includes for inport export on auth tables
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

# includes for REST Framework TokenAdmin (TokenAuthentication)
from rest_framework.authtoken.admin import TokenAdmin
TokenAdmin.raw_id_fields = ['user']
TokenAdmin.change_list_template = "api_token_admin_changelist.html"
TokenAdmin.change_form_template = "api_token_admin_changeform.html"

from dialplans.dialplanfunctions import SwitchDp
from pbx.commonfunctions import DomainFilter, DomainUtils
from django.contrib import messages


class UserResource(resources.ModelResource):
    class Meta:
        model = User


class UserAdmin(ImportExportMixin, UserAdmin):
    resource_class = UserResource


class GroupResource(resources.ModelResource):
    class Meta:
        model = Group


class GroupAdmin(ImportExportMixin, GroupAdmin):
    resource_class = GroupResource


#
# Provides a Log entry viewer to the admin site
#
class LogEntryResource(resources.ModelResource):

    class Meta:
        model = LogEntry


class LogEntryAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = LogEntryResource

    date_hierarchy = 'action_time'

    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]

    search_fields = [
        'object_repr',
        'change_message'
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        'action_flag',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = '<a href="%s">%s</a>' % (
                reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id]),
                escape(obj.object_repr),
            )
        return mark_safe(link)
    object_link.admin_order_field = "object_repr"
    object_link.short_description = "object"


class DomainSettingsDomainFilter(admin.SimpleListFilter):
    title = _('Category')
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        if 'domain_id__domain_id__exact' in request.GET:
            muuid = request.GET['domain_id__domain_id__exact']
            dpds = set([c.category for c in model_admin.model.objects.all().filter(domain_id=muuid)])
        else:
            dpds = set([c.category for c in model_admin.model.objects.all()])
        return [(s, s) for s in dpds]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category=self.value())


#
# Domain settings
#
class DomainSettingInLine(admin.TabularInline):
    model = DomainSetting
    extra = 3
    fieldsets = [
        (None,          {'fields': ['category', 'subcategory', 'value_type', 'value', 'sequence', 'enabled']}),
    ]
    ordering = ['category', 'subcategory', 'sequence']


class DomainSettingResource(resources.ModelResource):
    class Meta:
        model = DomainSetting
        import_id_fields = ('id', )


class DomainSettingAdmin(ImportExportModelAdmin):
    resource_class = DomainSettingResource
    save_as = True
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['category', 'subcategory', 'value_type', 'value']
    list_display = ('category', 'subcategory', 'value_type', 'value', 'enabled')
    list_filter = (DomainFilter, DomainSettingsDomainFilter, 'enabled')
    list_display_links = ('category', 'subcategory', 'value_type', 'value')
    fieldsets = [
        (None, {'fields': [
                'domain_id', 'category', 'subcategory', 'value_type', 'value',
                'sequence', 'enabled', 'description'
                ]}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    ordering = ['category', 'subcategory', 'sequence']

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


#
# Domain
#
class DomainResource(resources.ModelResource):

    class Meta:
        model = Domain
        import_id_fields = ('id', )


class DomainAdmin(ImportExportModelAdmin):
    resource_class = DomainResource

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'description']
    list_display = ('name', 'description', 'enabled', 'select_domain')
    list_filter = ('name', 'description', 'enabled')
    fieldsets = [
        (None,          {'fields': ['name', 'enabled', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    inlines = [DomainSettingInLine]

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
        if not change:
            SwitchDp().import_xml(obj.name, False, obj.id)  # Create dialplans
            DomainSetting.objects.create(
                domain_id=obj,   # Create default menu setting
                category='domain',
                subcategory='menu',
                value_type='text',
                value='Default',
                sequence=10,
                updated_by=request.user.username
                )


#
# Profile (user) Settings
#
class ProfileSettingInLine(admin.TabularInline):
    model = ProfileSetting
    extra = 3
    fieldsets = [
        (None, {'fields': ['category', 'subcategory', 'value_type', 'value', 'sequence', 'enabled']}),
    ]
    ordering = ['category', 'subcategory', 'sequence']


class ProfileSettingResource(resources.ModelResource):

    class Meta:
        model = ProfileSetting
        import_id_fields = ('id', )


class ProfileSettingAdmin(ImportExportModelAdmin):
    resource_class = ProfileSettingResource
    save_as = True
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['category', 'subcategory', 'value_type', 'value']
    list_display = ('category', 'subcategory', 'value_type', 'value', 'enabled')
    list_filter = ('user_id', 'category', 'enabled')
    list_display_links = ('category', 'subcategory', 'value_type', 'value')
    fieldsets = [
        (None, {'fields': [
                'user_id', 'category', 'subcategory', 'value_type', 'value', 'sequence',
                'enabled', 'description'
                ]}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    ordering = ['category', 'subcategory', 'sequence']

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class ProfileResource(resources.ModelResource):

    class Meta:
        model = Profile
        import_id_fields = ('id', )


#
# Profile (user)
#
class ProfileAdmin(ImportExportModelAdmin):
    resource_class = ProfileResource
    readonly_fields = ['username', 'email', 'created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['username', 'email']
    fieldsets = [
        (None, {'fields': ['domain_id', 'username', 'email', 'user']}),
        ('Status', {'fields': ['status', 'enabled', 'api_key'], 'classes': ['collapse']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]

    list_display = ('username', 'domain_id', 'email', 'enabled')
    list_filter = (DomainFilter, 'enabled')
    inlines = [ProfileSettingInLine]

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
        super().save_model(request, obj, form, change)


#
# Default Settings
#
class DefaultSettingResource(resources.ModelResource):

    class Meta:
        model = DefaultSetting
        import_id_fields = ('id', )


@admin.action(permissions=['change'], description=_('Copy selected to domain...'))
def copy_settings_to_domain(modeladmin, request, queryset):
    title = _("Copy settings?")
    opts = modeladmin.model._meta
    app_label = opts.app_label
    if 'apply' in request.POST:
        c = 0
        if not request.POST['domain']:
            return None
        d = Domain.objects.get(pk=request.POST['domain'])
        dss = request.POST.getlist('_selected_action')
        qs = DefaultSetting.objects.filter(id__in=dss)
        for q in qs:
            if DomainSetting.objects.filter(domain_id=d.id, category=q.category,
                subcategory=q.subcategory, enabled='true').exists():
                continue
            c += 1
            DomainSetting.objects.create(
                domain_id = d,
                category=q.category,
                subcategory=q.subcategory,
                value_type=q.value_type,
                value=q.value,
                sequence=q.sequence,
                enabled='true',
                description=q.description,
                updated_by=request.user.username
            )
        modeladmin.message_user(
            request,
            _('Successfully copied %s settings' % str(c)),
            messages.SUCCESS
        )
        # Return None to display the change list page again.
        return None
    form = CopySettingsToDomainForm(initial={'_selected_action': queryset.values_list('pk', flat=True)})
    request.current_app = modeladmin.admin_site.name
    return TemplateResponse(
        request,
        "admin/copy_settings_to_domain.html",
        {**modeladmin.admin_site.each_context(request), 'title': title,
        'items': queryset, 'form': form, 'opts': opts, 'media': modeladmin.media}
    )


class DefaultSettingAdmin(ImportExportModelAdmin, ExportActionModelAdmin):
    resource_class = DefaultSettingResource
    save_as = True
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['category', 'subcategory', 'value_type', 'value']
    list_display = ('category', 'subcategory', 'value_type', 'value', 'enabled')
    list_filter = ('category', 'enabled')
    list_display_links = ('category', 'subcategory', 'value_type', 'value')
    fieldsets = [
        (None, {'fields': ['category', 'subcategory', 'value_type', 'value', 'sequence', 'enabled', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    ordering = ['category', 'subcategory', 'sequence']
    actions = [copy_settings_to_domain]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(ProfileSetting, ProfileSettingAdmin)
admin.site.register(Domain, DomainAdmin)
admin.site.register(DomainSetting, DomainSettingAdmin)
admin.site.register(DefaultSetting, DefaultSettingAdmin)
admin.site.register(LogEntry, LogEntryAdmin)
