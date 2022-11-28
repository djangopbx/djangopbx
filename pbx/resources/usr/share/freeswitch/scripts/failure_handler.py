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
from resources.db.pgdb import PgDb


def handler(session, args):

    debug = True
    if not session:
        return
    if not session.ready():
        return

    domain_uuid                 = session.getVariable('domain_uuid')
    domain_name                 = session.getVariable('domain_name')
    context                     = session.getVariable('context')
    originate_disposition       = session.getVariable('originate_disposition')
    originate_causes            = session.getVariable('originate_causes')
    hangup_on_subscriber_absent = session.getVariable('hangup_on_subscriber_absent')
    hangup_on_call_reject       = session.getVariable('hangup_on_call_reject')
    caller_id_name              = session.getVariable('caller_id_name')
    caller_id_number            = session.getVariable('caller_id_number')
    call_direction              = session.getVariable('call_direction')
    if call_direction == 'local':
        caller_id_name          = session.getVariable('effective_caller_id_name')

    sip_to_user                 = session.getVariable('sip_to_user')
    dialed_user                 = session.getVariable('dialed_user')
    missed_call_app             = session.getVariable('missed_call_app')
    missed_call_data            = session.getVariable('missed_call_data')
    sip_code                    = session.getVariable('last_bridge_proto_specific_hangup_cause')

    if debug:
        consoleLog('INFO', '[failure_handler] originate_causes: %s\n' % originate_causes)
        consoleLog('INFO', '[failure_handler] originate_disposition: %s\n' % originate_disposition)
        consoleLog('INFO', '[failure_handler] hangup_on_subscriber_absent: %s\n' % hangup_on_subscriber_absent)
        consoleLog('INFO', '[failure_handler] hangup_on_call_reject: %s\n' % hangup_on_call_reject)
        consoleLog('INFO', '[failure_handler] sip_code: %s\n' % sip_code)

    if originate_causes:
        array = originate_causes.split(';')
        if ('USER_BUSY' in array) or (sip_code == 'sip:486'):
            originate_disposition = 'USER_BUSY'
            session:setVariable('originate_disposition', originate_disposition)

    if not originate_disposition:
        return

    if originate_disposition == 'USER_BUSY':
        pass
    elif originate_disposition == 'NO_ANSWER':
        pass
    elif originate_disposition == 'USER_NOT_REGISTERED':
        pass
    elif originate_disposition == 'SUBSCRIBER_ABSENT':
        pass
    elif originate_disposition == 'CALL_REJECTED':
        pass

