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

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from pbx.commonfunctions import shcommand, get_version
from pbx.fseventsocket import EventSocket
from .forms import LogViewerForm
import re
import sys

@staff_member_required
def fslogviewer(request):
    form = LogViewerForm()
    form.fields['logtext'].initial = shcommand(['/usr/local/bin/fslogviewer.sh'])
    form.fields['logtext'].label = 'FreeSWITCH Log (/var/log/freeswitch/freeswitch.log)'

    return render(request, 'status/logviewer.html', {'refresher': 'status:fslogviewer', 'form': form})


@staff_member_required
def djangopbx(request):
    info = {}
    info['Version<br>&nbsp;'] = get_version('pbx')
    info['Git Branch'] = shcommand(['/usr/bin/git', '--git-dir=%s/.git' % settings.BASE_DIR, 'name-rev', '--name-only', 'HEAD'])
    info['Git Commit'] = shcommand(['/usr/bin/git', '--git-dir=%s/.git' % settings.BASE_DIR, 'rev-parse', 'HEAD'])
    info['Git Origin<br>&nbsp;'] = shcommand(['/usr/bin/git', '--git-dir=%s/.git' % settings.BASE_DIR, 'config', '--get', 'remote.origin.url']).replace('.git', '')
    info['Project Path'] = settings.BASE_DIR

    es = EventSocket()
    if es.connect('127.0.0.1', 8021, 'ClueCon'):
        fs_ver = es.send('api version')
        z = re.match('FreeSWITCH Version (\d+\.\d+\.\d+(?:\.\d+)?).*\(.*?(\d+\w+)\s*\)', fs_ver)
        info['Switch Version'] = '%s (%s)' % (z.groups()[0], z.groups()[1])
    info['Python Version'] = sys.version

    return render(request, 'status/infotable.html', {'refresher': 'status:djangopbx', 'info': info, 'title': 'DjangoPBX'})
