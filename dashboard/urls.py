#
#    DjangoPBX
#
#    MIT License
#
#    Copyright (c) 2016 - 2024 Adrian Fretwell <adrian@djangopbx.com>
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

from rest_framework import routers
from django.urls import path
from . import views

router = routers.DefaultRouter()
router.register(r'config_stats', views.CfgStatsViewSet, basename='cfgstats')
router.register(r'switch_status', views.SwitchStatusViewSet, basename='switchstatus')
router.register(r'switch_live_traffic', views.SwitchLiveTrafficViewSet, basename='switchlivetraffic')
router.register(r'general_system_information', views.GeneralSystemInformationViewSet, basename='generalsysteminformation')
router.register(r'cpu_usage', views.CpuUsageViewSet, basename='cpuusage')
router.register(r'disk_i_o', views.DiskInputOutputViewSet, basename='diskio')
router.register(r'memory_usage', views.MemoryUsageViewSet, basename='memoryusage')
router.register(r'disk_info', views.DiskInfoViewSet, basename='diskinfo')
router.register(r'network_traffic', views.NetworkTrafficViewSet, basename='networktraffic')
router.register(r'network_traffic_by_interface', views.NetworkTrafficByInterfaceViewSet, basename='networktrafficbyinterface')

urlpatterns = [
    path('osdashboard/', views.osdashboard, name='osdashboard'),
    path('swdashboard/', views.swdashboard, name='swdashboard'),
    path('usrdashboard/', views.usrdashboard, name='usrdashboard'),
]
