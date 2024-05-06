#
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

from django.utils.translation import gettext_lazy as _
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers


class CfgStatsSerializer(serializers.Serializer):

    id      = serializers.CharField(source='item')         # noqa: E501, E221
    item    = serializers.CharField(label=_('Item'))       # noqa: E501, E221
    enabled = serializers.IntegerField(label=_('Enabled')) # noqa: E501, E221
    total   = serializers.IntegerField(label=_('Total'))   # noqa: E501, E221


class SwitchStatusSerializer(serializers.Serializer):

    id      = serializers.CharField(source='line')         # noqa: E501, E221
    switch  = serializers.CharField(label=_('Switch'))     # noqa: E501, E221
    measure = serializers.CharField(label=_('Measure'))    # noqa: E501, E221


class SwitchLiveTrafficSerializer(serializers.Serializer):

    id      = serializers.CharField(source='line')         # noqa: E501, E221
    switch  = serializers.CharField(label=_('Switch'))     # noqa: E501, E221
    item    = serializers.CharField(label=_('Item'))       # noqa: E501, E221
    value   = serializers.IntegerField(label=_('Value'))   # noqa: E501, E221


class GenericItemValueSerializer(serializers.Serializer):

    id      = serializers.CharField(source='item')         # noqa: E501, E221
    item    = serializers.CharField(label=_('Item'))       # noqa: E501, E221
    value   = serializers.CharField(label=_('Value'))      # noqa: E501, E221


class DiskInfoSerializer(serializers.Serializer):

    id      = serializers.CharField(source='device')            # noqa: E501, E221
    device  = serializers.CharField(label=_('Device'))          # noqa: E501, E221
    total   = serializers.CharField(label=_('Total'))           # noqa: E501, E221
    used    = serializers.CharField(label=_('Used'))            # noqa: E501, E221
    free    = serializers.CharField(label=_('Free'))            # noqa: E501, E221
    pc_used = serializers.CharField(label=_('Percent Used'))    # noqa: E501, E221
    fs_type = serializers.CharField(label=_('Filesystem Type')) # noqa: E501, E221
    mount   = serializers.CharField(label=_('Mount Point'))     # noqa: E501, E221


class NetworkTrafficByInterfaceSerializer(serializers.Serializer):

    id             = serializers.CharField(source='interface')           # noqa: E501, E221
    interface      = serializers.CharField(label=_('Interface'))         # noqa: E501, E221
    bytessent      = serializers.CharField(label=_('Bytes Sent'))        # noqa: E501, E221
    bytesrecv      = serializers.CharField(label=_('Bytes Recv'))        # noqa: E501, E221
    bytesendrate   = serializers.CharField(label=_('Bytes Send Rate'))   # noqa: E501, E221
    byterecvrate   = serializers.CharField(label=_('Bytes Recv Rate'))   # noqa: E501, E221
    packetssent    = serializers.CharField(label=_('Packets Sent'))      # noqa: E501, E221
    packetsrecv    = serializers.CharField(label=_('Packets Recv'))      # noqa: E501, E221
    packetsendrate = serializers.CharField(label=_('Packets Sent Rate')) # noqa: E501, E221
    packetrecvrate = serializers.CharField(label=_('Packets Recv Rate')) # noqa: E501, E221
