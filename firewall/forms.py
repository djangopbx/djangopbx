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

from django import forms
from django_ace import AceWidget


class LogViewerForm(forms.Form):
    logtext = forms.CharField(widget=AceWidget(showgutter=False, usesofttabs=False, showprintmargin=False, width="1200px", height="600px", mode='text', theme='cobalt'))


class IpAddressForm(forms.Form):
    ipv4 = forms.GenericIPAddressField(label = 'IPv4 Address', protocol = 'IPv4', required = False)
    ipv4len = forms.IntegerField(label = '/', min_value = 8, max_value = 32, initial = 32)
    ipv6 = forms.GenericIPAddressField(label = 'IPv6 Address', protocol = 'IPv6', required = False)
    ipv6len = forms.IntegerField(label = '/', min_value = 48, max_value = 128, initial = 128)
    setname = forms.CharField(widget=forms.HiddenInput(), required=False)
