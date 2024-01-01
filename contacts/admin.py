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

import re
from django.contrib import admin
from .models import (
    Contact, ContactTel, ContactEmail, ContactGeo, ContactUrl, ContactOrg,
    ContactAddress, ContactDate, ContactCategory, ContactGroup
)
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.conf import settings
from pbx.commonfunctions import DomainFilter, DomainUtils


class ContactTelResource(resources.ModelResource):
    class Meta:
        model = ContactTel
        import_id_fields = ('id', )


class ContactTelAdmin(ImportExportModelAdmin):
    resource_class = ContactTelResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['tel_type', 'number']
    fieldsets = [
        (None,  {'fields': ['contact_id', 'tel_type', 'number', 'speed_dial']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('tel_type', 'number')
    list_filter = ('tel_type',)
    ordering = [
        'number'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class ContactTelInLine(admin.TabularInline):
    model = ContactTel
    extra = 1
    fieldsets = [
        (None,          {'fields': ['tel_type', 'number', 'speed_dial']}),
    ]
    ordering = [
        'number'
    ]


class ContactEmailResource(resources.ModelResource):
    class Meta:
        model = ContactEmail
        import_id_fields = ('id', )


class ContactEmailAdmin(ImportExportModelAdmin):
    resource_class = ContactEmailResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['email_type', 'email']
    fieldsets = [
        (None,  {'fields': ['contact_id', 'email_type', 'email']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('email_type', 'email')
    list_filter = ('email_type',)
    ordering = [
        'email'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class ContactEmailInLine(admin.TabularInline):
    model = ContactEmail
    extra = 1
    fieldsets = [
        (None,          {'fields': ['email_type', 'email']}),
    ]
    ordering = [
        'email'
    ]


class ContactGeoResource(resources.ModelResource):
    class Meta:
        model = ContactGeo
        import_id_fields = ('id', )


class ContactGeoAdmin(ImportExportModelAdmin):
    resource_class = ContactGeoResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['geo_uri',]
    fieldsets = [
        (None,  {'fields': ['contact_id', 'geo_uri']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('geo_uri',)
    list_filter = ('geo_uri',)
    ordering = [
        'geo_uri'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class ContactGeoInLine(admin.TabularInline):
    model = ContactGeo
    extra = 1
    fieldsets = [
        (None,          {'fields': ['geo_uri',]}),
    ]
    ordering = [
        'geo_uri'
    ]


class ContactUrlResource(resources.ModelResource):
    class Meta:
        model = ContactUrl
        import_id_fields = ('id', )


class ContactUrlAdmin(ImportExportModelAdmin):
    resource_class = ContactUrlResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['url_uri',]
    fieldsets = [
        (None,  {'fields': ['contact_id', 'url_uri']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('url_uri',)
    list_filter = ('url_uri',)
    ordering = [
        'url_uri'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class ContactUrlInLine(admin.TabularInline):
    model = ContactUrl
    extra = 1
    fieldsets = [
        (None,          {'fields': ['url_uri',]}),
    ]
    ordering = [
        'url_uri'
    ]


class ContactOrgResource(resources.ModelResource):
    class Meta:
        model = ContactOrg
        import_id_fields = ('id', )


class ContactOrgAdmin(ImportExportModelAdmin):
    resource_class = ContactOrgResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['organisation_name', 'organisation_unit']
    fieldsets = [
        (None,  {'fields': ['contact_id', 'organisation_name', 'organisation_unit']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('organisation_name', 'organisation_unit')
    list_filter = ('organisation_name',)
    ordering = [
        'organisation_unit'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class ContactOrgInLine(admin.TabularInline):
    model = ContactOrg
    extra = 1
    fieldsets = [
        (None,          {'fields': ['organisation_name', 'organisation_unit']}),
    ]
    ordering = [
        'organisation_unit'
    ]


class ContactAddressResource(resources.ModelResource):
    class Meta:
        model = ContactAddress
        import_id_fields = ('id', )


class ContactAddressAdmin(ImportExportModelAdmin):
    resource_class = ContactAddressResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['street_address', 'locality', 'postal_code']
    fieldsets = [
        (None,  {'fields': ['contact_id', 'post_office_box', 'extended_address', 'street_address', 'locality',
                            'region', 'postal_code', 'country_name', 'addr_type']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('addr_type', 'postal_code', 'street_address')
    list_filter = ('postal_code', 'street_address', 'locality')
    ordering = [
        'postal_code'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class ContactAddressInLine(admin.TabularInline):
    model = ContactAddress
    extra = 1
    fieldsets = [
        (None,          {'fields': ['addr_type', 'street_address', 'locality', 'postal_code', 'region', 'post_office_box', 'country_name']}),
    ]
    ordering = [
        'postal_code'
    ]


class ContactDateResource(resources.ModelResource):
    class Meta:
        model = ContactDate
        import_id_fields = ('id', )


class ContactDateAdmin(ImportExportModelAdmin):
    resource_class = ContactDateResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['sig_date', 'label']
    fieldsets = [
        (None,  {'fields': ['contact_id', 'sig_date', 'label']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('sig_date', 'label')
    list_filter = ('sig_date',)
    ordering = [
        'label'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class ContactDateInLine(admin.TabularInline):
    model = ContactDate
    extra = 1
    fieldsets = [
        (None,          {'fields': ['sig_date', 'label']}),
    ]
    ordering = [
        'label'
    ]


class ContactCategoryResource(resources.ModelResource):
    class Meta:
        model = ContactCategory
        import_id_fields = ('id', )


class ContactCategoryAdmin(ImportExportModelAdmin):
    resource_class = ContactCategoryResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['category',]
    fieldsets = [
        (None,  {'fields': ['contact_id', 'category']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('category',)
    list_filter = ('category',)
    ordering = [
        'category'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class ContactCategoryInLine(admin.TabularInline):
    model = ContactCategory
    extra = 1
    fieldsets = [
        (None,          {'fields': ['category',]}),
    ]
    ordering = [
        'category'
    ]


class ContactGroupResource(resources.ModelResource):
    class Meta:
        model = ContactGroup
        import_id_fields = ('id', )


class ContactGroupAdmin(ImportExportModelAdmin):
    resource_class = ContactGroupResource
    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name',]
    fieldsets = [
        (None,  {'fields': ['contact_id', 'group_id', 'name']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name',)
    list_filter = ('name',)
    ordering = [
        'group_id'
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)


class ContactGroupInLine(admin.TabularInline):
    model = ContactGroup
    extra = 1
    fieldsets = [
        (None,          {'fields': ['group_id', 'name']}),
    ]
    ordering = [
        'name'
    ]


class ContactResource(resources.ModelResource):
    class Meta:
        model = Contact
        import_id_fields = ('id', )


class ContactAdmin(ImportExportModelAdmin):
    resource_class = ContactResource
    save_as = True

    class Media:
        css = {
            'all': ('css/custom_admin_tabularinline.css', )     # Include extra css to remove title from tabular inline
        }

    readonly_fields = ['fn', 'created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['fn', 'family_name', 'given_name', 'nickname']
    fieldsets = [
        (None,  {'fields': ['domain_id', 'user_id', 'fn', 'family_name', 'given_name', 'additional_name',
                            'honorific_prefix', 'honorific_suffix', 'nickname', 'timezone', 'enabled']}),
        ('Notes',   {'fields': ['notes',], 'classes': ['collapse']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('fn', 'given_name', 'family_name', 'nickname')
    list_filter = (DomainFilter, 'enabled', 'user_id')
    ordering = [
        'fn'
    ]
    inlines = [
        ContactTelInLine,
        ContactEmailInLine,
        ContactGeoInLine,
        ContactUrlInLine,
        ContactOrgInLine,
        ContactAddressInLine,
        ContactDateInLine,
        ContactCategoryInLine,
        ContactGroupInLine
    ]

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
        fn = '%s %s %s %s %s' % (
            obj.honorific_prefix if obj.honorific_prefix else '',
            obj.given_name if obj.given_name else '',
            obj.additional_name if obj.additional_name else '',
            obj.family_name if obj.family_name else '',
            obj.honorific_suffix if obj.honorific_suffix else '',
                                )
        obj.fn = re.sub('\s+', ' ', fn.strip())
        if not change:
            obj.domain_id = DomainUtils().domain_from_session(request)
        super().save_model(request, obj, form, change)



admin.site.register(Contact, ContactAdmin)

if settings.PBX_ADMIN_SHOW_ALL:
    admin.site.register(ContactTel, ContactTelAdmin)
    admin.site.register(ContactEmail, ContactEmailAdmin)
    admin.site.register(ContactGeo, ContactGeoAdmin)
    admin.site.register(ContactUrl, ContactUrlAdmin)
    admin.site.register(ContactOrg, ContactOrgAdmin)
    admin.site.register(ContactAddress, ContactAddressAdmin)
    admin.site.register(ContactDate, ContactDateAdmin)
    admin.site.register(ContactCategory, ContactCategoryAdmin)
    #admin.site.register(ContactGroup, ContactGroupAdmin)
