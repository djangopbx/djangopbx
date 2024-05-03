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

import json
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaulttags import register
from django.contrib import messages
from .forms import LogViewerForm, IpAddressForm
from pbx.commonfunctions import shcommand
from pbx.amqpcmdevent import AmqpCmdEvent
from django.utils.http import urlsafe_base64_decode
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import permissions
from pbx.restpermissions import (
    AdminApiAccessPermission
)
from .serializers import FwGenericSerializer, FwCountersSerializer


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_item_humanize(dictionary, key):
    return intcomma(dictionary.get(key))


@register.filter
def ip_prefix(ip):
    if type(ip) is dict:
        return ip['prefix']['addr'] + '/' + str(ip['prefix']['len'])
    return ip


def _find_objects(ruleset, type):
    return [o[type] for o in ruleset if type in o]


@staff_member_required
def fwconfigviewer(request):
    form = LogViewerForm()
    form.fields['logtext'].initial = shcommand(['cat', '/etc/nftables.conf'])
    form.fields['logtext'].label = 'Firewall nftables Configuration (/etc/nftables.conf)'

    return render(request, 'firewall/configfileviewer.html', {'refresher': 'fwconfigviewer', 'form': form})


@staff_member_required
def fwlistcounters(request):
    nftjdata = shcommand(['/usr/local/bin/fw-list-counters.sh'])
    data = json.loads(nftjdata)
    return render(
            request, 'firewall/fwlistcounters.html',
            {'refresher': 'fwlistcounters', 'counters': _find_objects(data['nftables'], 'counter')}
            )


@staff_member_required
def fwblocklist(request):
    nftjdata = shcommand(['/usr/local/bin/fw-show-ipv4-block-list.sh'])
    dataipv4 = json.loads(nftjdata)
    nftjdata = shcommand(['/usr/local/bin/fw-show-ipv6-block-list.sh'])
    dataipv6 = json.loads(nftjdata)
    ipv4 = []
    if 'elem' in dataipv4['nftables'][1]['set']:
        ipv4 = dataipv4['nftables'][1]['set']['elem']
    ipv6 = []
    if 'elem' in dataipv6['nftables'][1]['set']:
        ipv6 = dataipv6['nftables'][1]['set']['elem']
    return render(
            request, 'firewall/fwiplist.html',
            {'title': 'Block List', 'refresher': 'fwblocklist', 'ipv4': ipv4, 'ipv6': ipv6}
            )


@staff_member_required
def fwwhitelist(request):
    nftjdata = shcommand(['/usr/local/bin/fw-show-ipv4-white-list.sh'])
    dataipv4 = json.loads(nftjdata)
    nftjdata = shcommand(['/usr/local/bin/fw-show-ipv6-white-list.sh'])
    dataipv6 = json.loads(nftjdata)
    ipv4 = []
    if 'elem' in dataipv4['nftables'][1]['set']:
        ipv4 = dataipv4['nftables'][1]['set']['elem']
    ipv6 = []
    if 'elem' in dataipv6['nftables'][1]['set']:
        ipv6 = dataipv6['nftables'][1]['set']['elem']
    return render(
            request, 'firewall/fwiplist.html',
            {'title': 'White List', 'refresher': 'fwwhitelist', 'ipv4': ipv4, 'ipv6': ipv6}
            )


@staff_member_required
def fwsipcustomerlist(request):
    nftjdata = shcommand(['/usr/local/bin/fw-show-ipv4-sip-customer-list.sh'])
    dataipv4 = json.loads(nftjdata)
    nftjdata = shcommand(['/usr/local/bin/fw-show-ipv6-sip-customer-list.sh'])
    dataipv6 = json.loads(nftjdata)
    ipv4 = []
    if 'elem' in dataipv4['nftables'][1]['set']:
        ipv4 = dataipv4['nftables'][1]['set']['elem']
    ipv6 = []
    if 'elem' in dataipv6['nftables'][1]['set']:
        ipv6 = dataipv6['nftables'][1]['set']['elem']
    return render(
            request, 'firewall/fwiplist.html',
            {'title': 'SIP Customer List', 'refresher': 'fwsipcustomerlist', 'ipv4': ipv4, 'ipv6': ipv6}
            )


@staff_member_required
def fwsipgatewaylist(request):
    nftjdata = shcommand(['/usr/local/bin/fw-show-ipv4-sip-gateway-list.sh'])
    dataipv4 = json.loads(nftjdata)
    nftjdata = shcommand(['/usr/local/bin/fw-show-ipv6-sip-gateway-list.sh'])
    dataipv6 = json.loads(nftjdata)
    ipv4 = []
    if 'elem' in dataipv4['nftables'][1]['set']:
        ipv4 = dataipv4['nftables'][1]['set']['elem']
    ipv6 = []
    if 'elem' in dataipv6['nftables'][1]['set']:
        ipv6 = dataipv6['nftables'][1]['set']['elem']
    return render(
            request, 'firewall/fwiplist.html',
            {'title': 'SIP Gateway List', 'refresher': 'fwsipgatewaylist', 'ipv4': ipv4, 'ipv6': ipv6}
            )


@staff_member_required
def fwwebblocklist(request):
    nftjdata = shcommand(['/usr/local/bin/fw-show-ipv4-web-block-list.sh'])
    dataipv4 = json.loads(nftjdata)
    nftjdata = shcommand(['/usr/local/bin/fw-show-ipv6-web-block-list.sh'])
    dataipv6 = json.loads(nftjdata)
    ipv4 = []
    if 'elem' in dataipv4['nftables'][1]['set']:
        ipv4 = dataipv4['nftables'][1]['set']['elem']
    ipv6 = []
    if 'elem' in dataipv6['nftables'][1]['set']:
        ipv6 = dataipv6['nftables'][1]['set']['elem']
    return render(
            request, 'firewall/fwiplist.html',
            {'title': 'Web Block List', 'refresher': 'fwwebblocklist', 'ipv4': ipv4, 'ipv6': ipv6}
            )


@staff_member_required
def fwaddip(request):
    firewall_event_template = '{\"Event-Name\":\"FIREWALL\", \"Action\":\"add\", \"IP-Type\":\"%s\",\"Fw-List\":\"%s\", \"IP-Address\":\"%s\"}' # noqa: E501
    if request.method == 'POST':

        form = IpAddressForm(request.POST)
        setname = request.POST['setname']
        fwlist = 'None'
        if setname == 'BL':
            BLform = form
            fwlist = 'block'
        if setname == 'WL':
            WLform = form
            fwlist = 'white'
        if setname == 'SCL':
            SCLform = form
            fwlist = 'sip-customer'
        if setname == 'SGL':
            SGLform = form
            fwlist = 'sip-gateway'
        if setname == 'WBL':
            SGLform = form
            fwlist = 'web-block'

        if form.is_valid():
            broker = AmqpCmdEvent()
            broker.connect()
            if len(form.cleaned_data['ipv4']) > 0:
                ipaddr = form.cleaned_data['ipv4']
                if form.cleaned_data['ipv4len'] < 32:
                    ipaddr += '/' + str(form.cleaned_data['ipv4len'])
                nftdata = shcommand(['/usr/local/bin/fw-add-ipv4-%s-list.sh' % fwlist, ipaddr])
                if len(nftdata) > 0:
                    messages.add_message(request, messages.INFO, _('Error: %s' % nftdata))
                else:
                    messages.add_message(request, messages.INFO, _('IP Added'))
                routing = 'DjangoPBX.%s.FIREWALL.add.ipv4' % broker.hostname
                payload = firewall_event_template % ('ipv4', fwlist, ipaddr)

            if len(form.cleaned_data['ipv6']) > 0:
                ipaddr = form.cleaned_data['ipv6']
                if form.cleaned_data['ipv6len'] < 128:
                    ipaddr += '/' + str(form.cleaned_data['ipv6len'])
                nftdata = shcommand(['/usr/local/bin/fw-add-ipv6-%s-list.sh' % fwlist, ipaddr])
                if len(nftdata) > 0:
                    messages.add_message(request, messages.INFO, _('Error: %s' % nftdata))
                else:
                    messages.add_message(request, messages.INFO, _('IP Added'))
                routing = 'DjangoPBX.%s.FIREWALL.add.ipv6' % broker.hostname
                payload = firewall_event_template % ('ipv6', fwlist, ipaddr)
            try:
                broker.adhoc_publish(payload, routing, 'TAP.Firewall')
            except:
                pass
            broker.disconnect()
        else:
            messages.add_message(request, messages.INFO, _('IP Address is invalid'))

    form = IpAddressForm()
    return render(
            request, 'firewall/fw_add_del_ip.html',
            {'form': form, 'formurl': 'fwaddip',
                'title': _('Add IP Address to Firewall'), 'buttontxt': _('Add IP(s)')})


@staff_member_required
def fwdelip(request):
    firewall_event_template = '{\"Event-Name\":\"FIREWALL\", \"Action\":\"delete\", \"IP-Type\":\"%s\",\"Fw-List\":\"%s\", \"IP-Address\":\"%s\"}' # noqa: E501
    if request.method == 'POST':

        form = IpAddressForm(request.POST)
        setname = request.POST['setname']
        fwlist = 'None'
        if setname == 'BL':
            BLform = form
            fwlist = 'block'
        if setname == 'WL':
            WLform = form
            fwlist = 'white'
        if setname == 'SCL':
            SCLform = form
            fwlist = 'sip-customer'
        if setname == 'SGL':
            SGLform = form
            fwlist = 'sip-gateway'
        if setname == 'WBL':
            SGLform = form
            fwlist = 'web-block'

        if form.is_valid():
            broker = AmqpCmdEvent()
            broker.connect()
            if len(form.cleaned_data['ipv4']) > 0:
                ipaddr = form.cleaned_data['ipv4']
                if form.cleaned_data['ipv4len'] < 32:
                    ipaddr += '/' + str(form.cleaned_data['ipv4len'])
                nftdata = shcommand(['/usr/local/bin/fw-delete-ipv4-%s-list.sh' % fwlist, ipaddr])
                if len(nftdata) > 0:
                    messages.add_message(request, messages.INFO, _('Error: %s' % nftdata))
                else:
                    messages.add_message(request, messages.INFO, _('IP Deleted'))
                routing = 'DjangoPBX.%s.FIREWALL.delete.ipv4' % broker.hostname
                payload = firewall_event_template % ('ipv4', fwlist, ipaddr)

            if len(form.cleaned_data['ipv6']) > 0:
                ipaddr = form.cleaned_data['ipv6']
                if form.cleaned_data['ipv6len'] < 128:
                    ipaddr += '/' + str(form.cleaned_data['ipv6len'])
                nftdata = shcommand(['/usr/local/bin/fw-delete-ipv6-%s-list.sh' % fwlist, ipaddr])
                if len(nftdata) > 0:
                    messages.add_message(request, messages.INFO, _('Error: %s' % nftdata))
                else:
                    messages.add_message(request, messages.INFO, _('IP Deleted'))
                routing = 'DjangoPBX.%s.FIREWALL.delete.ipv6' % broker.hostname
                payload = firewall_event_template % ('ipv6', fwlist, ipaddr)
            try:
                broker.adhoc_publish(payload, routing, 'TAP.Firewall')
            except:
                pass
            broker.disconnect()
        else:
            messages.add_message(request, messages.INFO, _('IP Address is invalid'))

    form = IpAddressForm()
    return render(
            request, 'firewall/fw_add_del_ip.html',
            {'form': form, 'formurl': 'fwdelip',
                'title': _('Delete IP Address from Firewall'), 'buttontxt': _('Delete IP(s)')})


class FwCountersView(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Firewall counters to be viewed.
    """
    serializer_class = FwCountersSerializer
    shell_command = '/usr/local/bin/fw-list-counters.sh'

    def get_queryset(self):
        pass

    def list(self, request):
        nftjdata = shcommand([self.shell_command])
        data = json.loads(nftjdata)
        data = _find_objects(data['nftables'], 'counter')
        c_count = 0
        c_data = []
        for counter in data:
            cd = {'counter': counter['name'], 'packets': counter['packets'], 'bytes': counter['bytes']}
            c_data.append(cd)
            c_count += 1
        results = self.serializer_class(c_data, many=True, context={'request': request}).data
        return Response({'count': c_count, 'results': results})

    def retrieve(self, request, pk=None):
        if not pk:
            return Response({'status': 'err', 'message': 'pk not found'})
        counter, packets, bytes = urlsafe_base64_decode(pk).decode().split('&')
        return Response({'counter': counter, 'packets': packets, 'bytes': bytes})


class FirewallViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Firewall lists to be viewed and updated.
    """
    serializer_class = FwGenericSerializer
    shell_command = '/usr/local/bin/fw-%s-%s-%s-list.sh'
    firewall_event_template = '{\"Event-Name\":\"FIREWALL\", \"Action\":\"%s\", \"IP-Type\":\"%s\",\"Fw-List\":\"%s\", \"IP-Address\":\"%s\"}' # noqa: E501
    fw_list_lookup = {
        'ipv4_white_list': 'white',
        'ipv6_white_list': 'white',
        'ipv4_sip_gateway_list': 'sip-gateway',
        'ipv6_sip_gateway_list': 'sip-gateway',
        'ipv4_sip_customer_list': 'sip-customer',
        'ipv6_sip_customer_list': 'sip-customer',
        'ipv4_web_block_list': 'web-block',
        'ipv6_web_block_list': 'web-block',
        'ipv4_block_list': 'block',
        'ipv6_block_list': 'block'
    }
    ip_type_lookup = {
        'ipv4_addr': 'ipv4',
        'ipv6_addr': 'ipv6'
    }

    permission_classes = [
        permissions.IsAuthenticated,
        AdminApiAccessPermission,
    ]

    def get_queryset(self):
        pass

    def build_list_shell_command(self):
        raise NotImplementedError

    def build_generic_shell_command(self, action='add', ip_type='ipv4_addr', fw_list='ipv4_sip_customer_list'):
        return self.shell_command % (action, self.ip_type_lookup[ip_type], self.fw_list_lookup[fw_list])

    def send_fw_event(self, action, ip_type, fw_list, ip_address):
        broker = AmqpCmdEvent()
        broker.connect()
        routing = 'DjangoPBX.%s.FIREWALL.%s.%s' % (broker.hostname, action, ip_type)
        payload = self.firewall_event_template % (action, ip_type, fw_list, ip_address)
        try:
            broker.adhoc_publish(payload, routing, 'TAP.Firewall')
        except:
            pass
        broker.disconnect()

    def list(self, request):
        nftjdata = shcommand([self.build_list_shell_command()])
        data = json.loads(nftjdata)
        ip_count = 0
        ip_data = []
        ip_type = ''
        fw_list = ''
        if 'type' in data['nftables'][1]['set']:
            ip_type = data['nftables'][1]['set']['type']
        if 'name' in data['nftables'][1]['set']:
            fw_list = data['nftables'][1]['set']['name']
        if 'elem' in data['nftables'][1]['set']:
            for ip in  data['nftables'][1]['set']['elem']:
                ipd = {'ip_type': ip_type, 'fw_list': fw_list, 'ip_address': ip}
                ip_data.append(ipd)
                ip_count += 1
        results = self.serializer_class(ip_data, many=True, context={'request': request}).data
        return Response({'count': ip_count, 'results': results})

    def retrieve(self, request, pk=None):
        if not pk:
            return Response({'status': 'err', 'message': 'pk not found'})
        ip_type, fw_list, ip = urlsafe_base64_decode(pk).decode().split('&')
        return Response({'fw_list': fw_list, 'ip_type': ip_type, 'ip_address': ip})

    def create(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            fwdata = serializer.save()
            if 'suffix' in fwdata:
                ip_address = '%s/%s' % (fwdata['ip_address'], fwdata['suffix'])
            else:
                ip_address = fwdata['ip_address']
            nftdata = shcommand([self.build_generic_shell_command('add', fwdata['ip_type'], fwdata['fw_list']), ip_address])
            self.send_fw_event('add', fwdata['ip_type'], fwdata['fw_list'], ip_address)
            if len(nftdata) > 0:
                return Response({'Error': _(nftdata)}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'added': 'OK', 'ip_address': fwdata['ip_address']}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        if not pk:
            return Response({'status': 'err', 'message': 'pk not found'})
        ip_type, fw_list, ip_address = urlsafe_base64_decode(pk).decode().split('&')
        nftdata = shcommand([self.build_generic_shell_command('delete', ip_type, fw_list), ip_address])
        self.send_fw_event('delete', ip_type, fw_list, ip_address)
        if len(nftdata) > 0:
            return Response({'Error': _(nftdata)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FwWhiteIpv4View(FirewallViewSet):
    """
    API endpoint that allows Firewall White IPv4 lists to be viewed and updated.
    """
    def build_list_shell_command(self):
        return self.shell_command % ('show', 'ipv4', 'white')


class FwWhiteIpv6View(FirewallViewSet):
    """
    API endpoint that allows Firewall White IPv6 lists to be viewed and updated.
    """
    def build_list_shell_command(self):
        return self.shell_command % ('show', 'ipv6', 'white')


class FwSipGatewayIpv4View(FirewallViewSet):
    """
    API endpoint that allows Firewall SIP Gateway IPv4 lists to be viewed and updated.
    """
    def build_list_shell_command(self):
        return self.shell_command % ('show', 'ipv4', 'sip-gateway')


class FwSipGatewayIpv6View(FirewallViewSet):
    """
    API endpoint that allows Firewall SIP Gateway IPv6 lists to be viewed and updated.
    """
    def build_list_shell_command(self):
        return self.shell_command % ('show', 'ipv6', 'sip-gateway')


class FwSipCustomerIpv4View(FirewallViewSet):
    """
    API endpoint that allows Firewall SIP Customer IPv4 lists to be viewed and updated.
    """
    def build_list_shell_command(self):
        return self.shell_command % ('show', 'ipv4', 'sip-customer')


class FwSipCustomerIpv6View(FirewallViewSet):
    """
    API endpoint that allows Firewall SIP Customer IPv6 lists to be viewed and updated.
    """
    def build_list_shell_command(self):
        return self.shell_command % ('show', 'ipv6', 'sip-customer')


class FwWebBlockIpv4View(FirewallViewSet):
    """
    API endpoint that allows Firewall Web Block IPv4 lists to be viewed and updated.
    """
    def build_list_shell_command(self):
        return self.shell_command % ('show', 'ipv4', 'web-block')


class FwWebBlockIpv6View(FirewallViewSet):
    """
    API endpoint that allows Firewall Web Block IPv6 lists to be viewed and updated.
    """
    def build_list_shell_command(self):
        return self.shell_command % ('show', 'ipv6', 'web-block')


class FwBlockIpv4View(FirewallViewSet):
    """
    API endpoint that allows Firewall Block IPv4 lists to be viewed and updated.
    """
    def build_list_shell_command(self):
        return self.shell_command % ('show', 'ipv4', 'block')


class FwBlockIpv6View(FirewallViewSet):
    """
    API endpoint that allows Firewall Block IPv6 lists to be viewed and updated.
    """
    def build_list_shell_command(self):
        return self.shell_command % ('show', 'ipv6', 'block')
