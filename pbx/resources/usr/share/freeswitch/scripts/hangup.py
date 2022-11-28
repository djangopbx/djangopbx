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
from freeswitch import *
from resources.email.sendsmtp import Message


def hangup_hook(session, what):
    debug = False
    if debug:
        consoleLog('INFO','[hangup] hook for %s\n' % what)

    return


def fsapi(session, stream, env, args):
    debug = False
    # Un comment to output env to console
    #stream.write('fsapi env!\n' + env.serialize())

    originate_disposition = env.getHeader('originate_disposition')
    if not originate_disposition:
        return

    originate_causes      = env.getHeader('originate_causes')
    if debug:
        consoleLog('INFO', '[hangup] originate_causes: %s\n' % originate_causes)
        consoleLog('INFO', '[hangup] originate_disposition: %s\n' % originate_disposition)

    if not originate_disposition == 'ORIGINATOR_CANCEL':
        return

    uuid                  = env.getHeader('uuid')
    domain_uuid           = env.getHeader('domain_uuid')
    domain_name           = env.getHeader('domain_name')
    sip_to_user           = env.getHeader('sip_to_user')
    dialed_user           = env.getHeader('dialed_user')
    missed_call_app       = env.getHeader('missed_call_app')
    missed_call_data      = env.getHeader('missed_call_data')
    caller_id_name        = env.getHeader('caller_id_name')
    caller_id_number      = env.getHeader('caller_id_number')
    if not caller_id_name:
        caller_id_name = env.getHeader('Caller-Caller-ID-Name')
    if not caller_id_number:
        caller_id_number = env.getHeader('Caller-Caller-ID-Number')

    default_language = env.getHeader('default_language');
    default_dialect  = env.getHeader('default_dialect');

    #if debug:
    #    consoleLog('INFO', '[hangup] domain_uuid: %s\n' % domain_uuid)
    #    consoleLog('INFO', '[hangup] default_language: %s\n' % default_language)
    #    consoleLog('INFO', '[hangup] default_dialect: %s\n' % default_dialect)

    if not missed_call_app:
        return
    if not missed_call_app == 'email':
        return

    m = Message()

    template = m.GetTemplate(domain_uuid, '%s-%s' % (default_language, default_dialect), 'missed', 'default')
    if not template:
        consoleLog('WARNING', '[hangup] No email template missed for domain: %s\n' % domain_name)
        return

    subject = template[0].format(caller_id_name = caller_id_name, caller_id_number = caller_id_number, sip_to_user = sip_to_user, dialed_user = dialed_user)
    body = template[1].format(caller_id_name = caller_id_name, caller_id_number = caller_id_number, sip_to_user = sip_to_user, dialed_user = dialed_user)
    out = m.Send(missed_call_data, subject, body, template[2])
    if debug or not out[0]:
        consoleLog('WARNING', '[hangup] %s\n' % out[1])

    return
