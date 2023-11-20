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

"""pbx URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _

from rest_framework import routers

# Routers provide an easy way of automatically determining the URL conf.
from tenants.urls import router as tenantsrouter
from portal.urls import router as portalrouter
from switch.urls import router as switchrouter
from dialplans.urls import router as dialplansrouter
from recordings.urls import router as recordingsrouter
from musiconhold.urls import router as musiconholdrouter
from accounts.urls import router as accountsrouter
from voicemail.urls import router as voicemailrouter
from xmlcdr.urls import router as xmlcdrrouter
from conferencesettings.urls import router as conferencesettingsrouter
from provision.urls import router as provisionrouter
from httapihandler.urls import router as httapihandlerrouter
from contacts.urls import router as contactsrouter
from phrases.urls import router as phrasesrouter
from ringgroups.urls import router as ringgroupsrouter
from numbertranslations.urls import router as numbertranslationsrouter
from ivrmenus.urls import router as ivrmenusrouter
from callflows.urls import router as callflowsrouter
from callblock.urls import router as callblockrouter
from callcentres.urls import router as callcentresrouter


# This overrides names in site headers and titles
# , not required if custom admin templates are being used
# but no harm in setting them.
admin.site.site_header = _('DjangoPBX Administration')
admin.site.site_title = _('DjangoPBX Admin Portal')
admin.site.index_title = _('Welcome to the DjangoPBX Admin Portal')

router = routers.DefaultRouter()
router.registry.extend(tenantsrouter.registry)
router.registry.extend(portalrouter.registry)
router.registry.extend(switchrouter.registry)
router.registry.extend(dialplansrouter.registry)
router.registry.extend(recordingsrouter.registry)
router.registry.extend(musiconholdrouter.registry)
router.registry.extend(accountsrouter.registry)
router.registry.extend(voicemailrouter.registry)
router.registry.extend(xmlcdrrouter.registry)
router.registry.extend(conferencesettingsrouter.registry)
router.registry.extend(provisionrouter.registry)
router.registry.extend(httapihandlerrouter.registry)
router.registry.extend(contactsrouter.registry)
router.registry.extend(phrasesrouter.registry)
router.registry.extend(ringgroupsrouter.registry)
router.registry.extend(numbertranslationsrouter.registry)
router.registry.extend(ivrmenusrouter.registry)
router.registry.extend(callflowsrouter.registry)
router.registry.extend(callblockrouter.registry)
router.registry.extend(callcentresrouter.registry)


urlpatterns = [
    path('', include('portal.urls')),
    path('xmlhandler/', include('xmlhandler.urls')),
    path('httapihandler/', include('httapihandler.urls')),
    path('xmlcdr/', include('xmlcdr.urls')),
    path('portal/', include('portal.urls')),
    path('portal/auth/', include('django.contrib.auth.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('firewall/', include('firewall.urls')),
    path('status/', include('status.urls')),
    path('dialplans/', include('dialplans.urls')),
    path('voicemail/', include('voicemail.urls')),
    path('provision/', include('provision.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('utilities/', include('utilities.urls')),

    # Wire up our API using automatic URL routing.
    # Additionally, we include login URLs for the browsable API.
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
