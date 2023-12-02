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

from django.db.models import Q
from lxml import etree
from .httapihandler import HttApiHandler
from contacts.models import ContactTel
from tenants.models import Profile


class SpeedDialHandler(HttApiHandler):

    handler_name = 'speeddial'

    def get_variables(self):
        self.var_list = [
            'user_uuid',
            'speed_dial'
        ]
        self.var_list.extend(self.domain_var_list)

    def get_data(self):
        if self.exiting:
            return self.return_data('Ok\n')

        self.get_domain_variables()
        speed_dial = self.qdict.get('speed_dial', '~None~')
        user_uuid = self.qdict.get('user_uuid', False)
        if user_uuid:
            q = ContactTel.objects.filter(contact_id_id__domain_id=self.domain_uuid,
                contact_id_id__user_id__user_uuid=user_uuid,
                contact_id_id__enabled='true', speed_dial=speed_dial).first()
            if not q:
                groups = Profile.objects.get(user_uuid=user_uuid).user.groups.all()
                q = ContactTel.objects.filter(contact_id_id__domain_id=self.domain_uuid,
                    contact_id_id__contactgroup__group_id__in=groups,
                    contact_id_id__enabled='true', speed_dial=speed_dial).first()
            if not q:
                q = ContactTel.objects.filter(contact_id_id__domain_id=self.domain_uuid,
                    contact_id_id__enabled='true', speed_dial=speed_dial).first()
        else:
            q = ContactTel.objects.filter(contact_id_id__domain_id=self.domain_uuid,
                contact_id_id__enabled='true', speed_dial=speed_dial).first()

        x_root = self.XrootApi()
        etree.SubElement(x_root, 'params')
        x_work = etree.SubElement(x_root, 'work')
        if q:
            etree.SubElement(x_work, 'execute', application='transfer',
                data='%s XML %s' % (q.number.replace(' ', ''), self.domain_name))
        else:
            etree.SubElement(x_work, 'hangup', cause='UNALLOCATED_NUMBER')

        etree.indent(x_root)
        xml = str(etree.tostring(x_root), "utf-8")
        return xml
