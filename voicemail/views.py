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
from time import sleep
from datetime import datetime
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from pbx.fscmdabslayer import FsCmdAbsLayer
from pbx.commonfunctions import audio_type
from accounts.accountfunctions import AccountFunctions

from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    Voicemail, VoicemailGreeting, VoicemailMessages, VoicemailOptions,
    VoicemailDestinations
)
from .serializers import (
    VoicemailSerializer, VoicemailGreetingSerializer, VoicemailMessagesSerializer,
    VoicemailOptionsSerializer, VoicemailDestinationsSerializer
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
    API endpoint that allows VoicemailGreetings to be viewed or edited.
    """
    queryset = VoicemailGreeting.objects.all().order_by('voicemail_id', 'name')
    serializer_class = VoicemailGreetingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['voicemail_id', 'name', 'filestore']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class VoicemailMessagesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows VoicemailMessages to be viewed or edited.
    """
    queryset = VoicemailMessages.objects.all().order_by('voicemail_id', 'created')
    serializer_class = VoicemailMessagesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['voicemail_id', 'name', 'filestore']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class VoicemailOptionsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows VoicemailOptions to be viewed or edited.
    """
    queryset = VoicemailOptions.objects.all().order_by('voicemail_id', 'option_digits')
    serializer_class = VoicemailOptionsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['voicemail_id', 'description', 'option_digits']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


class VoicemailDestinationsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows VoicemailDestinations to be viewed or edited.
    """
    queryset = VoicemailDestinations.objects.all().order_by('voicemail_id', 'voicemail_dest')
    serializer_class = VoicemailDestinationsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['voicemail_id', 'voicemail_dest']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)


def append_vm_info(info, domain_name, vm_uuid, vm_user, vm_caller, vm_duration, extension, filename, audio_type, date_time):
    info['<!-- %s --> %s' % (vm_uuid, vm_user)] = [
            date_time.strftime("%d-%m-%Y, %H:%M:%S"),
            vm_caller,
            vm_duration,
            '<audio controls preload=\'none\'><source src="/fs/voicemail/default/%s/%s/%s" type="%s"> %s</audio>' % (
                domain_name,
                extension, filename, audio_type,
                _('Your browser does not support the audio tag.')
                ),
            '<a href=\"/voicemail/listvoicemails/%s/%s/delete/\">%s</a>' % (vm_uuid, vm_user, _('Delete'))
            ]

@login_required
def listvoicemails(request, vmuuid=None, vmext=None, action=None):
    extension_list = request.session['extension_list'].split(',')
    if request.user.is_superuser:
        extension_list = AccountFunctions().list_superuser_extensions(request.session['domain_uuid'])
    th = [_('Extension'), _('Date Time'), _('From'), _('Duration'), _('Message'), _('Action')]
    info = {}
    if settings.PBX_USE_MOD_VOICEMAIL:
        es = FsCmdAbsLayer()
        if not es.connect():
            return render(request, 'error.html', {'back': '/portal/',
                'info': {'Message': _('Unable to connect to the FreeSWITCH')}, 'title': 'Broker/Socket Error'})
        if action == 'delete':
            es.clear_responses()
            es.send('api vm_delete %s@%s %s' % (vmext, request.session['domain_name'], vmuuid))
            es.process_events(0.25)
            es.get_responses()
            sleep(1)
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
                    atype = audio_type(file_ext)
                    try:
                        i = int(v[0])
                    except ValueError:
                        i = 0
                    date_time = datetime.fromtimestamp(i)
                    append_vm_info(info, request.session['domain_name'], v[6], v[2], v[8], v[9], e, filename, atype, date_time)
        es.disconnect()
    else:
        if action == 'delete':
            VoicemailMessages.objects.filter(pk=vmuuid).delete()
        vms = Voicemail.objects.filter(enabled='true', extension_id__extension__in=extension_list)
        for vm in vms:
            msgs = vm.voicemailmessages_set.all()
            for msg in msgs:
                try:
                    file_ext = os.path.splitext(msg.name)[1]
                except:
                    file_ext = 'wav'
                atype = audio_type(file_ext)
                append_vm_info(info, request.session['domain_name'], str(msg.id),
                            vm.extension_id.extension, msg.caller_id_number, msg.duration,
                            vm.extension_id.extension, msg.name, atype, msg.created)
    return render(
            request, 'infotablemulti.html',
            {'refresher': '/voicemail/listvoicemails/', 'th': th, 'info': info, 'title': 'Voicemails'}
            )
