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

import os
from datetime import datetime
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from pbx.fscmdabslayer import FsCmdAbsLayer
from accounts.accountfunctions import AccountFunctions

from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    Voicemail, VoicemailGreeting,
)
from .serializers import (
    VoicemailSerializer, VoicemailGreetingSerializer,
)


class VoicemailViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Voicemails to be viewed or edited.
    """
    queryset = Voicemail.objects.all().order_by('extension_id')
    serializer_class = VoicemailSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['extension_id']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class VoicemailGreetingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows VoicemailGreetingss to be viewed or edited.
    """
    queryset = VoicemailGreeting.objects.all().order_by('voicemail_id', 'name')
    serializer_class = VoicemailGreetingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['voicemail_id', 'name']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


@login_required
def listvoicemails(request, vmuuid=None, vmext=None, action=None):
    extension_list = request.session['extension_list'].split(',')
    if request.user.is_superuser:
        extension_list = AccountFunctions().list_superuser_extensions(request.session['domain_uuid'])
    th = [_('Extension'), _('Date Time'), _('From'), _('Duration'), _('Message'), _('Action')]
    info = {}
    es = FsCmdAbsLayer()
    if not es.connect():
        return render(request, 'error.html', {'back': '/portal/',
            'info': {'Message': _('Unable to connect to the FreeSWITCH')}, 'title': 'Broker/Socket Error'})
    if action == 'delete':
        es.clear_responses()
        es.send('api vm_delete %s@%s %s' % (vmext, request.session['domain_name'], vmuuid))
        es.process_events(0.25)
        es.get_responses()

    for e in extension_list:
        es.clear_responses()
        es.send('api vm_list %s@%s' % (e, request.session['domain_name']))
        es.process_events(2)
        es.get_responses()
        valid_resp_list = [x for x in es.responses if not '-ERR no reply' in x]
        vmstr = '\n'.join(valid_resp_list)
        if not len(vmstr) < 1:
            # '1670780459:0:201:test1.djangopbx.com:inbox:/var/lib/freeswitch/storage/voicemail/default/test1.djangopbx.com/201/msg_2740d2b1-de55-4425-b71e-4215647642ea.wav:68d2c984-78da-4d13-a48e-2e800fc7506f:Test1:202:7'  # noqa: E501
            vmlist = vmstr.split('\n')
            for vm in vmlist:
                if ':' not in vm:
                    continue
                v = vm.split(':')
                filename = os.path.basename(v[5])
                file_ext = os.path.splitext(filename)[1]
                atype = 'audio/wav'
                if file_ext == 'mp3':
                    atype = 'audio/mpeg'
                try:
                    i = int(v[0])
                except ValueError:
                    i = 0
                date_time = datetime.fromtimestamp(i)
                info['<!-- %s --> %s' % (v[6], v[2])] = [
                        date_time.strftime("%d-%m-%Y, %H:%M:%S"),
                        v[8],
                        v[9],
                        '<audio controls><source src="/fs/voicemail/default/%s/%s/%s" type="%s"> %s</audio>' % (
                            request.session['domain_name'],
                            e, filename, atype,
                            _('Your browser does not support the audio tag.')
                            ),
                        '<a href=\"/voicemail/listvoicemails/%s/%s/delete/\">%s</a>' % (v[6], v[2], _('Delete'))
                        ]

    es.disconnect()
    return render(
            request, 'infotablemulti.html',
            {'refresher': '/voicemail/listvoicemails/', 'th': th, 'info': info, 'title': 'Voicemails'}
            )
