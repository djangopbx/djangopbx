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

from django.urls import path
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'firewall_counters', views.FwCountersView, basename='fwcounters')
router.register(r'firewall_white_ipv4_list', views.FwWhiteIpv4View, basename='fwwhiteipv4')
router.register(r'firewall_white_ipv6_list', views.FwWhiteIpv6View, basename='fwwhiteipv6')
router.register(r'firewall_sip_gateway_ipv4_list', views.FwSipGatewayIpv4View, basename='fwsipgatewayipv4')
router.register(r'firewall_sip_gateway_ipv6_list', views.FwSipGatewayIpv6View, basename='fwsipgatewayipv6')
router.register(r'firewall_sip_customer_ipv4_list', views.FwSipCustomerIpv4View, basename='fwsipcustomeripv4')
router.register(r'firewall_sip_customer_ipv6_list', views.FwSipCustomerIpv6View, basename='fwsipcustomeripv6')
router.register(r'firewall_web_block_ipv4_list', views.FwWebBlockIpv4View, basename='fwwebblockipv4')
router.register(r'firewall_web_block_ipv6_list', views.FwWebBlockIpv6View, basename='fwwebblockipv6')
router.register(r'firewall_block_ipv4_list', views.FwBlockIpv4View, basename='fwblockipv4')
router.register(r'firewall_block_ipv6_list', views.FwBlockIpv6View, basename='fwblockipv6')


urlpatterns = [
    path('fwlistcounters/', views.fwlistcounters, name='fwlistcounters'),
    path('fwblocklist/', views.fwblocklist, name='fwblocklist'),
    path('fwwhitelist/', views.fwwhitelist, name='fwwhitelist'),
    path('fwsipcustomerlist/', views.fwsipcustomerlist, name='fwsipcustomerlist'),
    path('fwsipgatewaylist/', views.fwsipgatewaylist, name='fwsipgatewaylist'),
    path('fwwebblocklist/', views.fwwebblocklist, name='fwwebblocklist'),
    path('fwconfigviewer/', views.fwconfigviewer, name='fwconfigviewer'),
    path('fwaddip/', views.fwaddip, name='fwaddip'),
    path('fwdelip/', views.fwdelip, name='fwdelip'),
]
