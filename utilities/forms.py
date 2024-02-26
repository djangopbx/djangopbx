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

from django import forms
from django.utils.translation import gettext_lazy as _


class ClearCacheForm(forms.Form):

    directory     = forms.BooleanField(label=_('Directory'), widget=forms.CheckboxInput(attrs={'class': 'form-check'}), required=False, help_text=_('Check to clear cache entries related to extensions and users.'))       # noqa: E501, E221
    dialplan      = forms.BooleanField(label=_('Dialplan'), widget=forms.CheckboxInput(attrs={'class': 'form-check'}), required=False, help_text=_('Check to clear cache entries related to the dialplan.'))                # noqa: E501, E221
    languages     = forms.BooleanField(label=_('Languages'), widget=forms.CheckboxInput(attrs={'class': 'form-check'}), required=False, help_text=_('Check to clear cache entries related languages.'))                     # noqa: E501, E221
    configuration = forms.BooleanField(label=_('Configuration'), widget=forms.CheckboxInput(attrs={'class': 'form-check'}), required=False, help_text=_('Check to clear cache entries related to configuration.'))          # noqa: E501, E221
    clearall      = forms.BooleanField(label=_('Clear Server Cache'), widget=forms.CheckboxInput(attrs={'class': 'form-check'}), required=False, help_text=_('Check to clear the entire server cache - USE WITH CAUTION.')) # noqa: E501, E221


class ReloadXmlForm(forms.Form):

    host = forms.ChoiceField(label=_('Host'), widget=forms.Select(attrs={'class': 'custom-select custom-select-sm'}), required=True, help_text=_('Select the Switch host on which to issue the command.')) # noqa: E501, E221
    xml  = forms.BooleanField(label=_('XML'), widget=forms.CheckboxInput(attrs={'class': 'form-check'}), required=False, help_text=_('Check to re-load Extensible Markup Language files.'))                # noqa: E501, E221
    acl  = forms.BooleanField(label=_('ACL'), widget=forms.CheckboxInput(attrs={'class': 'form-check'}), required=False, help_text=_('Check to re-load Access Control Lists.'))                            # noqa: E501, E221
