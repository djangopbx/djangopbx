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

import os
from django.conf import settings
from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.utils.http import url_has_allowed_host_and_scheme
from django.http import (
    HttpResponse, HttpResponseRedirect, HttpResponseNotFound, FileResponse
    )
from django.contrib import messages
import django_tables2 as tables
import django_filters as filters
from django_filters.views import FilterView
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    Menu, MenuItem, MenuItemGroup,
)
from tenants.models import (
    Domain,
)
from accounts.models import (
    Extension, ExtensionUser,
)
from tenants.pbxsettings import (
    PbxSettings,
)
from .serializers import (
    MenuSerializer, MenuItemSerializer, MenuItemNavSerializer, MenuItemGroupSerializer,
)

from accounts.accountfunctions import AccountFunctions
from switch.switchsounds import SwitchSounds
from pbx.fscmdabslayer import FsCmdAbsLayer


@login_required
def index(request):
    no_menu_links = []
    local_message = None
    s = PbxSettings()

    dreload = True
    ureload = True
    if 'domain_name' in request.session:
        pbx_domain_name = request.session['domain_name']
        dreload = False
    else:
        request.session['domain_name'] = 'None'

    if 'domain_uuid' in request.session:
        pbx_domain_uuid = request.session['domain_uuid']
        dreload = False
    else:
        request.session['domain_uuid'] = 'f4b3b3d2-6287-489c-aa00-64529e46f2d7'

    if 'domain_change' in request.session:
        if request.session['domain_change'] == 'yes':
            dreload = True
            ureload = False
            request.session['domain_change'] = 'no'
            local_message = _('Domain changed to: ') + request.session['domain_name']

    if dreload:
        brand = s.default_brand_settings()
        if request.user.profile.domain_id:
            brand = s.domain_brand_settings(brand, request.user.profile.domain_id.id)
        request.session['brand_footer'] = brand.get('footer_text', 'DjangoPBX &copy; Adrian Fretwell 2024')
        request.session['brand_logo'] = brand.get('logo', '/img/logo.png')
        request.session['brand_portal_text'] = brand.get('portal_text', 'DjangoPBX Portal')
        request.session['brand_portal_image'] = brand.get('portal_image', '/img/welcome.png')
        if not local_message:
            local_message = _(brand.get('welcome_message', 'Welcome to DjangoPBX'))

        messages.add_message(request, messages.INFO, local_message)
        if request.user.profile.domain_id:
            pbx_user_uuid = str(request.user.profile.user_uuid)
            if ureload:
                pbx_domain_name = request.user.profile.domain_id.name
                pbx_domain_uuid = str(request.user.profile.domain_id.id)
                request.session['domain_name'] = pbx_domain_name
                request.session['domain_uuid'] = pbx_domain_uuid
                request.session['user_uuid'] = pbx_user_uuid
                extension_list = []
                for ext in AccountFunctions().list_user_extensions_uuid(pbx_domain_uuid, pbx_user_uuid):
                    extension_list.append(str(ext))
                request.session['extension_list_uuid'] = ','.join(extension_list)
                extension_list = []
                for ext in AccountFunctions().list_user_extensions(pbx_domain_uuid, pbx_user_uuid):
                    extension_list.append(ext)
                request.session['extension_list'] = ','.join(extension_list)

            currentmenu = s.settings(
                pbx_user_uuid, pbx_domain_uuid, 'domain', 'menu', 'text', 'Default', True )[0]
            try:
                m = Menu.objects.get(name=currentmenu)
            except Menu.DoesNotExist:
                m = None
        else:
            request.session['user_uuid'] = 'ffffffff-aaaa-489c-aa00-1234567890ab'
            request.session['extension_list'] = 'None,None'
            request.session['extension_list_uuid'] = 'ffffffff-aaaa-489c-aa00-1234567890ab,'
            try:
                m = Menu.objects.get(name='Default')
            except Menu.DoesNotExist:
                m = None

        if m:
            if request.user.is_superuser:
                menuList = MenuItem.objects.filter(menu_id=m.id, parent_id__isnull=True).order_by('sequence')
                submenuList = MenuItem.objects.filter(menu_id=m.id, parent_id__isnull=False).order_by('sequence')
            else:
                groupList = list(request.user.groups.values_list('name', flat=True))
                menuitemList = MenuItemGroup.objects.values_list(
                    'menu_item_id', flat=True
                    ).filter(name__in=groupList, menu_item_id__menu_id=m.id)
                menuList = MenuItem.objects.filter(
                    menu_id=m.id, parent_id__isnull=True, id__in=menuitemList
                    ).order_by('sequence')
                submenuList = MenuItem.objects.filter(
                    menu_id=m.id, parent_id__isnull=False, id__in=menuitemList
                    ).order_by('sequence')

            mainmenu = MenuItemNavSerializer(menuList, many=True)
            menudata = mainmenu.data
            request.session['portalmenu'] = menudata

            submenu = MenuItemNavSerializer(submenuList, many=True)
            submenudata = submenu.data
            request.session['portalsubmenu'] = submenudata
        else:
            no_menu_links = ['/admin/','/portal/pbxlogout/']

        redirect_to = request.POST.get(
            'next', request.GET.get('next', '')
        )
        if redirect_to:
            if url_has_allowed_host_and_scheme(
                url=redirect_to,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return HttpResponseRedirect(redirect_to)

    return render(request, 'portal/index.html', {'nomenulinks': no_menu_links})


@login_required
@permission_required('tenants.domain.can_select_domain')
def selectdomain(request, domainuuid):
    d = Domain.objects.get(pk=domainuuid)
    request.session['domain_name'] = d.name
    request.session['domain_uuid'] = str(d.id)
    request.session['domain_change'] = 'yes'
    messages.add_message(request, messages.INFO, _('Selected Domain changed to ') + d.name)
    if request.META['HTTP_REFERER'].endswith('/admin/tenants/domain/'):
        return HttpResponseRedirect('/admin/')
    return HttpResponseRedirect('/')


@login_required
def servefsmedia(request, fs, fdir, fdom, fpath, fullpath):
    if not fs == 'fs':
        return HttpResponseNotFound()
    if not request.user.is_superuser:
        if fdir == 'recordings':
            if not fdom == request.session['domain_name']:
                return HttpResponseNotFound()
        if fdir == 'voicemail':
            if not fpath == request.session['domain_name']:
                return HttpResponseNotFound()

    file_location = '%s/%s' % (settings.MEDIA_ROOT, fullpath)
    if not os.path.exists(file_location):
        return HttpResponseNotFound()

    return FileResponse(open(file_location, 'rb'))


class DomainSelectorList(tables.Table):
    class Meta:
        model = Domain
        attrs = {"class": "paleblue"}
        fields = ('name', 'description')
        order_by = 'name'

    name = tables.Column(linkify=("selectdomain", [tables.A("id")]))


class DomainFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Domain
        fields = ['name', 'description', 'enabled']


class DomainSelector(tables.SingleTableMixin, FilterView):
    table_class = DomainSelectorList
    queryset = Domain.objects.all()
    filterset_class = DomainFilter


class MenuViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Menus to be viewed or edited.
    """
    queryset = Menu.objects.all().order_by('name')
    serializer_class = MenuSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class MenuItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Menu Items to be viewed or edited.
    """
    queryset = MenuItem.objects.all().order_by('menu_id', 'sequence')
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['parent_id', 'title']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class MenuItemGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Menus to be viewed or edited.
    """
    queryset = MenuItemGroup.objects.all().order_by('menu_item_id', 'name')
    serializer_class = MenuItemGroupSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['menu_item_id', 'name']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class ClickDial(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        c_vars = []
        dest = kwargs.get('dest', '')
        host = kwargs.get('host')
        if dest:
            ss = SwitchSounds()
            eu = ExtensionUser.objects.filter(user_uuid=request.user.profile.user_uuid, default_user='true').first()
            extn = eu.extension_id.extension
            context = eu.extension_id.user_context
            dest_exists = Extension.objects.filter(domain_id=request.session['domain_uuid'], extension=extn )
            c_vars.append('click_to_call=true')
            c_vars.append('origination_caller_id_name=%s' % eu.extension_id.effective_caller_id_name)
            c_vars.append('origination_caller_id_number=%s' % eu.extension_id.effective_caller_id_number)
            c_vars.append('outbound_caller_id_name=%s' % eu.extension_id.outbound_caller_id_name)
            c_vars.append('outbound_caller_id_number=%s' % eu.extension_id.outbound_caller_id_number)
            c_vars.append('instant_ringback=true')
            c_vars.append('ringback=%s' % ss.get_default_ringback())
            c_vars.append('presence_id=%s@%s' % (extn, request.session['domain_name']))
            c_vars.append('call_direction=%s' % ('local' if dest_exists else 'outbound'))
            if eu.extension_id.toll_allow:
                c_vars.append('toll_allow=%s' % eu.extension_id.toll_allow)

            ch_vars = '{%s}' % ','.join(c_vars)
            if '@' in dest:
                cmd = 'api originate %suser/%s@%s &bridge(%s/sofia/external/%s)' % (ch_vars, extn, context, ch_vars, dest)
            else:
                cmd = 'api originate %suser/%s@%s %s XML %s' % (ch_vars, extn, context, dest, context)

            es = FsCmdAbsLayer()
            if es.connect():
                es.clear_responses()
                if host:
                    es.send(cmd, host)
                else:
                    es.send(cmd)
                es.process_events()
                es.get_responses()
                es.disconnect()

        if request.META.get('HTTP_REFERER'):
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            return HttpResponse('')

@login_required
def pbxlogout(request):
    return render(request, 'portal/pbx_logout.html', {})
