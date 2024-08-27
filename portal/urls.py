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

from django.urls import path, re_path
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'menus', views.MenuViewSet)
router.register(r'menu_items', views.MenuItemViewSet)
router.register(r'menu_item_groups', views.MenuItemGroupViewSet)


urlpatterns = [
    path('', views.index, name='index'),
    path('domainselect/', views.DomainSelector.as_view(), name='domainselect'),
    path('selectdomain/<domainuuid>/', views.selectdomain, name='selectdomain'),
    path(
        'favicon.ico',
        RedirectView.as_view(url=staticfiles_storage.url("favicon.ico")),
    ),
    re_path(
        r'^(?P<fullpath>(?P<fs>fs)/(?P<fdir>[A-Za-z0-9._-]+)/(?P<fpro>[A-Za-z0-9_-]+)/(?P<fdom>[A-Za-z0-9._-]+)/(?P<fext>[A-Za-z0-9._-]+)/(?P<fpath>[A-Za-z0-9._-]+))$', # noqa: E501, E221
        views.servefsmediavoicemail, name='servefsmediavoicemail'
        ),
    re_path(
        r'^(?P<fullpath>(?P<fs>fs)/(?P<fdir>[A-Za-z0-9._-]+)/(?P<fdom>[A-Za-z0-9._-]+)/(?P<fpath>[A-Za-z0-9._-]+))$', # noqa: E501, E221
        views.servefsmediarecordings, name='servefsmediarecordings'
        ),
    re_path(
        r'^(?P<fullpath>(?P<fs>fs)/(?P<fdir>[A-Za-z0-9._-]+)/(?P<fdom>[A-Za-z0-9._-]+)/archive/(?P<fyear>[0-9]{4})/(?P<fmon>[JFMASOND][a-z]{2})/(?P<fday>[0123][0-9])/(?P<fpath>[A-Za-z0-9._-]+))$', # noqa: E501, E221
        views.servefsmediarecordingsarchive, name='servefsmediarecordingsarchive'
        ),
#    re_path(
#        r'^(?P<fullpath>(?P<fs>fs)/(?P<fdir>.*)/(?P<fdom>.*)/(?P<fpath>.*))$',
#        views.servefsmedia, name='servefsmedia'
#        ),
    re_path(r'clickdial/(?P<dest>[A-Za-z0-9\.@]+)/', views.ClickDial.as_view(), name='clickdial'),
    re_path(r'clickdial/(?P<dest>[A-Za-z0-9\.@]+)/<host>/', views.ClickDial.as_view(), name='clickdial'),
    re_path(r'voicemail/(?P<vmid>[A-Fa-f0-9\-]+)_(?P<msgid>[A-Fa-f0-9\-]+)', views.VoicemailDownload.as_view(), name='voicemaildownload'), # noqa: E501, E221
    re_path(r'tmprecording/(?P<sessionid>[A-Fa-f0-9\-]+)_(?P<fileid>[A-Fa-f0-9\-]+\.[A-Za-z0-9]+)', views.TmpRecordingDownload.as_view(), name='tmprecoringdownload'), # noqa: E501, E221
    path('pbxlogout/', views.pbxlogout, name='pbxlogout'),
]
