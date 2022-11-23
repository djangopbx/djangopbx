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
from django.apps import apps
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from .xmlhandlerfunctions import XmlHandlerFunctions

logger = logging.getLogger(__name__)

@csrf_exempt
def index(request):
    debug = False
    if request.META['REMOTE_ADDR'] not in apps.get_app_config('xmlhandler').xml_config_allowed_addresses:
        return HttpResponseNotFound()

    context_type          = apps.get_app_config('xmlhandler').context_type
    number_as_presence_id = apps.get_app_config('xmlhandler').number_as_presence_id

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


        if hunt_context:
            call_context = hunt_context

        if hunt_destination_number:
            destination_number = hunt_destination_number

        if section == 'directory':
            xml = XmlHandlerFunctions().GetDirectory(domain, user, number_as_presence_id)
        if section == 'dialplan':
            xml = XmlHandlerFunctions().GetDialplan(call_context, context_type, hostname, destination_number )
    else:
        return HttpResponseNotFound()

    if debug:
        logger.info('XML Handler response: {}'.format(xml))

    return HttpResponse(xml, content_type='application/xml')


def dialplan(request):
    if request.META['REMOTE_ADDR'] not in apps.get_app_config('xmlhandler').xml_config_allowed_addresses:
        return HttpResponseNotFound()

    if request.method == 'GET':
        hostname = request.POST.get('hostname', 'None')
        xml = XmlHandlerFunctions().GetDialplanStatic(hostname)
    else:
        return HttpResponseNotFound()

    return HttpResponse(xml, content_type='application/xml')


def directory(request):
    if request.META['REMOTE_ADDR'] not in apps.get_app_config('xmlhandler').xml_config_allowed_addresses:
        return HttpResponseNotFound()

    number_as_presence_id = apps.get_app_config('xmlhandler').number_as_presence_id
    if request.method == 'GET':
        xml = XmlHandlerFunctions().GetDirectoryStatic(number_as_presence_id)
    else:
        return HttpResponseNotFound()

    return HttpResponse(xml, content_type='application/xml')

