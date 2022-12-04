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
from django.utils.translation import gettext, gettext_lazy as _
from pbx.commonchoices import EnabledTrueFalseChoice
from .dialplanfunctions import DpDestAction


class NewIbRouteForm(forms.Form):

    prefix             = forms.CharField(label = _('Prefix'), max_length=16, required = False)
    destination        = forms.CharField(label = _('Destination'), max_length=128, required = True)
    calleridname       = forms.CharField(label = _('Caller ID Name'), max_length=128, required = False)
    calleridnumber     = forms.CharField(label = _('Caller ID Prefix'), max_length=128, required = False)
    context            = forms.CharField(label = _('Context'), max_length=128, initial = 'public', required = True)
    #action             = forms.ChoiceField(widget=forms.Select, choices=DpDestAction().get_dp_action_choices(request.session('domain_uuid')))
    action             = forms.ChoiceField(widget=forms.Select)
    calleridnameprefix = forms.CharField(label = _('Caller ID Name Prefix'), max_length=128, required = False)
    record             = forms.ChoiceField(widget=forms.Select, choices=EnabledTrueFalseChoice.choices)
    accountcode        = forms.CharField(label = _('Account Code'), max_length=128, required = False)
    enabled            = forms.ChoiceField(widget=forms.Select, choices=EnabledTrueFalseChoice.choices)
    description        = forms.CharField(label = _('Description'), max_length=128, required = False)

