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

import os
from django.utils.translation import gettext_lazy as _
from .models import SwitchVariable
from tenants.pbxsettings import PbxSettings

phrases_available = True
try:
    from phrases.models import Phrases
except ImportError:
    phrases_available = False

moh_available = True
try:
    from musiconhold.models import MusicOnHold
except ImportError:
    moh_available = False


class SwitchSounds():

    def __init__(self):
        self.sounds_dir = '/'
        self.recordings_dir = False
        self.sounds_dir = False
        self.voice_dir = False

    def get_languages(self):
        lang_list = []
        self.get_sounds_dir()
        for f1 in os.scandir(self.sounds_dir):
            if f1.is_dir():
                d1 = os.path.relpath(f1.path, start=self.sounds_dir)
                if len(d1) == 2:
                    for f2 in os.scandir(f1.path):
                        if f2.is_dir():
                            d2 = os.path.relpath(f2.path, start=f1.path)
                            if len(d2) == 2:
                                for f3 in os.scandir(f2.path):
                                    if f3.is_dir():
                                        d3 = os.path.relpath(f3.path, start=f2.path)
                                        lang_list.append(('%s/%s/%s' % (d1, d2, d3), '%s-%s %s' % (d1, d2, d3)))

        return lang_list

    def sounds_dir_scan(self, sdir, rdir=None ):
        if not rdir:
            rdir = sdir
        dlist =[]
        for f in os.scandir(sdir):
            if f.is_dir():
                if not f.name in ['flac', '16000', '32000', '48000', '64000']:
                    dlist.extend(self.sounds_dir_scan(f.path, rdir))
            else:
                dlist.append(os.path.relpath(f.path, start=rdir).replace('/8000',''))
        dlist.sort()
        return dlist

    def recordings_dir_scan(self, sdir, rdir=None ):
        if not rdir:
            rdir = sdir
        dlist =[]
        for f in os.scandir(sdir):
            if f.is_dir():
                if not f.name in ['archive']:
                    dlist.extend(self.recordingsdir_scan(f.path, rdir))
            else:
                dlist.append(os.path.relpath(f.path, start=rdir).replace('/8000',''))
        dlist.sort()
        return dlist

    def get_sounds_dir(self):
        if self.sounds_dir:
            return self.sounds_dir
        soundslist = PbxSettings().default_settings('switch', 'sounds', 'dir')
        if soundslist:
            sounddir = soundslist[0]
        else:
            sounddir = '/usr/share/freeswitch/sounds'
        self.sounds_dir = sounddir
        return sounddir

    def get_recordings_dir(self, domain_name):
        if self.recordings_dir:
            return self.recordings_dir
        reclist = PbxSettings().default_settings('switch', 'recordings', 'dir')
        if reclist:
            recdir = os.path.join(reclist[0], domain_name)
        else:
            recdir = os.path.join('/usr/share/freeswitch/recordings', domain_name)
        self.recordings_dir = recdir
        return recdir


    def get_voice_dir(self):
        if self.voice_dir:
            return self.voice_dir
        dl = 'en'
        dd = 'us'
        dv = 'callie'
        slist = SwitchVariable.objects.values_list('value', flat=True).filter(enabled='true', category='Defaults', name='default_language')
        #using len() because we are going to get the results anyway, slist.count() would mead another hit on the DB
        if len(slist) == 1:
            dl = slist[0]
        slist = SwitchVariable.objects.values_list('value', flat=True).filter(enabled='true', category='Defaults', name='default_dialect')
        if len(slist) == 1:
            dd = slist[0]
        slist = SwitchVariable.objects.values_list('value', flat=True).filter(enabled='true', category='Defaults', name='default_voice')
        if len(slist) == 1:
            dv = slist[0]
        self.voice_dir = '%s/%s/%s' % (dl, dd, dv)
        return self.voice_dir

    def get_recordings_list(self, domain_name, full_path=False):
        rec_file_list = []
        rec_file_list = self.recordings_dir_scan(self.get_recordings_dir(domain_name))
        if full_path:
            return list(('{}/{}'.format(self.recordings_dir, a), a) for a in rec_file_list)
        return list((a, a) for a in rec_file_list)

    def get_phrases_list(self, domain_name):
        phrase_list = []
        d = PbxSettings().get_domain(domain_name)
        if d:
            ps = Phrases.objects.filter(domain_id = d.id, enabled='true').order_by('name')
            if len(ps) < 1:
                phrases_available = False
            for p in ps:
                phrase_list.append(('phrase:{}'.format(p.id), p.name))
        return phrase_list

    def get_sounds_list(self):
        sound_file_list = []
        sound_file_list = self.sounds_dir_scan(os.path.join(self.get_sounds_dir(), self.get_voice_dir()))
        return list((a, a) for a in sound_file_list)

    def decorate(self, text, decorate):
        if decorate:
            return '--- %s ----------' % _(text)
        else:
            return _(text)

    def get_sounds_choices_list(self, domain_name, decorate=False, opt=255):
        sounds_choices = []
        if opt & 1 == 1:
            sounds_choices.append((self.decorate('Miscellaneous', decorate), [('say:', 'Say'), ('tone_stream:', 'Tone Stream')]))
        if opt & 2 == 2:
            if phrases_available:
                phrase_list = self.get_phrases_list(domain_name)
                if phrases_available:
                    sounds_choices.append((self.decorate('Phrases', decorate), phrase_list))
        if opt & 4 == 4:
            if os.path.exists(self.get_recordings_dir(domain_name)):
                sounds_choices.append((self.decorate('Recordings', decorate), self.get_recordings_list(domain_name, True)))
        if opt & 8 == 8:
            if os.path.exists(self.get_sounds_dir()):
                sounds_choices.append((self.decorate('Sounds', decorate), self.get_sounds_list()))
        return sounds_choices

    def get_tones(self, category):
        tone_list = []
        rts = SwitchVariable.objects.filter(enabled='true', category=category).order_by('name')
        for rt in rts:
            tone_list.append(('${%s}' % rt.name, rt.name))
        return tone_list

    def get_moh_list(self):
        moh_list = []
        mohs = MusicOnHold.objects.order_by('name').distinct('name')
        for moh in mohs:
            moh_list.append(('local_stream://%s' % moh.name, moh.name))
        return moh_list

    def get_ringback_choices_list(self, domain_name):
        ringback_choices = []
        if moh_available:
            ringback_choices.append((_('Music on Hold'), self.get_moh_list()))
        if os.path.exists(self.get_recordings_dir(domain_name)):
            ringback_choices.append((_('Recordings'), self.get_recordings_list(domain_name, True)))
        ringback_choices.append((_('Ringtones'), self.get_tones('Ringtones')))
        ringback_choices.append((_('Tones'), self.get_tones('Tones')))
        return ringback_choices

    def get_record_template(self, domain_name):
        rec_dir = self.get_recordings_dir(domain_name)
        return '%s/archive/${strftime(%%Y)}/${strftime(%%b)}/${strftime(%%d)}/${uuid}.${record_ext}' % rec_dir

    def get_cc_record(self, domain_name):
        return [('', 'False'), (self.get_record_template(domain_name), 'True')]

    def get_default_ringback(self):
        dfr = SwitchVariable.objects.filter(enabled='true', category='Defaults', name='ringback').first()
        if dfr.value:
            dr = dfr.value.replace('$', '').replace('{', '').replace('}', '')
            r = SwitchVariable.objects.filter(enabled='true', category='Ringtones', name=dr).first()
            if r:
                return r.value
        return '%(400,200,400,450);%(400,2000,400,450)'
