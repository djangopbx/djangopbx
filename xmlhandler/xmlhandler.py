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

from django.conf import settings
from django.core.cache import cache
from lxml import etree
from switch.models import SwitchVariable

class XmlHandler():
    cs_dsn = None

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
        return settings.PBX_XMLH_ALLOWED_ADDRESSES

    def get_language_switch_vars(self):
        cache_key = 'xmlhandler:lang:switchvars'
        cv = cache.get(cache_key)
        if cv:
            return cv
        names = ['default_dialect', 'default_language', 'default_voice']
        lang_dict = {names[0]: 'us', names[1]: 'en', names[2]: 'callie'}
        qs = SwitchVariable.objects.filter(category='Defaults', name__in=names, enabled='true')
        for q in qs:
            lang_dict[q.name] = q.value
        cache.set(cache_key, lang_dict)
        return lang_dict

    def get_callcentre_dsn(self):
        if self.cs_dsn is not None:
            return self.cs_dsn
        cache_key = 'xmlhandler:cc:dsv_value'
        cv = cache.get(cache_key)
        if cv:
            self.cs_dsn = cv
            return cv
        try:
            cs_dsn_r = SwitchVariable.objects.get(enabled='true', category='DSN', name='dsn_callcentre')
            self.cs_dsn = cs_dsn_r.value
        except:
            self.cs_dsn = False
        cache.set(cache_key, self.cs_dsn)
        return self.cs_dsn

    def get_snd_file_prefix(self, soundfile, domain_name = 'None'):
        t_snd_dir = soundfile.split('/')
        if t_snd_dir[0] in settings.PBX_SOUND_DIRS:
            return soundfile
        if settings.PBX_USE_LOCAL_FILE_STORAGE and settings.PBX_FREESWITCH_LOCAL:
            return soundfile
        filestore = settings.PBX_FILESTORES[settings.PBX_DEFAULT_FILESTORE]
        if t_snd_dir[0]: # if True, soundfile does not start with a /
            return '%s%s/%s' % (settings.PBX_XMLH_HTTP_CACHE_SCHEME, filestore, soundfile)
        return '%s%s%s' % (settings.PBX_XMLH_HTTP_CACHE_SCHEME, filestore, soundfile)
