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

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required

from .models import (
    Menu, MenuItem, MenuItemGroup,
)

from .serializers import (
    MenuItemSerializer,
)


@login_required
def index(request):

    m = Menu.objects.get(name = 'Default')

    if request.user.is_superuser:
        menuList = MenuItem.objects.filter(menu_id = m.id, parent_id__isnull=True).order_by('sequence')
        submenuList = MenuItem.objects.filter(menu_id = m.id, parent_id__isnull=False).order_by('sequence')
    else:
        groupList = list(request.user.groups.values_list('name', flat=True))
        menuitemList = MenuItemGroup.objects.values_list('menu_item_uuid', flat=True).filter(name__in=groupList, menu_id=m.id)
        menuList = MenuItem.objects.filter(menu_id = m.id, parent_id__isnull=True, id__in=menuitemList).order_by('sequence')
        submenuList = MenuItem.objects.filter(menu_id = m.id, parent_id__isnull=False, id__in=menuitemList).order_by('sequence')

    mainmenu = MenuItemSerializer(menuList, many=True)
    menudata = mainmenu.data
    request.session['portalmenu'] = menudata

    submenu = MenuItemSerializer(submenuList, many=True)
    submenudata = submenu.data
    request.session['portalsubmenu'] = submenudata

    return render(request, 'portal/index.html', {})


