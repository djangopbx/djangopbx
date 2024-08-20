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

from lxml import etree
from .httapihandler import HttApiHandler
from pbx.pbxsendsmtp import PbxTemplateMessage


class HangupHandler(HttApiHandler):

    handler_name = 'hangup'

    def get_data(self):

        missed_call_app  = self.session_json.get('variable_missed_call_app')        # noqa: E221
        missed_call_data = self.session_json.get('variable_missed_call_data')       # noqa: E221
        caller_id_name   = self.session_json.get('variable_caller_id_name', ' ')    # noqa: E221
        caller_id_number = self.session_json.get('variable_caller_id_number', ' ')  # noqa: E221
        sip_to_user      = self.session_json.get('variable_sip_to_user', ' ')       # noqa: E221
        dialed_user      = self.session_json.get('variable_dialed_user', ' ')       # noqa: E221
        default_language = self.session_json.get('variable_default_language', ' ')  # noqa: E221
        default_dialect  = self.session_json.get('variable_default_dialect', ' ')   # noqa: E221

        if not missed_call_app:
            return self.return_data('Ok\n')
        if not missed_call_app == 'email':
            return self.return_data('Ok\n')
        if not missed_call_data:
            return self.return_data('Ok\n')

        m = PbxTemplateMessage()
        template = m.GetTemplate(
            self.domain_uuid, '%s-%s' % (default_language, default_dialect),
            'missed', 'default'
            )
        if not template[0]:
            self.logger.warn(self.log_header.format('hangup', 'Email Template mising'))
            return self.return_data('Ok\n')

        subject = template[0].format(
                caller_id_name=caller_id_name, caller_id_number=caller_id_number,
                sip_to_user=sip_to_user, dialed_user=dialed_user
                )
        body = template[1].format(
                caller_id_name=caller_id_name, caller_id_number=caller_id_number,
                sip_to_user=sip_to_user, dialed_user=dialed_user
                )
        out = m.Send(missed_call_data, subject, body, template[2])
        if self.debug or not out[0]:
            self.logger.warn(self.log_header.format('hangup', out[1]))

        return self.return_data('Ok\n')
