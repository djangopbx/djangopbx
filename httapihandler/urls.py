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

from django.urls import path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'httapisession', views.HttApiSessionViewSet)

urlpatterns = [
    path('index/', views.httapiindex, name='index'),
    path('test/', views.test, name='test'),
    path('followme/', views.followme, name='followme'),
    path('followmetoggle/', views.followmetoggle, name='followmetoggle'),
    path('failurehandler/', views.failurehandler, name='failurehandler'),
    path('hangup/', views.hangup, name='hangup'),
    path('register/', views.register, name='register'),
    path('ringgroup/', views.ringgroup, name='ringgroup'),
    path('recordings/', views.recordings, name='recordings'),
    path('callflowtoggle/', views.callflowtoggle, name='callflowtoggle'),
    path('callblock/', views.callblock, name='callblock'),
    path('conference/', views.conference, name='conference'),
    path('agentstatus/', views.agentstatus, name='agentstatus'),
    path('speeddial/', views.speeddial, name='speeddial'),
    path('ccevent/', views.ccevent, name='ccevent'),
    path('donotdisturb/<hraction>/', views.donotdisturb, name='donotdisturb'),
    path('callforward/<hraction>/', views.callforward, name='callforward'),
    path('callforward/<hraction>/<hrparam1>/', views.callforward, name='callforwardarg1'),
    path('disa/', views.disa, name='disa'),
    path('voicemail/<hraction>/', views.voicemail, name='voicemail'),
    path('voicemail/<hraction>/<vmuser>/<vmdomain>/', views.voicemail, name='voicemailvmuservmdomain'),
]
