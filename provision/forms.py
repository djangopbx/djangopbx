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


class DeviceLinesForm(forms.ModelForm):

    class Meta:
        widgets = {
            'line_number': forms.NumberInput(attrs={'size': 4}),
            'server_address': forms.TextInput(attrs={'size': 15}),
            'server_address_primary': forms.TextInput(attrs={'size': 12}),
            'server_address_secondary': forms.TextInput(attrs={'size': 12}),
            'outbound_proxy_primary': forms.TextInput(attrs={'size': 10}),
            'outbound_proxy_secondary': forms.TextInput(attrs={'size': 10}),
            'display_name': forms.TextInput(attrs={'size': 8}),
            'user_id': forms.TextInput(attrs={'size': 8}),
            'auth_id': forms.TextInput(attrs={'size': 8}),
            'password': forms.TextInput(attrs={'size': 8}),
            'sip_port': forms.NumberInput(attrs={'size': 7}),
            'sip_transport': forms.Select(attrs={'size': 1}),
            'register_expires': forms.NumberInput(attrs={'size': 5}),
            'shared_line': forms.TextInput(attrs={'size': 10}),
            'enabled': forms.Select(attrs={'size': 1})
        }


class DeviceKeysForm(forms.ModelForm):

    class Meta:
        widgets = {
            'category': forms.Select(attrs={'size': 1}),
            'key_id': forms.NumberInput(attrs={'size': 5}),
            'key_type': forms.Select(choices=[('None', 'None')], attrs={'size': 1}),
            'line': forms.NumberInput(attrs={'size': 5}),
            'value': forms.TextInput(attrs={'size': 15}),
            'extension': forms.TextInput(attrs={'size': 15}),
            'label': forms.TextInput(attrs={'size': 15}),
            'icon': forms.TextInput(attrs={'size': 10})
        }


class DeviceForm(forms.ModelForm):

    class Meta:
        widgets = {
            'template': forms.Select(choices=[('None', 'None')]),
        }
        fields = '__all__'
