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
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin, ExportActionModelAdmin
from import_export import resources


from .models import (
    Menu, MenuItem, MenuItemGroup, Failed_logins,
)


class MenuItemFilter(admin.SimpleListFilter):
    title = _('Parent')
    parameter_name = 'workarea'

    def lookups(self, request, model_admin):
        mitms = [(c.id, c.title) for c in MenuItem.objects.filter(parent_id__isnull=True).order_by('title')]
        return [('all', _('All')), ('top', _('Top Level ( - )'))] + mitms

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset.filter()
        if self.value() == 'top':
            return queryset.filter(parent_id__isnull=True)
        if not self.value() == 'all':
            return queryset.filter(parent_id=self.value())


class MenuItemGroupInLine(admin.TabularInline):
    model = MenuItemGroup
    extra = 3
    fieldsets = [
        (None,          {'fields': ['group_id']}),
    ]


class MenuItemResource(resources.ModelResource):
    class Meta:
        model = MenuItem
        import_id_fields = ('id', )


class MenuItemAdmin(ImportExportModelAdmin, ExportActionModelAdmin):
    resource_class = MenuItemResource
    save_as = True
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']

    fieldsets = [
        (None,          {'fields': [
            'menu_id', 'parent_id', 'title', 'link', 'icon', 'category', 'protected', 'sequence', 'description'
            ]}),
        ('Update Info.', {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    inlines = [MenuItemGroupInLine]
    list_display = ('menu_id', 'parent_id', 'title', 'link', 'sequence', 'description')
    list_filter = ('menu_id', MenuItemFilter,)
    list_display_links = ('menu_id', 'title')
    ordering = ['sequence']

    # Be careful with this.  It relates to the MenuItemGroup model
    #  if we had more inlines we would need to test for which inline we were dealing with.
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


class MenuItemInLine(admin.TabularInline):
    model = MenuItem
    extra = 3
    fieldsets = [
        (None,          {'fields': [
            'menu_id', 'parent_id', 'title', 'link', 'icon', 'category', 'protected', 'sequence'
            ]}),
    ]
    ordering = ['sequence']


class MenuResource(resources.ModelResource):
    class Meta:
        model = Menu
        import_id_fields = ('id', )


class MenuAdmin(ImportExportModelAdmin):
    resource_class = MenuResource
    save_as = True

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    fieldsets = [
        (None,               {'fields': ['name']}),
        ('Description', {'fields': ['description'], 'classes': ['collapse']}),
    ]
    inlines = [MenuItemInLine]

    # Be careful with this.  It relates to the MenuItemGroup model
    #  if we had more inlines we would need to test for which inline we were dealing with.
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


class MenuItemGroupResource(resources.ModelResource):
    class Meta:
        model = MenuItemGroup
        import_id_fields = ('id', )


class MenuItemGroupAdmin(ImportExportModelAdmin):
    resource_class = MenuItemGroupResource
    readonly_fields = ['name', 'created', 'updated', 'synchronised', 'updated_by']
    fieldsets = [
        (None,               {'fields': ['menu_item_id', 'name', 'group_id']}),
        ('Update Info.', {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'group_id', 'menu_item_id')

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class Failed_loginsResource(resources.ModelResource):
    class Meta:
        model = Failed_logins
        import_id_fields = ('id', )


class Failed_loginsAdmin(ImportExportModelAdmin):
    resource_class = Failed_loginsResource
    save_as = True

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['address']
    fieldsets = [
        (None,  {'fields': ['address', 'username', 'sttempts']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('address', 'username', 'attempts', 'created', 'updated')
    ordering = [
        'address'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        if change:
            messages.add_message(request, messages.WARN, _('A changed IP will not be added to Firewall automatically'))
        else:
            if ':' in obj.address:
                shcommand(["/usr/local/bin/fw-add-ipv6-web-block-list.sh", obj.address])
            else:
                shcommand(["/usr/local/bin/fw-add-ipv4-web-block-list.sh", obj.address])
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        if ':' in obj.address:
            shcommand(["/usr/local/bin/fw-delete-ipv6-web-block-list.sh", obj.address])
        else:
            shcommand(["/usr/local/bin/fw-delete-ipv4-web-block-list.sh", obj.address])
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if ':' in obj.address:
                shcommand(["/usr/local/bin/fw-delete-ipv6-web-block-list.sh", obj.address])
            else:
                shcommand(["/usr/local/bin/fw-delete-ipv4-web-block-list.sh", obj.address])
        super().delete_queryset(request, queryset)


admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(Failed_logins, Failed_loginsAdmin)

if settings.PBX_ADMIN_SHOW_ALL:
    admin.site.register(MenuItemGroup, MenuItemGroupAdmin)
