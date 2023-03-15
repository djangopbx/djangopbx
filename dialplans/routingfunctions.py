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

import regex as re_alt
from lxml import etree
from io import StringIO
from .models import Dialplan
from django.db.models import Q

class DpRouting():

    def route_to_bridge(self, call_context, digits, toll_allow='', hostname=None):
        dp = Dialplan.objects.filter(
            (Q(context=call_context) | Q(context='${domain_name}')),
            (Q(hostname=hostname) | Q(hostname__isnull=True)),  xml__isnull=False,
            category='Outbound route', enabled='true'
            ).values_list('xml', flat=True).order_by('sequence')


        for xml in dp:
            toll_allow_required = False
            toll_allow_match = False
            digits_match = False
            bridge = []
            regex = re_alt.compile('expression=\"(.*)\"', re_alt.MULTILINE)
            # FreeSWITCH doesn't seem to mind < and > in an XML attribute although technically wrong, but lxml does mind.
            xml = regex.sub(lambda m: m.group().replace('<', "&lt;").replace('>', "&gt;"), xml)

            parser = etree.XMLParser(remove_comments=True)
            tree = etree.parse(StringIO(xml), parser)
            extension = tree.getroot()

            if not etree.iselement(extension):
                continue

            if len(extension):  # check root has children
                if extension.tag == 'extension':
                    for extchild in extension:
                        if extchild.tag == 'condition':
                            cond_field = extchild.get('field')
                            cond_exp = extchild.get('expression')
                            if cond_field == '${toll_allow}':
                                toll_allow_required = True
                                if re_alt.search(cond_exp, toll_allow):
                                    toll_allow_match = True
                                else:
                                    continue
                            if cond_field == 'destination_number':
                                if re_alt.search(cond_exp, digits):
                                    digits_match = True
                                else:
                                    continue

                        if toll_allow_match or digits_match:
                            for condchild in extchild:
                                if condchild.tag == 'action':
                                    app_field = condchild.get('application')
                                    if app_field == 'bridge':
                                        bridge.append(condchild.get('data'))

                    if (not toll_allow_required and digits_match) or (toll_allow_match and digits_match):
                        return bridge

