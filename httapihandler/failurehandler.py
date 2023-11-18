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


class FailureHandler(HttApiHandler):

    handler_name = 'failure'

    def get_variables(self):
        self.var_list = [
        'originate_disposition',
        'dialed_extension',
        'last_busy_dialed_extension',
        'forward_busy_enabled',
        'forward_busy_destination',
        'forward_busy_destination',
        'forward_no_answer_enabled',
        'forward_no_answer_destination',
        'forward_user_not_registered_enabled',
        'forward_user_not_registered_destination'
        ]
        self.var_list.extend(self.domain_var_list)

    def get_data(self):
        no_work = True
        if self.exiting:
            return self.return_data('Ok\n')

        self.get_domain_variables()
        originate_disposition = self.qdict.get('originate_disposition')
        dialed_extension = self.qdict.get('dialed_extension')
        context = self.qdict.get('Caller-Context')
        if not context:
            context = self.domain_name

        x_root = self.XrootApi()
        etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')

        if originate_disposition == 'USER_BUSY':
            last_busy_dialed_extension = self.qdict.get('last_busy_dialed_extension', '~None~')
            if self.debug:
                self.logger.debug(self.log_header.format(
                    'falurehandler', 'last_busy_dialed_extension %s' % last_busy_dialed_extension
                    ))
            if dialed_extension and last_busy_dialed_extension:
                if not dialed_extension == last_busy_dialed_extension:
                    forward_busy_enabled = self.qdict.get('forward_busy_enabled', 'false')
                    if forward_busy_enabled:
                        if forward_busy_enabled == 'true':
                            forward_busy_destination = self.qdict.get('forward_busy_destination')
                            no_work = False
                            if forward_busy_destination:
                                etree.SubElement(
                                    x_work, 'execute', application='set',
                                    data='last_busy_dialed_extension=%s' % dialed_extension
                                    )
                                x_log = etree.SubElement(x_work, 'log', level='NOTICE')
                                x_log.text = 'forwarding on busy to: %s' % forward_busy_destination
                                etree.SubElement(
                                    x_work, 'execute', application='transfer',
                                    data='%s XML %s' % (forward_busy_destination, context)
                                    )
                            else:
                                x_log = etree.SubElement(x_work, 'log', level='NOTICE')
                                x_log.text = 'forwarding on busy with empty destination: hangup(USER_BUSY)'
                                etree.SubElement(x_work, 'hangup', cause='USER_BUSY')
            if no_work:
                etree.SubElement(x_work, 'hangup', cause='USER_BUSY')

        elif originate_disposition == 'NO_ANSWER':
            forward_no_answer_enabled = self.qdict.get('forward_no_answer_enabled')
            if forward_no_answer_enabled:
                if forward_no_answer_enabled == 'true':
                    forward_no_answer_destination = self.qdict.get('forward_no_answer_destination')
                    no_work = False
                    if forward_no_answer_destination:
                        x_log = etree.SubElement(x_work, 'log', level='NOTICE')
                        x_log.text = 'forwarding on no answer to: %s' % forward_no_answer_destination
                        etree.SubElement(
                            x_work, 'execute', application='transfer',
                            data='%s XML %s' % (forward_no_answer_destination, context)
                            )
                    else:
                        x_log = etree.SubElement(x_work, 'log', level='NOTICE')
                        x_log.text = 'forwarding on no answer with empty destination: hangup(NO_ANSWER)'
                        etree.SubElement(x_work, 'hangup', cause='NO_ANSWER')
            if no_work:
                etree.SubElement(x_work, 'hangup', cause='NO_ANSWER')

        elif originate_disposition == 'USER_NOT_REGISTERED':
            forward_user_not_registered_enabled = self.qdict.get('forward_user_not_registered_enabled')
            if forward_user_not_registered_enabled:
                if forward_user_not_registered_enabled == 'true':
                    forward_user_not_registered_destination = self.qdict.get(
                        'forward_user_not_registered_destination'
                        )
                    no_work = False
                    if forward_user_not_registered_destination:
                        x_log = etree.SubElement(x_work, 'log', level='NOTICE')
                        x_log.text = 'forwarding on not registerd to: %s' % forward_user_not_registered_destination
                        etree.SubElement(
                            x_work, 'execute', application='transfer',
                            data='%s XML %s' % (forward_user_not_registered_destination, context)
                            )
                    else:
                        x_log = etree.SubElement(x_work, 'log', level='NOTICE')
                        x_log.text = 'forwarding on user not registered with empty destination: hangup(NO_ANSWER)'
                        etree.SubElement(x_work, 'hangup', cause='NO_ANSWER')
            if no_work:
                etree.SubElement(x_work, 'hangup', cause='NO_ANSWER')

        elif originate_disposition == 'SUBSCRIBER_ABSENT':
            no_work = False
            x_log = etree.SubElement(x_work, 'log', level='NOTICE')
            x_log.text = 'subscriber absent: %s' % dialed_extension
            etree.SubElement(x_work, 'hangup', cause='UNALLOCATED_NUMBER')

        elif originate_disposition == 'CALL_REJECTED':
            no_work = False
            x_log = etree.SubElement(x_work, 'log', level='NOTICE')
            x_log.text = 'call rejected'
            etree.SubElement(x_work, 'hangup')

        if no_work:
            etree.SubElement(x_work, 'hangup')

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml
