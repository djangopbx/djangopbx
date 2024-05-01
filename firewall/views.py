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
                if form.cleaned_data['ipv6len'] < 32:
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
                if form.cleaned_data['ipv6len'] < 32:
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
