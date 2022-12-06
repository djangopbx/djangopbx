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

    prefix             = forms.CharField(label = _('Prefix'), max_length=16, required = False, help_text = _('Adds and optional prefix to the destination.'))
    destination        = forms.CharField(label = _('Destination'), max_length=128, required = True, help_text = _('Type a DID number, Regex, or use the N,X,Z notation.'))
    calleridname       = forms.CharField(label = _('Caller ID Name'), max_length=128, required = False)
    calleridnumber     = forms.CharField(label = _('Caller ID Prefix'), max_length=128, required = False, help_text = _('This is a short prefix that can be added to the inbound caller ID name.  It helps to identify the trunk if more than one is configured.'))
    context            = forms.CharField(label = _('Context'), max_length=128, initial = 'public', required = True)
    action             = forms.ChoiceField(label = _('Action'), widget=forms.Select)
    calleridnameprefix = forms.CharField(label = _('Caller ID Name Prefix'), max_length=128, required = False)
    record             = forms.ChoiceField(label = _('Record'), widget=forms.Select, choices=EnabledTrueFalseChoice.choices)
    accountcode        = forms.CharField(label = _('Account Code'), max_length=128, required = False)
    enabled            = forms.ChoiceField(label = _('Enabled'), widget=forms.Select, choices=EnabledTrueFalseChoice.choices)
    description        = forms.CharField(label = _('Description'), max_length=128, required = False)


class NewObRouteForm(forms.Form):

    routename          = forms.CharField(label = _('Route Name'), max_length=128, required = True, help_text = _('Type a name for the route that will help you to identify it in the dialplan.'))
    gateway1           = forms.ChoiceField(label = _('Gateway 1'), widget=forms.Select, required = True, help_text = _('Select the gateway to use with this outbound route.'))
    gateway2           = forms.ChoiceField(label = _('Gateway 2'), widget=forms.Select, required = False, help_text = _('Select another gateway as an alternative to use if the first one fails.'))
    gateway3           = forms.ChoiceField(label = _('Gateway 3'), widget=forms.Select, required = False, help_text = _('Select another gateway as an alternative to use if the second one fails.'))
    dpexpression       = forms.CharField(label = _('Dialplan Expression'), max_length=128, required = True)
    prefix             = forms.CharField(label = _('Prefix'), max_length=16, required = False)
    limit              = forms.IntegerField(label = 'Limit', min_value = 0, max_value = 128, initial = 0)
    accountcode        = forms.CharField(label = _('Account Code'), max_length=128, required = False)
    tollallow          = forms.CharField(label = _('Toll Allow'), max_length=32, required = False)
    pinnumbers         = forms.ChoiceField(label = _('PIN Numbers'), widget=forms.Select, choices=EnabledTrueFalseChoice.choices)
    dporder            = forms.IntegerField(label = 'Order', min_value = 10, max_value = 999, initial = 100, help_text = _('Select the order number. The order number determines the order of the outbound routes when there is more than one.'))
    enabled            = forms.ChoiceField(label = _('Enabled'), widget=forms.Select, choices=EnabledTrueFalseChoice.choices)
    description        = forms.CharField(label = _('Description'), max_length=128, required = False)
