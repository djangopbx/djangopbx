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
router.register(r'xmlcdrs', views.XmlCdrViewSet)

urlpatterns = [
    re_path(r'^xml_cdr_import/.*$', views.xml_cdr_import, name='xmlcdrimport'),
    path('cdrviewer/', views.CdrViewer.as_view(), name='cdrviewer'),
    path('selectcdr/<cdruuid>/', views.selectcdr, name='selectcdr'),
    path('cdrstatistics/', views.CdrStatistics.as_view(), name='cdrstatistics'),
    path('cdrstatisticsmos/<int:hours>', views.CdrStatisticsMos.as_view(), name='cdrstatisticsmos'),
    path('cdrstatisticscalls/<int:hours>/', views.CdrStatisticsCalls.as_view(), name='cdrstatisticscalls'),
]
