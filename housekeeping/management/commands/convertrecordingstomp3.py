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

import os
from django.utils import timezone
from django.core.management.base import BaseCommand
from pbx.commonfunctions import shcommand
from xmlcdr.models import XmlCdr


class Command(BaseCommand):
    help = 'Convert recordings to mp3'

    def handle(self, *args, **kwargs):
        qs = XmlCdr.objects.filter(end_stamp__date=timezone.now().date() - timezone.timedelta(1),
             record_path__isnull=False, record_name__isnull=False)
        for q in qs:
            if q.record_name.endswith('wav'):
                infile = os.path.join(q.record_path, q.record_name)
                outname = q.record_name.replace('.wav', '.mp3')
                outfile = os.path.join(q.record_path, outname)
                shcommand(['/usr/bin/lame', '-b', '16', '-m', 'm', '-q', '8', infile, outfile])
                q.record_name = outname
                q.save()
                os.remove(infile)
