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

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from rest_framework import viewsets
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend

from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    Contact, ContactTel, ContactEmail, ContactGeo, ContactUrl, ContactOrg, ContactAddress, 
    ContactDate, ContactCategory, ContactGroup,
)
from tenants.models import Profile, Domain
from .serializers import (
    ContactSerializer, ContactTelSerializer, ContactEmailSerializer, ContactGeoSerializer,
    ContactUrlSerializer, ContactOrgSerializer, ContactAddressSerializer,
    ContactDateSerializer, ContactCategorySerializer, ContactGroupSerializer,
)
from django.utils.decorators import method_decorator
from django_tables2 import Table, SingleTableMixin, LazyPaginator
from django_filters.views import FilterView
import django_filters as filters
from django.utils.html import format_html

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404


class ContactViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Contacts to be viewed or edited.
    """
    queryset = Contact.objects.all().order_by('fn')
    serializer_class = ContactSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'user_id', 'family_name', 'fn', 'nickname', 'enabled']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactTelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ContactTel to be viewed or edited.
    """
    queryset = ContactTel.objects.all().order_by('number')
    serializer_class = ContactTelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contact_id', 'tel_type', 'number']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactEmailViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ContactEmail to be viewed or edited.
    """
    queryset = ContactEmail.objects.all().order_by('email')
    serializer_class = ContactEmailSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contact_id', 'email_type']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactGeoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ContactGeo to be viewed or edited.
    """
    queryset = ContactGeo.objects.all().order_by('geo_uri')
    serializer_class = ContactGeoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contact_id',]
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactUrlViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ContactUrl to be viewed or edited.
    """
    queryset = ContactUrl.objects.all().order_by('url_uri')
    serializer_class = ContactUrlSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contact_id',]
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactOrgViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ContactOrg to be viewed or edited.
    """
    queryset = ContactOrg.objects.all().order_by('organisation_name')
    serializer_class = ContactOrgSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contact_id',]
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactAddressViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ContactAddress to be viewed or edited.
    """
    queryset = ContactAddress.objects.all().order_by('postal_code')
    serializer_class = ContactAddressSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contact_id', 'locality', 'region']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactDateViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ContactDate to be viewed or edited.
    """
    queryset = ContactDate.objects.all().order_by('contact_id')
    serializer_class = ContactDateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['label', 'sig_date']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ContactCategory to be viewed or edited.
    """
    queryset = ContactCategory.objects.all().order_by('category')
    serializer_class = ContactCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contact_id', 'category']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ContactGroup to be viewed or edited.
    """
    queryset = ContactGroup.objects.all().order_by('name')
    serializer_class = ContactGroupSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['contact_id', 'group_id']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]


class ContactListFilter(filters.FilterSet):
    fn = filters.CharFilter(lookup_expr='icontains')
    family_name = filters.CharFilter(lookup_expr='icontains')
    given_name = filters.CharFilter(lookup_expr='icontains')
    additional_name = filters.CharFilter(lookup_expr='icontains')
    nickname = filters.CharFilter(lookup_expr='icontains')
    notes = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Contact
        fields = [
            'honorific_prefix',
            'family_name',
            'given_name',
            'nickname',
            'enabled'
            ]


class ContactListList(Table):
    class Meta:
        model = Contact
        attrs = {"class": "paleblue"}
        fields = (
            'honorific_prefix',
            'family_name',
            'given_name',
            'nickname',
            'enabled'
            )
        order_by = 'family_name'

    def render_family_name(self, value, record):
        return format_html('<a href=\"/contacts/contactedit/{}/\">{}</a>', record.id, value)

    def render_enabled(self, value, record):
        return format_html(self.checkbox_conversion(value))

    def checkbox_conversion(self, value):
        if value == 'True':
            return '<i class=\"fa fa-check\"></i>'
        else:
            return '<i class=\"fa fa-times\"></i>'


@method_decorator(login_required, name='dispatch')
class ContactList(SingleTableMixin, FilterView):
    table_class = ContactListList
    filterset_class = ContactListFilter
    paginator_class = LazyPaginator

    table_pagination = {
        "per_page": 25
    }

    def get_queryset(self):
        if self.request.user.is_superuser:
            qs = Contact.objects.filter(domain_id=self.request.session['domain_uuid'])
        else:
            qs = Contact.objects.filter((Q(user_id__user_uuid=self.request.session['user_uuid']) | Q(user_id__isnull=True)),
                (Q(contactgroup__group_id__in=self.request.user.groups.all()) | Q(contactgroup__group_id__isnull=True)),
                domain_id=self.request.session['domain_uuid'],
                )
        return qs


class ContactAdd(LoginRequiredMixin, CreateView):
    template_name = "contacts/contact_add.html"
    model = Contact
    fields = [
            'user_id',
            'family_name',
            'given_name',
            'additional_name',
            'honorific_prefix',
            'honorific_suffix',
            'nickname',
            'timezone',
            'notes',
            'enabled'
            ]
    success_url = '/contacts/contactlist/'

    def dispatch(self, request, *args, **kwargs):
        self.domain = get_object_or_404(Domain, pk=self.request.session['domain_uuid'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.domain_id = self.domain
        form.instance.updated_by = self.request.user.username
        form.instance.fn = '%s %s %s %s %s' % (
            form.instance.honorific_prefix if form.instance.honorific_prefix else '',
            form.instance.given_name if form.instance.given_name else '',
            form.instance.additional_name if form.instance.additional_name else '',
            form.instance.family_name if form.instance.family_name else '',
            form.instance.honorific_suffix if form.instance.honorific_suffix else '',
                                )
        form.instance.fn = form.instance.fn.replace('  ', ' ').strip()
        if not form.instance.enabled:
            form.instance.enabled = 'false'
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        form.fields['user_id'].queryset = Profile.objects.filter(domain_id=self.request.session['domain_uuid'])
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contactadd'
        context['back'] = '/contacts/contactlist/'
        return context


class ContactEdit(LoginRequiredMixin, UpdateView):
    template_name = "contacts/contact_edit.html"
    model = Contact
    fields = [
            'user_id',
            'family_name',
            'given_name',
            'additional_name',
            'honorific_prefix',
            'honorific_suffix',
            'nickname',
            'timezone',
            'notes',
            'enabled'
            ]
    success_url = '/contacts/contactlist/'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.username
        form.instance.fn = '%s %s %s %s %s' % (
            form.instance.honorific_prefix if form.instance.honorific_prefix else '',
            form.instance.given_name if form.instance.given_name else '',
            form.instance.additional_name if form.instance.additional_name else '',
            form.instance.family_name if form.instance.family_name else '',
            form.instance.honorific_suffix if form.instance.honorific_suffix else '',
                                )
        form.instance.fn = form.instance.fn.replace('  ', ' ').strip()

        if not form.instance.enabled:
            form.instance.enabled = 'false'
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        form.fields['user_id'].queryset = Profile.objects.filter(domain_id=self.request.session['domain_uuid'])
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contactedit'
        context['back'] = '/contacts/contactlist/'
        context['c_tel'] = self.get_c_contacttel()
        context['c_tel_e_url'] = '/contacts/contactteledit/'
        context['c_tel_a_url'] = '/contacts/contactteladd/%s/' % str(self.object.id)
        context['c_tel_d_url'] = '/contacts/contactteldel/'
        context['c_tel_g_url'] = '/portal/clickdial/'
        context['c_adr'] = self.get_c_contactaddress()
        context['c_adr_e_url'] = '/contacts/contactaddressedit/'
        context['c_adr_a_url'] = '/contacts/contactaddressadd/%s/' % str(self.object.id)
        context['c_adr_d_url'] = '/contacts/contactaddressdel/'
        context['c_eml'] = self.get_c_contactemail()
        context['c_eml_e_url'] = '/contacts/contactemailedit/'
        context['c_eml_a_url'] = '/contacts/contactemailadd/%s/' % str(self.object.id)
        context['c_eml_d_url'] = '/contacts/contactemaildel/'
        context['c_eml_g_url'] = 'mailto:'
        context['c_url'] = self.get_c_contacturl()
        context['c_url_e_url'] = '/contacts/contacturledit/'
        context['c_url_a_url'] = '/contacts/contacturladd/%s/' % str(self.object.id)
        context['c_url_d_url'] = '/contacts/contacturldel/'
        context['c_url_g_url'] = 'https://'
        context['c_org'] = self.get_c_contactorg()
        context['c_org_e_url'] = '/contacts/contactorgedit/'
        context['c_org_a_url'] = '/contacts/contactorgadd/%s/' % str(self.object.id)
        context['c_org_d_url'] = '/contacts/contactorgdel/'
        context['c_geo'] = self.get_c_contactgeo()
        context['c_geo_e_url'] = '/contacts/contactgeoedit/'
        context['c_geo_a_url'] = '/contacts/contactgeoadd/%s/' % str(self.object.id)
        context['c_geo_d_url'] = '/contacts/contactgeodel/'
        context['c_geo_g_url'] = 'https://'
        context['c_dte'] = self.get_c_contactdate()
        context['c_dte_e_url'] = '/contacts/contactdateedit/'
        context['c_dte_a_url'] = '/contacts/contactdateadd/%s/' % str(self.object.id)
        context['c_dte_d_url'] = '/contacts/contactdatedel/'
        context['c_cat'] = self.get_c_contactcategory()
        context['c_cat_e_url'] = '/contacts/contactcategoryedit/'
        context['c_cat_a_url'] = '/contacts/contactcategoryadd/%s/' % str(self.object.id)
        context['c_cat_d_url'] = '/contacts/contactcategorydel/'
        context['c_grp'] = self.get_c_contactgroup()
        context['c_grp_e_url'] = '/contacts/contactgroupedit/'
        context['c_grp_a_url'] = '/contacts/contactgroupadd/%s/' % str(self.object.id)
        context['c_grp_d_url'] = '/contacts/contactgroupdel/'
        return context

    def get_c_contacttel(self):
        cdetail = {}
        cds = self.object.contacttel_set.all()
        for cd in cds:
            cdetail[cd.id] = {'Number': cd.number, 'Type': cd.tel_type.capitalize(), 'Speed dial': ('*0%s' % cd.speed_dial if cd.speed_dial else '')}
        return cdetail

    def get_c_contactaddress(self):
        cdetail = {}
        cds = self.object.contactaddress_set.all()
        for cd in cds:
            cdetail[cd.id] = {'Post Code': cd.postal_code, 'Type': cd.addr_type.capitalize(), 'Street': (cd.street_address if cd.street_address else '')}
        return cdetail

    def get_c_contactemail(self):
        cdetail = {}
        cds = self.object.contactemail_set.all()
        for cd in cds:
            cdetail[cd.id] = {'Email': cd.email, 'Type': cd.email_type.capitalize()}
        return cdetail

    def get_c_contacturl(self):
        cdetail = {}
        cds = self.object.contacturl_set.all()
        for cd in cds:
            cdetail[cd.id] = {'Url': cd.url_uri}
        return cdetail

    def get_c_contactorg(self):
        cdetail = {}
        cds = self.object.contactorg_set.all()
        for cd in cds:
            cdetail[cd.id] = {'Organisation Name': cd.organisation_name, 'Organisation Unit': cd.organisation_unit}
        return cdetail

    def get_c_contactgeo(self):
        cdetail = {}
        cds = self.object.contactgeo_set.all()
        for cd in cds:
            cdetail[cd.id] = {'Uri': cd.geo_uri}
        return cdetail

    def get_c_contactdate(self):
        cdetail = {}
        cds = self.object.contactdate_set.all()
        for cd in cds:
            cdetail[cd.id] = {'Label': cd.label, 'Significant Date': cd.sig_date}
        return cdetail

    def get_c_contactcategory(self):
        cdetail = {}
        cds = self.object.contactcategory_set.all()
        for cd in cds:
            cdetail[cd.id] = {'Category': cd.category}
        return cdetail

    def get_c_contactgroup(self):
        cdetail = {}
        cds = self.object.contactgroup_set.all()
        for cd in cds:
            cdetail[cd.id] = {'Group': cd.group_id}
        return cdetail


class ContactTelEdit(LoginRequiredMixin, UpdateView):
    template_name = "generic_edit.html"
    model = ContactTel
    fields = [
            'tel_type',
            'number',
            'speed_dial'
            ]

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contactteledit'
        context['listicon'] = 'fa fa-phone'
        context['title'] = 'Update Number'
        context['back'] = '/contacts/contactedit/%s/' % str(self.object.contact_id_id)
        return context


class ContactTelAdd(LoginRequiredMixin, CreateView):
    template_name = "generic_add.html"
    model = ContactTel
    fields = [
            'tel_type',
            'number',
            'speed_dial'
            ]

    def dispatch(self, request, *args, **kwargs):
        self.contact = get_object_or_404(Contact, pk=kwargs['contact_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def form_valid(self, form):
        form.instance.contact_id = self.contact
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_arg'] = str(self.contact.id)
        context['url_name'] = 'contactteladd'
        context['listicon'] = 'fa fa-phone'
        context['title'] = 'Add Number'
        context['back'] = '/contacts/contactedit/%s/' % str(self.contact.id)
        return context


class ContactTelDel(LoginRequiredMixin, DeleteView):
    template_name = "generic_del.html"
    model = ContactTel

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contactteldel'
        context['listicon'] = 'fa fa-phone'
        context['title'] = 'Delete Number'
        context['back'] = '/contacts/contactedit/%s/' % str(self.object.contact_id_id)
        return context


class ContactAddressEdit(LoginRequiredMixin, UpdateView):
    template_name = "generic_edit.html"
    model = ContactAddress
    fields = [
            'addr_type',
            'post_office_box',
            'extended_address',
            'street_address',
            'locality',
            'region',
            'postal_code',
            'country_name'
            ]

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contactaddressedit'
        context['listicon'] = 'fa fa-university'
        context['title'] = 'Update Address'
        context['back'] = '/contacts/contactedit/%s/' % str(self.object.contact_id_id)
        return context


class ContactAddressAdd(LoginRequiredMixin, CreateView):
    template_name = "generic_add.html"
    model = ContactAddress
    fields = [
            'addr_type',
            'post_office_box',
            'extended_address',
            'street_address',
            'locality',
            'region',
            'postal_code',
            'country_name'
            ]

    def dispatch(self, request, *args, **kwargs):
        self.contact = get_object_or_404(Contact, pk=kwargs['contact_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def form_valid(self, form):
        form.instance.contact_id = self.contact
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_arg'] = str(self.contact.id)
        context['url_name'] = 'contactaddressadd'
        context['listicon'] = 'fa fa-university'
        context['title'] = 'Add Address'
        context['back'] = '/contacts/contactedit/%s/' % str(self.contact.id)
        return context


class ContactAddressDel(LoginRequiredMixin, DeleteView):
    template_name = "generic_del.html"
    model = ContactAddress

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contactaddressdel'
        context['listicon'] = 'fa fa-university'
        context['title'] = 'Delete Address'
        context['back'] = '/contacts/contactedit/%s/' % str(self.object.contact_id_id)
        return context


class ContactEmailEdit(LoginRequiredMixin, UpdateView):
    template_name = "generic_edit.html"
    model = ContactEmail
    fields = [
            'email_type',
            'email',
            ]

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contactemailedit'
        context['listicon'] = 'fa fa-envelope'
        context['title'] = 'Update Email'
        context['back'] = '/contacts/contactedit/%s/' % str(self.object.contact_id_id)
        return context


class ContactEmailAdd(LoginRequiredMixin, CreateView):
    template_name = "generic_add.html"
    model = ContactEmail
    fields = [
            'email_type',
            'email',
            ]

    def dispatch(self, request, *args, **kwargs):
        self.contact = get_object_or_404(Contact, pk=kwargs['contact_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def form_valid(self, form):
        form.instance.contact_id = self.contact
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_arg'] = str(self.contact.id)
        context['url_name'] = 'contactemailadd'
        context['listicon'] = 'fa fa-envelope'
        context['title'] = 'Add Email'
        context['back'] = '/contacts/contactedit/%s/' % str(self.contact.id)
        return context


class ContactEmailDel(LoginRequiredMixin, DeleteView):
    template_name = "generic_del.html"
    model = ContactEmail

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contactemaildel'
        context['listicon'] = 'fa fa-envelope'
        context['title'] = 'Delete Email'
        context['back'] = '/contacts/contactedit/%s/' % str(self.object.contact_id_id)
        return context


class ContactUrlEdit(LoginRequiredMixin, UpdateView):
    template_name = "generic_edit.html"
    model = ContactUrl
    fields = [
            'url_uri'
            ]

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contacturledit'
        context['listicon'] = 'fa fa-anchor'
        context['title'] = 'Update URL'
        context['back'] = '/contacts/contactedit/%s/' % str(self.object.contact_id_id)
        return context


class ContactUrlAdd(LoginRequiredMixin, CreateView):
    template_name = "generic_add.html"
    model = ContactUrl
    fields = [
            'url_uri'
            ]

    def dispatch(self, request, *args, **kwargs):
        self.contact = get_object_or_404(Contact, pk=kwargs['contact_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def form_valid(self, form):
        form.instance.contact_id = self.contact
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_arg'] = str(self.contact.id)
        context['url_name'] = 'contacturladd'
        context['listicon'] = 'fa fa-anchor'
        context['title'] = 'Add url'
        context['back'] = '/contacts/contactedit/%s/' % str(self.contact.id)
        return context


class ContactUrlDel(LoginRequiredMixin, DeleteView):
    template_name = "generic_del.html"
    model = ContactUrl

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contacturldel'
        context['listicon'] = 'fa fa-anchor'
        context['title'] = 'Delete url'
        context['back'] = '/contacts/contactedit/%s/' % str(self.object.contact_id_id)
        return context


class ContactOrgEdit(LoginRequiredMixin, UpdateView):
    template_name = "generic_edit.html"
    model = ContactOrg
    fields = [
            'organisation_name',
            'organisation_unit'
            ]

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contactorgedit'
        context['listicon'] = 'fa fa-industry'
        context['title'] = 'Update Organisation'
        context['back'] = '/contacts/contactedit/%s/' % str(self.object.contact_id_id)
        return context


class ContactOrgAdd(LoginRequiredMixin, CreateView):
    template_name = "generic_add.html"
    model = ContactOrg
    fields = [
            'organisation_name',
            'organisation_unit'
            ]

    def dispatch(self, request, *args, **kwargs):
        self.contact = get_object_or_404(Contact, pk=kwargs['contact_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def form_valid(self, form):
        form.instance.contact_id = self.contact
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_arg'] = str(self.contact.id)
        context['url_name'] = 'contactorgadd'
        context['listicon'] = 'fa fa-industry'
        context['title'] = 'Add Organisation'
        context['back'] = '/contacts/contactedit/%s/' % str(self.contact.id)
        return context


class ContactOrgDel(LoginRequiredMixin, DeleteView):
    template_name = "generic_del.html"
    model = ContactOrg

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contactorgdel'
        context['listicon'] = 'fa fa-industry'
        context['title'] = 'Delete Organisation'
        context['back'] = '/contacts/contactedit/%s/' % str(self.object.contact_id_id)
        return context


class ContactGeoEdit(LoginRequiredMixin, UpdateView):
    template_name = "generic_edit.html"
    model = ContactGeo
    fields = [
            'geo_uri'
            ]

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contactgeoedit'
        context['listicon'] = 'fa fa-map-marker'
        context['title'] = 'Update Geographic URI'
        context['back'] = '/contacts/contactedit/%s/' % str(self.object.contact_id_id)
        return context


class ContactGeoAdd(LoginRequiredMixin, CreateView):
    template_name = "generic_add.html"
    model = ContactGeo
    fields = [
            'geo_uri'
            ]

    def dispatch(self, request, *args, **kwargs):
        self.contact = get_object_or_404(Contact, pk=kwargs['contact_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def form_valid(self, form):
        form.instance.contact_id = self.contact
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_arg'] = str(self.contact.id)
        context['url_name'] = 'contactgeoadd'
        context['listicon'] = 'fa fa-map-marker'
        context['title'] = 'Add Geographic URI'
        context['back'] = '/contacts/contactedit/%s/' % str(self.contact.id)
        return context


class ContactGeoDel(LoginRequiredMixin, DeleteView):
    template_name = "generic_del.html"
    model = ContactGeo

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contactgeodel'
        context['listicon'] = 'fa fa-map-marker'
        context['title'] = 'Delete Geographic URI'
        context['back'] = '/contacts/contactedit/%s/' % str(self.object.contact_id_id)
        return context


class ContactDateEdit(LoginRequiredMixin, UpdateView):
    template_name = "generic_edit.html"
    model = ContactDate
    fields = [
            'label',
            'sig_date'
            ]

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contactdateedit'
        context['listicon'] = 'fa fa-calendar'
        context['title'] = 'Update Significant Date'
        context['back'] = '/contacts/contactedit/%s/' % str(self.object.contact_id_id)
        return context


class ContactDateAdd(LoginRequiredMixin, CreateView):
    template_name = "generic_add.html"
    model = ContactDate
    fields = [
            'label',
            'sig_date'
            ]

    def dispatch(self, request, *args, **kwargs):
        self.contact = get_object_or_404(Contact, pk=kwargs['contact_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def form_valid(self, form):
        form.instance.contact_id = self.contact
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_arg'] = str(self.contact.id)
        context['url_name'] = 'contactdateadd'
        context['listicon'] = 'fa fa-calendar'
        context['title'] = 'Add Significant Date'
        context['back'] = '/contacts/contactedit/%s/' % str(self.contact.id)
        return context


class ContactDateDel(LoginRequiredMixin, DeleteView):
    template_name = "generic_del.html"
    model = ContactDate

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contactdatedel'
        context['listicon'] = 'fa fa-calendar'
        context['title'] = 'Delete Significant Date'
        context['back'] = '/contacts/contactedit/%s/' % str(self.object.contact_id_id)
        return context


class ContactCategoryEdit(LoginRequiredMixin, UpdateView):
    template_name = "generic_edit.html"
    model = ContactCategory
    fields = [
            'category'
            ]

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contactcategoryedit'
        context['listicon'] = 'fa fa-book'
        context['title'] = 'Update Category'
        context['back'] = '/contacts/contactedit/%s/' % str(self.object.contact_id_id)
        return context


class ContactCategoryAdd(LoginRequiredMixin, CreateView):
    template_name = "generic_add.html"
    model = ContactCategory
    fields = [
            'category'
            ]

    def dispatch(self, request, *args, **kwargs):
        self.contact = get_object_or_404(Contact, pk=kwargs['contact_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def form_valid(self, form):
        form.instance.contact_id = self.contact
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_arg'] = str(self.contact.id)
        context['url_name'] = 'contactcategoryadd'
        context['listicon'] = 'fa fa-book'
        context['title'] = 'Add Category'
        context['back'] = '/contacts/contactedit/%s/' % str(self.contact.id)
        return context


class ContactCategoryDel(LoginRequiredMixin, DeleteView):
    template_name = "generic_del.html"
    model = ContactCategory

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contactcategorydel'
        context['listicon'] = 'fa fa-book'
        context['title'] = 'Delete Category'
        context['back'] = '/contacts/contactedit/%s/' % str(self.object.contact_id_id)
        return context


class ContactGroupEdit(LoginRequiredMixin, UpdateView):
    template_name = "generic_edit.html"
    model = ContactGroup
    fields = [
            'group_id'
            ]

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        if not self.request.user.is_superuser:
            form.fields['group_id'].queryset = self.request.user.groups.all()
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contactgroupedit'
        context['listicon'] = 'fa fa-Users'
        context['title'] = 'Update Group'
        context['back'] = '/contacts/contactedit/%s/' % str(self.object.contact_id_id)
        return context


class ContactGroupAdd(LoginRequiredMixin, CreateView):
    template_name = "generic_add.html"
    model = ContactGroup
    fields = [
            'group_id'
            ]

    def dispatch(self, request, *args, **kwargs):
        self.contact = get_object_or_404(Contact, pk=kwargs['contact_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def form_valid(self, form):
        form.instance.contact_id = self.contact
        form.instance.updated_by = self.request.user.username
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for key, f in form.fields.items():
            f.widget.attrs['class'] = 'form-control form-control-sm'
        if not self.request.user.is_superuser:
            form.fields['group_id'].queryset = self.request.user.groups.all()
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_arg'] = str(self.contact.id)
        context['url_name'] = 'contactgroupadd'
        context['listicon'] = 'fa fa-users'
        context['title'] = 'Add Group'
        context['back'] = '/contacts/contactedit/%s/' % str(self.contact.id)
        return context


class ContactGroupDel(LoginRequiredMixin, DeleteView):
    template_name = "generic_del.html"
    model = ContactGroup

    def get_success_url(self):
        return '/contacts/contactedit/%s/' % str(self.object.contact_id_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_name'] = 'contactgroupdel'
        context['listicon'] = 'fa fa-users'
        context['title'] = 'Delete Group'
        context['back'] = '/contacts/contactedit/%s/' % str(self.object.contact_id_id)
        return context
