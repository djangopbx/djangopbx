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
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'devicevendors', views.DeviceVendorsViewSet)
router.register(r'devicevendorfunctions', views.DeviceVendorFunctionsViewSet)
router.register(r'devicevendorfunctiongroups', views.DeviceVendorFunctionGroupsViewSet)
router.register(r'deviceprofiles', views.DeviceProfilesViewSet)
router.register(r'deviceprofilesettings', views.DeviceProfileSettingsViewSet)
router.register(r'deviceprofilekeys', views.DeviceProfileKeysViewSet)
router.register(r'devices', views.DevicesViewSet)
router.register(r'devicelines', views.DeviceLinesViewSet)
router.register(r'devicekeys', views.DeviceKeysViewSet)
router.register(r'devicesettings', views.DeviceSettingsViewSet)


urlpatterns = [
    re_path(r'^device_config/(?P<mac>[A-Fa-f0-9]{12})\.(xml|cfg)$', views.device_config, name='deviceconfig'),
    re_path(r'^device_config/(?P<macboot>[A-Fa-f0-9]{12})\.boot$', views.device_config, name='deviceconfig'),
    re_path(r'^device_config/(?P<file>y[0-9]{12}\.cfg)$', views.device_config, name='deviceconfig'),
    re_path(r'^device_config/(?P<file>y0{12}\.boot)$', views.device_config, name='deviceconfig'),
    re_path(r'^device_config/contacts/(?P<contacts>(users|groups|extensions))/(?P<file>directory\.xml)$', views.device_config, name='deviceconfig'),
    re_path(r'^device_config/(?P<file>favorite_setting\.(xml|cfg))$', views.device_config, name='deviceconfig'),
    re_path(r'^device_config/(?P<file>super_search\.(xml|cfg))$', views.device_config, name='deviceconfig'),
]
