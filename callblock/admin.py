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
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect

from .models import (
    CallBlock
)
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from django.conf import settings
from django.forms import ModelForm, Select

from pbx.commonfunctions import DomainFilter, DomainUtils
from pbx.commondestination import CommonDestAction


class CallBlockAdminForm(ModelForm):

    class Meta:
        model = CallBlock
        widgets = {
            "data": Select(choices=[('', 'List unavailable')]),
        }
        fields = '__all__'


class CallBlockResource(resources.ModelResource):
    class Meta:
        model = CallBlock
        import_id_fields = ('id', )


class CallBlockAdmin(ImportExportModelAdmin):
    resource_class = CallBlockResource
    form = CallBlockAdminForm
    save_as = True

    readonly_fields = ['created', 'updated', 'synchronised', 'updated_by']
    search_fields = ['name', 'extension', 'description']
    fieldsets = [
        (None,  {'fields': ['domain_id', 'name', 'number', 'block_count', 'data',
                            'enabled', 'description']}),
        ('update Info.',   {'fields': ['created', 'updated', 'synchronised', 'updated_by'], 'classes': ['collapse']}),
    ]
    list_display = ('name', 'number', 'block_count', 'enabled', 'description')
    list_display_links = ('name', 'number')
    list_filter = (DomainFilter, )
    ordering = [
        'domain_id', 'name', 'number'
    ]

    def get_form(self, request, obj=None, change=False, **kwargs):
        cda = CommonDestAction(request.session['domain_name'], request.session['domain_uuid'])
        # this is required for access to the request object so the domain_name session
        # variable can be passed to the chioces function
        action_choices = [('respond:608',_('Reject')), ('respond:486',_('Busy'))]
        action_choices.extend(cda.get_action_choices(':', False, 0b0000100001100000))
        self.form.Meta.widgets['data'].choices = action_choices
        return super().get_form(request, obj, change, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user.username
        if not change:
            obj.domain_id = DomainUtils().domain_from_session(request)
            obj.context = request.session['domain_name']
        super().save_model(request, obj, form, change)



admin.site.register(CallBlock, CallBlockAdmin)
