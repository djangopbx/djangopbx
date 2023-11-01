#
#    DjangoPBX
#
#    MIT License
#
#    Copyright (c) 2016 - 2023 Adrian Fretwell <adrian@djangopbx.com>
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

from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from django.shortcuts import render
from django.views import View
from .forms import ClearCacheForm, ReloadXmlForm
from dialplans.models import Dialplan
from django.conf import settings
from pbx.fseventsocket import EventSocket

phrases_available = True
try:
    from phrases.models import Phrases
except ImportError:
    phrases_available = False


@method_decorator(staff_member_required, name="dispatch")
class ClearCacheView(View):
    form_class = ClearCacheForm
    template_name = "utilities/clearcache.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'refresher': 'clearcache'})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            directory     = form.cleaned_data['directory']     # noqa: E221
            dialplan      = form.cleaned_data['dialplan']      # noqa: E221
            languages     = form.cleaned_data['languages']     # noqa: E221
            configuration = form.cleaned_data['configuration'] # noqa: E221
            clearall      = form.cleaned_data['clearall']      # noqa: E221

            domain_name = request.session['domain_name']
            domain_uuid = request.session['domain_uuid']

            if directory:
                cache.delete('directory:groups:%s' % domain_name)

            if dialplan:
                cache.delete('xmlhandler:context_type')
                cache.delete('dialplan:%s' % domain_name)
                dps = Dialplan.objects.filter(enabled='true', domain_id=domain_uuid, category='Inbound route')
                for dp in dps:
                    cache.delete('dialplan:%s:%s' % (domain_name, dp.number))

            if languages:
                del_list = [
                    'xmlhandler:lang:default_language',
                    'xmlhandler:lang:default_dialect',
                    'xmlhandler:lang:default_voice',
                    'xmlhandler:lang:sounds_dir'
                ]
                cache.delete_many(del_list)
                if phrases_available:
                    ps = Phrases.objects.filter(enabled='true', domain_id=domain_uuid)
                    for p in ps:
                        cache.delete('languages:%s:%s' % (p.language, str(p.id)))

            if configuration:
                cache.delete('xmlhandler:allowed_addresses')

            if clearall:
                cache.clear()

            messages.add_message(request, messages.INFO, _('Cache Cleared'))

        return render(request, self.template_name, {'form': form, 'refresher': 'clearcache'})


@method_decorator(staff_member_required, name="dispatch")
class ReloadXmlView(View):
    form_class = ReloadXmlForm
    template_name = "utilities/reloadxml.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'refresher': 'reloadxml'})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            xml = form.cleaned_data['xml'] # noqa: E221
            acl = form.cleaned_data['acl'] # noqa: E221

            if xml or acl:
                es = EventSocket()
                if not es.connect(*settings.EVSKT):
                    return render(request, 'error.html', {'back': '/portal/', 'info': {'Message': _('Unable to connect to the FreeSWITCH Event Socket')}, 'title': 'Event Socket Error'})

            if xml:
                 es.send('api reloadxml')

            if acl:
                 es.send('api reloadacl')

            messages.add_message(request, messages.INFO, _('XML/ACL Reloaded'))

        return render(request, self.template_name, {'form': form, 'refresher': 'reloadxml'})
