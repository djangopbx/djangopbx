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

from django.core.cache import cache
from django.db.models import Q
from dialplans.models import Dialplan
from accounts.models import Extension


class XmlHandlerFunctions():

    def NotFoundXml(self):
        return '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<document type="freeswitch/xml">
  <section name="result">
    <result status="not found" />
  </section>
</document>
'''

    def NotFoundPublic(self, xml_list):
        xml_list.append('''<extension name="not-found" continue="false" uuid="9913df49-0757-414b-8cf9-bcae2fd81ae7">
  <condition field="" expression="">
    <action application="set" data="call_direction=inbound" inline="true"/>
    <action application="log" data="WARNING [inbound routes] 404 not found ${sip_network_ip}" inline="true"/>
  </condition>
</extension>
''')
        return xml_list


    def XmlHeader(self, name, context):
        xml = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<document type="freeswitch/xml">
    <section name="{}" description="">
        <context name="{}">
'''
        return xml.format(name, context)


    def XmlFooter(self):
        return '''    </context>
  </section>
</document>
'''


    def GetDirectory(self, domain, user):
        pass


    def GetDialplan(self, caller_context, context_type, hostname, destination_number):
        xml_list = list()
        call_context = caller_context
        if caller_context == '':
            call_context = 'public'
        context_name = call_context
        if call_context == 'public' or call_context[:7] == 'public@' or call_context[-7:] == '.public':
            context_name = 'public'

        dialplan_cache_key = 'dialplan:%s' % call_context
        if context_name == 'public' and context_type == "single":
            dialplan_cache_key = 'dialplan:%s:%s' % (call_context, destination_number)

        xml = cache.get(dialplan_cache_key)
        if xml:
            return xml

        xml_list.append(self.XmlHeader('dialplan', call_context))

        if context_name == 'public' and context_type == 'single':
            xml_list.extend(Dialplan.objects.filter((Q(category = 'Inbound route',  number = destination_number) | Q(context__contains='public', domain_id__isnull=True)), (Q(hostname = hostname) | Q(hostname__isnull=True)), enabled = 'true').values_list('xml', flat=True).order_by('sequence'))
            if len(xml_list) == 1:
                xml_list = self.NotFoundPublic(xml_list)
        else:
            if context_name == "public" or ('@' in context_name):
                xml_list.extend(Dialplan.objects.filter((Q(hostname = hostname) | Q(hostname__isnull=True)), context = call_context, enabled = 'true').values_list('xml', flat=True).order_by('sequence'))
            else:
                xml_list.extend(Dialplan.objects.filter((Q(context = call_context) | Q(context = '${domain_name}')), (Q(hostname = hostname) | Q(hostname__isnull=True)), enabled = 'true').values_list('xml', flat=True).order_by('sequence'))

        if len(xml_list) == 0:
            return self.NotFoundXml()

        xml_list.append(self.XmlFooter())

        xml = '\n'
        xml = xml.join(xml_list)
        cache.set(dialplan_cache_key, xml)
        return xml

