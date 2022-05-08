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

from django.forms.models import model_to_dict
import uuid
from .models import DefaultSetting, DomainSetting, ProfileSetting, Domain


class PbxSettings():
    def default_settings(self, cat, subcat, settingtype = 'text', defaultsetting = '', usedefault = False):
        settingList = DefaultSetting.objects.values_list('value', flat=True).filter(
                category = cat,
                subcategory = subcat,
                value_type = settingtype,
                enabled  = 'true').order_by('sequence')

        if settingList.count() == 0:
            if usedefault:
                return list(defaultsetting)
            else:
                return False
        return settingList


    def domain_settings(self, uuidstr, cat, subcat, settingtype = 'text', defaultsetting = '', usedefault = False):
        settingList = DomainSetting.objects.values_list('value', flat=True).filter(
                domain_id = uuid.UUID(uuidstr),
                category = cat,
                subcategory = subcat,
                value_type = settingtype,
                enabled  = 'true').order_by('sequence')

        if settingList.count() == 0:
            if usedefault:
                return list(defaultsetting)
            else:
                return False
        return settingList


    def user_settings(self, uuidstr, cat, subcat, settingtype = 'text', defaultsetting = '', usedefault = False):
        settingList = ProfileSetting.objects.values_list('value', flat=True).filter(
                id = uuid.UUID(uuidstr),
                category = cat,
                subcategory = subcat,
                value_type = settingtype,
                enabled  = 'true').order_by('sequence')

        if settingList.count() == 0:
            if usedefault:
                return list(defaultsetting)
            else:
                return False
        return settingList


    def settings(self, useruuidstr, domainuuidstr, cat, subcat, settingtype = 'text', defaultsetting = '', usedefault = False):
        settingList = self.user_settings(useruuidstr, cat, subcat, settingtype, defaultsetting, False)
        if settingList:
            return settingList
        settingList = self.domain_settings(domainuuidstr, cat, subcat, settingtype, defaultsetting, False)
        if settingList:
            return settingList
        settingList = self.default_settings(cat, subcat, settingtype, defaultsetting, usedefault)
        return settingList


    def get_domains(self):
        qs_dict = [{i.name: str(i.id)} for i in Domain.objects.filter(enabled='true')]
        if qs_dict is not None:
            return qs_dict
        return False

