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

from django.utils.translation import gettext, gettext_lazy as _
from django.contrib import admin
from django.db import models
import tenants.models


class SelectedDomainFilter(admin.SimpleListFilter):
    title = _('Selected Domain')
    parameter_name = 'domain_selected'
    pbx_domain_uuid = 'f4b3b3d2-6287-489c-aa00-64529e46f2d7'
    pbx_domain_name = 'All'

    def lookups(self, request, model_admin):

        if 'domain_name' in request.session:
            self.pbx_domain_name = request.session['domain_name']
        if 'domain_uuid' in request.session:
            self.pbx_domain_uuid = request.session['domain_uuid']

        return [(c.id, c.name) for c in tenants.models.Domain.objects.all()] + [('Global', 'Global'), ('All', 'All')]

    def choices(self, cl):
        print(cl)
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.pbx_domain_uuid == str(lookup) or self.value() == str(lookup),
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }


    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'All':
                return queryset.all()
            elif self.value() == 'Global':
                return queryset.filter(domain_id__id__isnull=True)
            else:
                return queryset.filter(domain_id__id__exact=self.value())
        else:
            return queryset.filter(domain_id__id__exact=self.pbx_domain_uuid)

