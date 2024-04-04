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
from .forms import ClearCacheForm, ReloadXmlForm, TestEmailForm
from dialplans.models import Dialplan
from pbx.fscmdabslayer import FsCmdAbsLayer
from pbx.pbxsendsmtp import PbxTemplateMessage

phrases_available = True
try:
    from phrases.models import Phrases
except ImportError:
    phrases_available = False

ivrmenus_available = True
try:
    from ivrmenus.models import IvrMenus
except ImportError:
    ivrmenus_available = False



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
                    cache.delete('dialplan:%s:%s' % (dp.context, dp.number))

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
                cache.delete('configuration:acl.conf')
                cache.delete('configuration:sofia.conf')
                cache.delete('configuration:local_stream.conf')
                cache.delete('configuration:translate.conf')
                cache.delete('configuration:callcentre.conf')

                if ivrmenus_available:
                    ivrs = IvrMenus.objects.filter(enabled='true', domain_id=domain_uuid)
                    for ivr in ivrs:
                        cache.delete('configuration:ivr.conf:%s' % str(ivr.id))

            if clearall:
                cache.clear()

            messages.add_message(request, messages.INFO, _('Cache Cleared'))

        return render(request, self.template_name, {'form': form, 'refresher': 'clearcache'})


@method_decorator(staff_member_required, name="dispatch")
class ReloadXmlView(View):
    form_class = ReloadXmlForm
    template_name = "utilities/reloadxml.html"

    def get(self, request, *args, **kwargs):
        es = FsCmdAbsLayer()
        form = self.form_class()
        form.fields['host'].choices = [(h, h) for h in es.freeswitches]
        return render(request, self.template_name, {'form': form, 'refresher': 'reloadxml'})

    def post(self, request, *args, **kwargs):
        es = FsCmdAbsLayer()
        form = self.form_class(request.POST)
        form.fields['host'].choices = [(h, h) for h in es.freeswitches]
        if form.is_valid():
            host = form.cleaned_data['host'] # noqa: E221
            xml  = form.cleaned_data['xml']  # noqa: E221
            acl  = form.cleaned_data['acl']  # noqa: E221

            if xml or acl:
                if not es.connect():
                    return render(request, 'error.html', {'back': '/portal/', 'info': {'Message': _('Unable to connect to the FreeSWITCH Event Socket')}, 'title': 'Broker/Socket Error'})
            if xml:
                 es.send('api reloadxml', host)
            if acl:
                 es.send('api reloadacl', host)
            es.process_events()
            es.get_responses()
            es.disconnect()

            messages.add_message(request, messages.INFO, _('XML/ACL Reloaded'))

        return render(request, self.template_name, {'form': form, 'refresher': 'reloadxml'})


@method_decorator(staff_member_required, name="dispatch")
class TestEmailView(View):
    form_class = TestEmailForm
    template_name = "utilities/testemail.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'refresher': 'testemail'})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        out = None
        if form.is_valid():
            to      = form.cleaned_data['email_to']      # noqa: E221
            subject = form.cleaned_data['email_subject'] # noqa: E221
            body    = form.cleaned_data['email_body']    # noqa: E221

            m = PbxTemplateMessage()
            out = m.Send(to, subject, body, 'Text')
        return render(request, self.template_name, {'form': form, 'refresher': 'testemail', 'result': out})

