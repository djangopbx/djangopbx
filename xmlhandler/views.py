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

import logging
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from .xmlhandlerfunctions import DirectoryHandler, DialplanHandler

logger = logging.getLogger(__name__)


'''
def index(request):
    debug = False
    xmlhf = XmlHandlerFunctions()
    allowed_addresses = xmlhf.get_allowed_addresses()

    if request.META['REMOTE_ADDR'] not in allowed_addresses:
        return HttpResponseNotFound()

    if request.method == 'POST':
        if debug:
            logger.info('XML Handler request: {}'.format(request.POST))

        #domain_name     = request.POST.get('sip_from_host')
        #if not domain_name:
        #    domain_name = request.POST.get('domain_name')
        #if not domain_name:
        #    domain_name = request.POST.get('variable_domain_name')
        #if not domain_name:
        #    domain_name = request.POST.get('variable_sip_from_host')

        domain             = request.POST.get('domain')
        #purpose            = request.POST.get('purpose')
        action             = request.POST.get('action')
        profile            = request.POST.get('profile')
        key                = request.POST.get('key')
        user               = request.POST.get('user')
        user_context       = request.POST.get('variable_user_context', '')
        call_context       = request.POST.get('Caller-Context', '')
        destination_number = request.POST.get('Caller-Destination-Number', '')
        caller_id_number   = request.POST.get('Caller-Caller-ID-Number', '')
        hunt_context       = request.POST.get('Hunt-Context')
        section            = request.POST.get('section', '')
        hostname           = request.POST.get('FreeSWITCH-Switchname', '')
        hunt_destination_number = request.POST.get('Hunt-Destination-Number')

        #if action:
        #    print('Action: %s' % action)

        if hunt_context:
            call_context = hunt_context

        if hunt_destination_number:
            destination_number = hunt_destination_number

        if section == 'directory':
            event_calling_function = request.POST.get('Event-Calling-Function', '')
            if event_calling_function == 'switch_load_network_lists':
                xml = xmlhf.GetAcl(domain)
            elif event_calling_function == 'switch_xml_locate_domain':
                xml = xmlhf.GetDomain(domain)
            else:
                xml = xmlhf.GetDirectory(domain, user)

        if section == 'dialplan':
            xml = xmlhf.GetDialplan(call_context, hostname, destination_number )

    else:
        return HttpResponseNotFound()

    if debug:
        logger.info('XML Handler response: {}'.format(xml))

    return HttpResponse(xml, content_type='application/xml')
'''

@csrf_exempt
def dialplan(request):
    debug = True
    xmlhf = DialplanHandler()
    allowed_addresses = xmlhf.get_allowed_addresses()

    if request.META['REMOTE_ADDR'] not in allowed_addresses:
        return HttpResponseNotFound()

    if not request.method == 'POST':
        return HttpResponseNotFound()

    if debug:
        logger.info('XML Handler request: {}'.format(request.POST))

    call_context            = request.POST.get('Caller-Context', '')
    hostname                = request.POST.get('FreeSWITCH-Switchname', '')
    destination_number      = request.POST.get('Caller-Destination-Number', '')
    hunt_context            = request.POST.get('Hunt-Context')
    hunt_destination_number = request.POST.get('Hunt-Destination-Number')

    if hunt_context:
        call_context = hunt_context

    if hunt_destination_number:
        destination_number = hunt_destination_number

    xml = xmlhf.GetDialplan(call_context, hostname, destination_number )
    if debug:
        logger.info('XML Handler response: {}'.format(xml))

    return HttpResponse(xml, content_type='application/xml')


def staticdialplan(request):
    xmlhf = XmlHandlerFunctions()
    allowed_addresses = xmlhf.get_allowed_addresses()

    if request.META['REMOTE_ADDR'] not in allowed_addresses:
        return HttpResponseNotFound()

    if request.method == 'GET':
        hostname = request.GET.get('hostname', 'None')
        xml = xmlhf.GetDialplanStatic(hostname)
    else:
        return HttpResponseNotFound()

    return HttpResponse(xml, content_type='application/xml')


@csrf_exempt
def directory(request):
    debug = True
    xmlhf = DirectoryHandler()
    allowed_addresses = xmlhf.get_allowed_addresses()

    if request.META['REMOTE_ADDR'] not in allowed_addresses:
        return HttpResponseNotFound()

    if not request.method == 'POST':
        return HttpResponseNotFound()

    if debug:
        logger.info('XML Handler request: {}'.format(request.POST))

    purpose                = request.POST.get('purpose', '')
    action                 = request.POST.get('action', '')
    domain                 = request.POST.get('domain')
    user                   = request.POST.get('user')
    event_calling_function = request.POST.get('Event-Calling-Function', '')
    event_calling_file     = request.POST.get('Event-Calling-File', '')

    if purpose == 'gateways':
        xml = xmlhf.GetDomain()
    elif action == 'message-countl':
        xml = xmlhf.GetDirectory(domain, user)
    elif action == 'group_call':
        xml = xmlhf.GetGroupCall(domain)
    elif action == 'reverse-auth-lookup':
        xml = xmlhf.GetReverseAuthLookup()
    elif event_calling_function == 'switch_xml_locate_domain':
        xml = xmlhf.GetDomain()
    elif event_calling_function == 'switch_load_network_lists':
        xml = xmlhf.GetAcl(domain)
    elif event_calling_function == 'populate_database' and event_calling_file == 'mod_directory.c':
        xml = xmlhf.GetPopulateDirectory(domain)
    else:
        xml = xmlhf.GetDirectory(domain, user)

    if debug:
        logger.info('XML Handler response: {}'.format(xml))

    return HttpResponse(xml, content_type='application/xml')


def staticdirectory(request):
    xmlhf = XmlHandlerFunctions()
    allowed_addresses = xmlhf.get_allowed_addresses()

    if request.META['REMOTE_ADDR'] not in allowed_addresses:
        return HttpResponseNotFound()

    if request.method == 'GET':
        xml = xmlhf.GetDirectoryStatic()
    else:
        return HttpResponseNotFound()

    return HttpResponse(xml, content_type='application/xml')

