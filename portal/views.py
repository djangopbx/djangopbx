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
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.http import HttpResponseNotFound
import django_tables2 as tables
from django_filters.views import FilterView
import django_filters as filters
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from django.http import FileResponse

from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    Menu, MenuItem, MenuItemGroup,
)
from tenants.models import (
    Domain,
)
from tenants.pbxsettings import (
    PbxSettings,
)
from .serializers import (
    MenuSerializer, MenuItemSerializer, MenuItemNavSerializer, MenuItemGroupSerializer,
)

from accounts.accountfunctions import AccountFunctions


@login_required
def index(request):
    dreload = True
    ureload = True
    local_message = _('Welcome to DjangoPBX')
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

            currentmenu = PbxSettings().settings(
                pbx_user_uuid, pbx_domain_uuid, 'domain', 'menu', 'text', 'Default', True )[0]
            m = Menu.objects.get(name=currentmenu)
        else:
            request.session['user_uuid'] = 'ffffffff-aaaa-489c-aa00-1234567890ab'
            request.session['extension_list'] = 'None,None'
            request.session['extension_list_uuid'] = 'ffffffff-aaaa-489c-aa00-1234567890ab,'
            m = Menu.objects.get(name='Default')

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

    return render(request, 'portal/index.html', {})


@login_required
@permission_required('tenants.domain.can_select_domain')
def selectdomain(request, domainuuid):
    d = Domain.objects.get(pk=domainuuid)
    request.session['domain_name'] = d.name
    request.session['domain_uuid'] = str(d.id)
    request.session['domain_change'] = 'yes'
    messages.add_message(request, messages.INFO, _('Selected Domain changed to ') + d.name)
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
