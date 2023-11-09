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

import logging
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from .xmlhandlerfunctions import DirectoryHandler, DialplanHandler, LanguagesHandler, ConfigHandler

logger = logging.getLogger(__name__)


@csrf_exempt
def dialplan(request):
    debug = False
    xmlhf = DialplanHandler()
    allowed_addresses = xmlhf.get_allowed_addresses()

    if request.META['REMOTE_ADDR'] not in allowed_addresses:
        return HttpResponseNotFound()

    if not request.method == 'POST':
        return HttpResponseNotFound()

    if debug:
        logger.info('XML Handler request: {}'.format(request.POST))

    call_context = request.POST.get('Caller-Context', '')
    hostname = request.POST.get('FreeSWITCH-Switchname', '')
    destination_number = request.POST.get('Caller-Destination-Number', '')
    hunt_context = request.POST.get('Hunt-Context')
    hunt_destination_number = request.POST.get('Hunt-Destination-Number')

    if hunt_context:
        call_context = hunt_context

    if hunt_destination_number:
        destination_number = hunt_destination_number

    xml = xmlhf.GetDialplan(call_context, hostname, destination_number)
    if debug:
        logger.info('XML Handler response: {}'.format(xml))

    return HttpResponse(xml, content_type='application/xml')


def staticdialplan(request):
    xmlhf = DialplanHandler()
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
    debug = False
    xmlhf = DirectoryHandler()
    allowed_addresses = xmlhf.get_allowed_addresses()

    if request.META['REMOTE_ADDR'] not in allowed_addresses:
        return HttpResponseNotFound()

    if not request.method == 'POST':
        return HttpResponseNotFound()

    if debug:
        logger.info('XML Handler request: {}'.format(request.POST))

    purpose = request.POST.get('purpose', '')
    action = request.POST.get('action', '')
    domain = request.POST.get('domain')
    user = request.POST.get('user')
    event_calling_function = request.POST.get('Event-Calling-Function', '')
    event_calling_file = request.POST.get('Event-Calling-File', '')

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
    xmlhf = DirectoryHandler()
    allowed_addresses = xmlhf.get_allowed_addresses()

    if request.META['REMOTE_ADDR'] not in allowed_addresses:
        return HttpResponseNotFound()

    if request.method == 'GET':
        xml = xmlhf.GetDirectoryStatic()
    else:
        return HttpResponseNotFound()

    return HttpResponse(xml, content_type='application/xml')

@csrf_exempt
def languages(request):
    debug = False
    xmlhf = LanguagesHandler()
    allowed_addresses = xmlhf.get_allowed_addresses()

    if request.META['REMOTE_ADDR'] not in allowed_addresses:
        return HttpResponseNotFound()

    if not request.method == 'POST':
        return HttpResponseNotFound()

    if debug:
        logger.info('XML Handler request: {}'.format(request.POST))

    lang = request.POST.get('lang', '')
    macro_name = request.POST.get('macro_name', '')

    xml = xmlhf.GetLanguage(lang, macro_name)

    return HttpResponse(xml, content_type='application/xml')

@csrf_exempt
def configuration(request):
    debug = False

    xmlhf = ConfigHandler()
    allowed_addresses = xmlhf.get_allowed_addresses()
    if request.META['REMOTE_ADDR'] not in allowed_addresses:
        return HttpResponseNotFound()
    if not request.method == 'POST':
        return HttpResponseNotFound()
    if debug:
        logger.info('XML Handler request: {}'.format(request.POST))

    hostname = request.POST.get('hostname', '')
    if not hostname:
        xml = xmlhf.NotFoundXml()

    key_value = request.POST.get('key_value', '')
    if key_value == 'acl.conf':
        xml = xmlhf.GetACL()
    elif key_value == 'sofia.conf':
        xml = xmlhf.GetSofia(hostname)
    elif key_value == 'local_stream.conf':
        xml = xmlhf.GetLocalStream()
    elif key_value == 'translate.conf':
        xml = xmlhf.GetTranslate()
    elif key_value == 'ivr.conf':
        xml = xmlhf.GetIvr(request.POST.get('Menu-Name', ''))
    else:
        xml = xmlhf.NotFoundXml()

    return HttpResponse(xml, content_type='application/xml')
