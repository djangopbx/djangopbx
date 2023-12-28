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
from django.utils.translation import gettext_lazy as _
from pbx.commonchoices import EnabledTrueFalseChoice
from pbx.commondestination import CommonDestAction
from tenants.pbxsettings import PbxSettings
import json
from copy import deepcopy
from .timeconditions import TimeConditions


class NewIbRouteForm(forms.Form):

    prefix             = forms.CharField(label=_('Prefix'), widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), max_length=16, required=False, help_text=_('Adds and optional prefix to the destination.'))               # noqa: E501, E221
    destination        = forms.CharField(label=_('Destination'), widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), max_length=128, required=True, help_text=_('Type a DID number, Regex, or use the N,X,Z notation.'))  # noqa: E501, E221
#    calleridname       = forms.CharField(label=_('Caller ID Name'), widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), max_length=128, required=False)              # noqa: E501, E221
#    calleridnumber     = forms.CharField(label=_('Caller ID Prefix'), widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), max_length=128, required=False, help_text=_('This is a short prefix that can be added to the inbound caller ID name.  It helps to identify the trunk if more than one is configured.'))  # noqa: E501, E221
    context            = forms.CharField(label=_('Context'), widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), max_length=128, initial='public', required=True)  # noqa: E501, E221
    action             = forms.ChoiceField(label=_('Action'), widget=forms.Select(attrs={'class': 'custom-select custom-select-sm'}))                                                       # noqa: E501, E221
    calleridnameprefix = forms.CharField(label=_('Caller ID Name Prefix'), widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), max_length=128, required=False)       # noqa: E501, E221
    record             = forms.ChoiceField(label=_('Record'), widget=forms.Select(attrs={'class': 'custom-select custom-select-sm'}), choices=EnabledTrueFalseChoice.choices)               # noqa: E501, E221
    accountcode        = forms.CharField(label=_('Account Code'), widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), max_length=128, required=False)                # noqa: E501, E221
    enabled            = forms.ChoiceField(label=_('Enabled'), widget=forms.Select(attrs={'class': 'custom-select custom-select-sm'}), choices=EnabledTrueFalseChoice.choices)              # noqa: E501, E221
    description        = forms.CharField(label=_('Description'), widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), max_length=128, required=False)                 # noqa: E501, E221


class NewObRouteForm(forms.Form):

    routename          = forms.CharField(label=_('Route Name'), widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), max_length=64, required=True, help_text=_('Type a name for the route that will help you to identify it in the dialplan.'))  # noqa: E501, E221
    gateway1           = forms.ChoiceField(label=_('Gateway 1'), widget=forms.Select(attrs={'class': 'custom-select custom-select-sm'}), required=True, help_text=_('Select the gateway to use with this outbound route.'))                                          # noqa: E501, E221
    gateway2           = forms.ChoiceField(label=_('Gateway 2'), widget=forms.Select(attrs={'class': 'custom-select custom-select-sm'}), required=False, help_text=_('Select another gateway as an alternative to use if the first one fails.'))                     # noqa: E501, E221
    gateway3           = forms.ChoiceField(label=_('Gateway 3'), widget=forms.Select(attrs={'class': 'custom-select custom-select-sm'}), required=False, help_text=_('Select another gateway as an alternative to use if the second one fails.'))                    # noqa: E501, E221
    dpexpression       = forms.CharField(label=_('Dialplan Expression'), widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), max_length=128, required=True)          # noqa: E501, E221
    prefix             = forms.CharField(label=_('Prefix'), widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), max_length=16, required=False)                       # noqa: E501, E221
    limit              = forms.IntegerField(label=_('Limit'), widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'}), min_value=0, max_value=128, initial=0)       # noqa: E501, E221
    accountcode        = forms.CharField(label=_('Account Code'), widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), max_length=128, required=False)                # noqa: E501, E221
    tollallow          = forms.CharField(label=_('Toll Allow'), widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), max_length=32, required=False)                   # noqa: E501, E221
    pinnumbers         = forms.ChoiceField(label=_('PIN Numbers'), widget=forms.Select(attrs={'class': 'custom-select custom-select-sm'}), choices=EnabledTrueFalseChoice.choices)          # noqa: E501, E221
    dporder            = forms.IntegerField(label='Order', widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'}), min_value=10, max_value=999, initial=100, help_text=_('Select the order number. The order number determines the order of the outbound routes when there is more than one.'))  # noqa: E501, E221
    enabled            = forms.ChoiceField(label=_('Enabled'), widget=forms.Select(attrs={'class': 'custom-select custom-select-sm'}), choices=EnabledTrueFalseChoice.choices)              # noqa: E501, E221
    description        = forms.CharField(label=_('Description'), widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), max_length=128, required=False)                 # noqa: E501, E221


class TimeConditionForm(forms.Form):
    name               = forms.CharField(label=_('Name'), widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), max_length=64, required=True, help_text=_('Enter the name for the time condition.'))  # noqa: E501, E221
    number             = forms.CharField(label=_('Extension'), widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), max_length=32, required=True, help_text=_('Enter the extension number.'))        # noqa: E501, E221
    sequence           = forms.IntegerField(label=_('Order'), widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'}), min_value=10, max_value=999, initial=300)  # noqa: E501, E221
    enabled            = forms.ChoiceField(label=_('Enabled'), widget=forms.Select(attrs={'class': 'custom-select custom-select-sm'}), choices=EnabledTrueFalseChoice.choices)            # noqa: E501, E221
    description        = forms.CharField(label=_('Description'), widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}), max_length=128, required=False)               # noqa: E501, E221
    dp_id              = forms.CharField(widget=forms.HiddenInput(), required=False)                                                                                                        # noqa: E501, E221

    a_settings_count = 0
    a_setting_condition_count = {}
    custom_select_classes = 'custom-select custom-select-sm'

    def __init__(self, *args, **kwargs):
        i = 0
        if 'etreeroot' in kwargs:
            i += 1
            etreeroot = kwargs.pop('etreeroot')
        if 'domain_uuid' in kwargs:
            i += 1
            domain_uuid = kwargs.pop('domain_uuid')
        if 'domain_name' in kwargs:
            i += 1
            domain_name = kwargs.pop('domain_name')
        super().__init__(*args, **kwargs)
        if i == 3:
            self.setup_dynamic_fields(etreeroot, domain_uuid, domain_name)

    def setup_dynamic_fields(self, etreeroot, domain_uuid, domain_name):
        tc = TimeConditions()
        tc.build_vr_dict()
        action_choices = CommonDestAction(domain_name, domain_uuid).get_action_choices()
        self.fields['default_action'] = forms.ChoiceField(
            widget=forms.Select(attrs={'class': self.custom_select_classes}),
            choices=action_choices, required=False
            )

        tc_cnd = tc.get_condition_list(True)
        region = PbxSettings().default_settings('time_conditions', 'region', 'text', 'england', True)[0]
        preset_list = PbxSettings().default_settings('time_conditions', 'preset_%s' % region, 'array')
        for pj in preset_list:
            pset_name = list(json.loads(pj))[0]
            field_name = 'preset_%s' % pset_name
            self.fields[field_name] = forms.BooleanField(label=pset_name.replace('_', ' ').title(), required=False)

        i = 0
        for extchild in etreeroot:
            if extchild.tag == 'condition':
                if len(extchild) == 0:
                    continue
                is_preset = False
                for actchild in extchild:
                    a_data = actchild.get('data')
                    if a_data:
                        if a_data[:6] == 'preset':
                            is_preset = True
                            field_name = 'preset_%s' % a_data.split('=')[1]
                            self.a_set_initial_value(field_name, a_data.split('=')[1])

                    a_app = actchild.get('application')
                    if a_app:
                        if not a_app == 'set':
                            if not is_preset:
                                i += 1
                                field_name_a = 'settings_a_%s' % i
                                field_name_s = 'settings_s_%s' % i
                                self.fields[field_name_s] = forms.IntegerField(
                                    widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
                                    min_value=500, max_value=999, initial=500, required=False
                                    )
                                self.a_set_initial_value(field_name_s, '%s' % str(500 + (i*10)))

                                self.fields[field_name_a] = forms.ChoiceField(
                                    widget=forms.Select(attrs={'class': self.custom_select_classes}),
                                    choices=action_choices, required=False
                                    )
                                self.a_set_initial_value(field_name_a, '%s:%s' % (a_app, a_data))
                            self.a_set_initial_value('default_action', '%s:%s' % (a_app, a_data))

                if is_preset:
                    continue
                j = 0
                for m in extchild.attrib:
                    if m == 'break':
                        continue
                    if m == 'field':
                        continue
                    if m == 'expression':
                        continue
                    if m in tc_cnd:
                        j += 1

                        mval = extchild.get(m)
                        if '-' in mval:
                            mval_list = mval.split('-')
                        else:
                            mval_list = [mval, '']

                        field_name = 'settings_c_%s_%s' % (i, j)
                        field_name_v = 'settings_v_%s_%s' % (i, j)
                        field_name_v_hx = '#id_settings_v_%s_%s' % (i, j)
                        field_name_r = 'settings_r_%s_%s' % (i, j)
                        self.fields[field_name] = forms.ChoiceField(
                            widget=forms.Select(attrs={
                                'class': self.custom_select_classes,
                                'hx-get': '/dialplans/tcvrchoice',
                                'hx-target': field_name_v_hx
                                }), choices=tc.get_condition_list(), required=False
                            )
                        self.a_set_initial_value(field_name, m)
                        self.fields[field_name_v] = forms.ChoiceField(
                            widget=forms.Select(attrs={'class': self.custom_select_classes}),
                            choices=tc.vr_dict[m], required=False
                            )
                        empty_option = [('', '')]
                        empty_option.extend(tc.vr_dict[m])
                        self.fields[field_name_r] = forms.ChoiceField(
                            widget=forms.Select(attrs={'class': self.custom_select_classes}),
                            choices=empty_option, required=False
                            )
                        self.a_set_initial_value(field_name_v, mval_list[0])
                        self.a_set_initial_value(field_name_r, mval_list[1])

                # Extra empty condition line in each setting
                j += 1
                field_name = 'settings_c_%s_%s' % (i, j)
                field_name_v_hx = '#id_settings_v_%s_%s' % (i, j)
                self.fields[field_name] = forms.ChoiceField(
                    widget=forms.Select(attrs={
                        'class': self.custom_select_classes,
                        'hx-get': '/dialplans/tcvrchoice',
                        'hx-target': field_name_v_hx
                        }),
                    choices=tc.get_condition_list(), required=False
                    )
                self.a_set_initial_value(field_name, '')
                field_name_v = 'settings_v_%s_%s' % (i, j)
                self.fields[field_name_v] = forms.ChoiceField(
                    widget=forms.Select(attrs={'class': self.custom_select_classes}),
                    choices=tc.vr_choice, required=False
                    )
                self.a_set_initial_value(field_name_v, '')
                field_name_r = 'settings_r_%s_%s' % (i, j)
                self.fields[field_name_r] = forms.ChoiceField(
                    widget=forms.Select(attrs={'class': self.custom_select_classes}),
                    choices=tc.vr_choice, required=False
                    )
                self.a_set_initial_value(field_name_r, '')

                self.a_setting_condition_count[i] = j

        # Extra empty Settings group
        i += 1
        j = 1
        field_name = 'settings_c_%s_%s' % (i, j)
        field_name_v_hx = '#id_settings_v_%s_%s' % (i, j)
        self.fields[field_name] = forms.ChoiceField(
            widget=forms.Select(attrs={
                'class': self.custom_select_classes,
                'hx-get': '/dialplans/tcvrchoice',
                'hx-target': field_name_v_hx
                }),
            choices=tc.get_condition_list(), required=False
            )
        self.a_set_initial_value(field_name, '')
        field_name_v = 'settings_v_%s_%s' % (i, j)
        self.fields[field_name_v] = forms.ChoiceField(
            widget=forms.Select(attrs={'class': self.custom_select_classes}),
            choices=tc.vr_choice, required=False
            )
        self.a_set_initial_value(field_name_v, '')
        field_name_r = 'settings_r_%s_%s' % (i, j)
        self.fields[field_name_r] = forms.ChoiceField(
            widget=forms.Select(attrs={'class': self.custom_select_classes}),
            choices=tc.vr_choice, required=False
            )
        self.a_set_initial_value(field_name_r, '')

        field_name_a = 'settings_a_%s' % i
        field_name_s = 'settings_s_%s' % i
        self.fields[field_name_s] = forms.IntegerField(
            widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            min_value=500, max_value=999, initial=500, required=False
            )
        self.a_set_initial_value(field_name_s, '%s' % str(500 + (i*10)))
        self.fields[field_name_a] = forms.ChoiceField(
            widget=forms.Select(attrs={'class': self.custom_select_classes}),
            choices=action_choices, required=False
            )

        self.a_setting_condition_count[i] = j
        self.a_settings_count = i

        self.fields['settings_count'] = forms.CharField(widget=forms.HiddenInput(), required=False)
        self.a_set_initial_value('settings_count', '%s' % str(i))
        self.fields['setting_condition_count'] = forms.CharField(widget=forms.HiddenInput(), required=False)
        self.a_set_initial_value('setting_condition_count', '%s' % json.dumps(self.a_setting_condition_count))
        self.fields['tcregion'] = forms.CharField(widget=forms.HiddenInput(), required=False)
        self.a_set_initial_value('tcregion', region)

    def get_preset_fields(self):
        for field_name in self.fields:
            if field_name.startswith('preset_'):
                yield self[field_name]

    def get_settings_fields(self):
        lst = []
        d = {}
        dl = []
        for i in range(1, self.a_settings_count):
            for j in range(1, self.a_setting_condition_count[i] + 1):
                lst.append(
                    [
                        self['settings_c_%s_%s' % (i, j)],
                        self['settings_v_%s_%s' % (i, j)],
                        self['settings_r_%s_%s' % (i, j)]
                    ]
                    )
            d['set'] = deepcopy(lst)
            lst.clear()
            d[i] = [self['settings_a_%s' % i], self['settings_s_%s' % i]]
            dl.append(deepcopy(d))
            d.clear()
        return dl

    def a_set_initial_value(self, field, ival):
        try:
            self.initial[field] = ival
        except IndexError:
            self.initial[field] = ''
