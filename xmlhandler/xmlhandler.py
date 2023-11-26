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

from django.core.cache import cache
from lxml import etree
from tenants.pbxsettings import PbxSettings
from switch.models import SwitchVariable


class XmlHandler():

    def __init__(self):
        self.debug = False

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

    def XrootDynamic(self):
        return etree.XML(
                b'<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n'
                b'<document type=\"freeswitch/xml\"></document>'
                )

    def XrootStatic(self):
        return etree.XML(b'<?xml version=\"1.0\" encoding=\"UTF-8\"?><include></include>\n')

    def get_allowed_addresses(self):
        cache_key = 'xmlhandler:allowed_addresses'
        aa = cache.get(cache_key)
        if aa:
            allowed_addresses = aa.split(',')
        else:
            allowed_addresses = PbxSettings().default_settings('xmlhandler', 'allowed_address', 'array')
            aa = ','.join(allowed_addresses)
            cache.set(cache_key, aa)
        return allowed_addresses

    def get_default_language(self):
        cache_key = 'xmlhandler:lang:default_language'
        cv = cache.get(cache_key)
        if cv:
            return cv
        sv = SwitchVariable.objects.filter(category='defaults', name='default_language', enabled='true').first()
        if sv is None:
            cv = 'en'
        else:
            cv = sv.value
        cache.set(cache_key, cv)
        return cv

    def get_default_dialect(self):
        cache_key = 'xmlhandler:lang:default_dialect'
        cv = cache.get(cache_key)
        if cv:
            return cv
        sv = SwitchVariable.objects.filter(category='defaults', name='default_dialect', enabled='true').first()
        if sv is None:
            cv = 'us'
        else:
            cv = sv.value
        cache.set(cache_key, cv)
        return cv

    def get_default_voice(self):
        cache_key = 'xmlhandler:lang:default_voice'
        cv = cache.get(cache_key)
        if cv:
            return cv
        sv = SwitchVariable.objects.filter(category='defaults', name='default_voice', enabled='true').first()
        if sv is None:
            cv = 'callie'
        else:
            cv = sv.value
        cache.set(cache_key, cv)
        return cv

