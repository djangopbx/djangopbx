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
router.register(r'contact', views.ContactViewSet)
router.register(r'contacttel', views.ContactTelViewSet)
router.register(r'contactemail', views.ContactEmailViewSet)
router.register(r'contactgeo', views.ContactGeoViewSet)
router.register(r'contacturl', views.ContactUrlViewSet)
router.register(r'contactorg', views.ContactOrgViewSet)
router.register(r'contactaddress', views.ContactAddressViewSet)
router.register(r'contactdate', views.ContactDateViewSet)
router.register(r'contactcategory', views.ContactCategoryViewSet)
router.register(r'contactgroup', views.ContactGroupViewSet)

urlpatterns = [
    path('contactlist/', views.ContactList.as_view(), name='contactlist'),
    path('contactadd/', views.ContactAdd.as_view(), name='contactadd'),
    path('contactadd/<contact_id>/', views.ContactAdd.as_view(), name='contactadd'),
    path('contactedit/<pk>/', views.ContactEdit.as_view(), name='contactedit'),
    path('contactdel/<pk>/', views.ContactDel.as_view(), name='contactdel'),

    path('contactteladd/<contact_id>/', views.ContactTelAdd.as_view(), name='contactteladd'),
    path('contactteledit/<pk>/', views.ContactTelEdit.as_view(), name='contactteledit'),
    path('contactteldel/<pk>/', views.ContactTelDel.as_view(), name='contactteldel'),

    path('contactaddressadd/<contact_id>/', views.ContactAddressAdd.as_view(), name='contactaddressadd'),
    path('contactaddressedit/<pk>/', views.ContactAddressEdit.as_view(), name='contactaddressedit'),
    path('contactaddressdel/<pk>/', views.ContactAddressDel.as_view(), name='contactaddressdel'),

    path('contactemailadd/<contact_id>/', views.ContactEmailAdd.as_view(), name='contactemailadd'),
    path('contactemailedit/<pk>/', views.ContactEmailEdit.as_view(), name='contactemailedit'),
    path('contactemaildel/<pk>/', views.ContactEmailDel.as_view(), name='contactemaildel'),

    path('contacturladd/<contact_id>/', views.ContactUrlAdd.as_view(), name='contacturladd'),
    path('contacturledit/<pk>/', views.ContactUrlEdit.as_view(), name='contacturledit'),
    path('contacturldel/<pk>/', views.ContactUrlDel.as_view(), name='contacturldel'),

    path('contactorgadd/<contact_id>/', views.ContactOrgAdd.as_view(), name='contactorgadd'),
    path('contactorgedit/<pk>/', views.ContactOrgEdit.as_view(), name='contactorgedit'),
    path('contactorgdel/<pk>/', views.ContactOrgDel.as_view(), name='contactorgdel'),

    path('contactgeoadd/<contact_id>/', views.ContactGeoAdd.as_view(), name='contactgeoadd'),
    path('contactgeoedit/<pk>/', views.ContactGeoEdit.as_view(), name='contactgeoedit'),
    path('contactgeodel/<pk>/', views.ContactGeoDel.as_view(), name='contactgeodel'),

    path('contactdateadd/<contact_id>/', views.ContactDateAdd.as_view(), name='contactdateadd'),
    path('contactdateedit/<pk>/', views.ContactDateEdit.as_view(), name='contactdateedit'),
    path('contactdatedel/<pk>/', views.ContactDateDel.as_view(), name='contactdatedel'),

    path('contactcategoryadd/<contact_id>/', views.ContactCategoryAdd.as_view(), name='contactcategoryadd'),
    path('contactcategoryedit/<pk>/', views.ContactCategoryEdit.as_view(), name='contactcategoryedit'),
    path('contactcategorydel/<pk>/', views.ContactCategoryDel.as_view(), name='contactcategorydel'),

    path('contactgroupadd/<contact_id>/', views.ContactGroupAdd.as_view(), name='contactgroupadd'),
    path('contactgroupedit/<pk>/', views.ContactGroupEdit.as_view(), name='contactgroupedit'),
    path('contactgroupdel/<pk>/', views.ContactGroupDel.as_view(), name='contactgroupdel'),

    path('vcfupload/', views.ImportVcf.as_view(), name='vcfupload'),
    path('vcfexportsingle/<contact_id>/', views.ExportSingleVcf.as_view(), name='vcfexportsingle'),
    path('vcfexportmulti/', views.ExportMultiVcf.as_view(), name='vcfexportmulti'),
]
