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

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from utilities.clearcache import ClearCache

from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .models import (
    Phrases, PhraseDetails
)
from .serializers import (
    PhrasesSerializer, PhraseDetailsSerializer
)


class PhrasesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Phrases to be viewed or edited.
    """
    queryset = Phrases.objects.all().order_by('domain_id', 'name')
    serializer_class = PhrasesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['domain_id', 'name']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    @action(detail=True)
    def flush_cache_phrase(self, request, pk=None):
        obj = self.get_object()
        ClearCache().phrases(obj.domain_id.name)
        return Response({'status': 'language phrase cache flushed'})


class PhraseDetailsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows PhraseDetails to be viewed or edited.
    """
    queryset = PhraseDetails.objects.all().order_by('phrase_id', 'sequence')
    serializer_class = PhraseDetailsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['phrase_id']
    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.username)

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user.username)
