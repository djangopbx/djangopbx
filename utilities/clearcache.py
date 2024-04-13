#
#    DjangoPBX
#
#    MIT License
#
#    Copyright (c) 2016 - 2024 Adrian Fretwell <adrian@djangopbx.com>
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
from dialplans.models import Dialplan

phrases_available = True
try:
    from phrases.models import Phrases
except ImportError:
    phrases_available = False

ivrmenus_available = True
try:
    from ivrmenus.models import IvrMenus
except ImportError:
    ivrmenus_available = False


class ClearCache():

    def directory(self, domain_name):
        cache.delete('directory:groups:%s' % domain_name)

    def dialplan(self, domain_name, domain_uuid):
        cache.delete('xmlhandler:context_type')
        cache.delete('dialplan:%s' % domain_name)
        dps = Dialplan.objects.filter(enabled='true', domain_id=domain_uuid, category='Inbound route')
        for dp in dps:
            cache.delete('dialplan:%s:%s' % (dp.context, dp.number))
        return

    def languages(self, domain_uuid):
        del_list = [
            'xmlhandler:lang:default_language',
            'xmlhandler:lang:default_dialect',
            'xmlhandler:lang:default_voice',
            'xmlhandler:lang:sounds_dir'
        ]
        cache.delete_many(del_list)
        if phrases_available:
            ps = Phrases.objects.filter(enabled='true', domain_id=domain_uuid)
            for p in ps:
                cache.delete('languages:%s:%s' % (p.language, str(p.id)))
        return

    def configuration(self, domain_uuid):
        del_list = [
            'xmlhandler:allowed_addresses',
            'configuration:acl.conf',
            'configuration:sofia.conf',
            'configuration:local_stream.conf',
            'configuration:translate.conf',
            'configuration:callcentre.conf'
            'configuration:conference.conf'
        ]
        cache.delete_many(del_list)

        if ivrmenus_available:
            ivrs = IvrMenus.objects.filter(enabled='true', domain_id=domain_uuid)
            for ivr in ivrs:
                cache.delete('configuration:ivr.conf:%s' % str(ivr.id))
        return

    def clearall(self):
        cache.clear()
        return
