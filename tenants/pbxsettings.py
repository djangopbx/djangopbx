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

import uuid
from .models import DefaultSetting, DomainSetting, ProfileSetting, Domain
from accounts.models import ExtensionUser

#
# Class for processing and retrieving settings
#
class PbxSettings():
    true_str = 'true'
    sequence_str = 'sequence'
    text_str = 'text'
    provision_str = 'provision'

    def default_brand_settings(self):
        branding = {}
        dsl = DefaultSetting.objects.filter(
                category='brand',
                value_type=self.text_str,
                enabled=self.true_str).order_by(self.sequence_str)
        for ds in dsl:
            branding[ds.subcategory] = ds.value
        return branding

    def domain_brand_settings(self, bs_dict, domain):
        dsl = DomainSetting.objects.filter(
                domain_id=domain,
                category='brand',
                value_type=self.text_str,
                enabled=self.true_str).order_by(self.sequence_str)
        for ds in dsl:
            bs_dict[ds.subcategory] = ds.value
        return bs_dict

    def default_email_settings(self):
        email_cfg = {}
        dsl = DefaultSetting.objects.filter(
                category='email',
                value_type=self.text_str,
                enabled=self.true_str).order_by(self.sequence_str)
        for ds in dsl:
            email_cfg[ds.subcategory] = ds.value
        return email_cfg

    def default_provision_settings(self, ps_dict):
        dsl = DefaultSetting.objects.filter(
                category=self.provision_str,
                enabled=self.true_str).order_by(self.sequence_str)
        for ds in dsl:
            ps_dict[ds.subcategory] = ds.value
        return ps_dict

    def domain_provision_settings(self, ps_dict, domain):
        dsl = DomainSetting.objects.filter(
                domain_id=domain,
                category=self.provision_str,
                enabled=self.true_str).order_by(self.sequence_str)
        for ds in dsl:
            ps_dict[ds.subcategory] = ds.value
        return ps_dict

    def user_provision_settings(self, ps_dict, user):
        psl = ProfileSetting.objects.filter(
                user_id=user,
                category=self.provision_str,
                enabled=self.true_str).order_by(self.sequence_str)
        for ps in psl:
            ps_dict[ps.subcategory] = ps.value
        return ps_dict

    def feature_sync_vendor_settings(self, user_obj, domain_obj):
        # Tests to see if any vendor synchronisation is enabled
        #  and normalises Yes, No, 1 and 0 to True or False
        fsvs = {}
        feature_key_str = 'feature_key_sync'
        any_set_str = '_any_set'
        sync_enabled = ['1', 'Yes']
        fsvs[any_set_str] = False
        dsl = DefaultSetting.objects.filter(
                category=self.provision_str,
                enabled=self.true_str, subcategory__iendswith=feature_key_str).order_by(self.sequence_str)
        for ds in dsl:
            vendor_key = ds.subcategory.split('_', 1)[0]
            if ds.value in sync_enabled:
                fsvs[vendor_key] = True
                fsvs[any_set_str] = True
            else:
                fsvs[vendor_key] = False
        if isinstance(domain_obj, Domain):
            dsl = DomainSetting.objects.filter(
                domain_id = domain_obj,
                category=self.provision_str,
                enabled=self.true_str, subcategory__iendswith=feature_key_str).order_by(self.sequence_str)
            for ds in dsl:
                vendor_key = ds.subcategory.split('_', 1)[0]
                if ds.value in sync_enabled:
                    fsvs[vendor_key] = True
                    fsvs[any_set_str] = True
                else:
                    fsvs[vendor_key] = False
        if isinstance(user_obj, ExtensionUser):
            dsl = ProfileSetting.objects.filter(
                user_id = user_obj.user_uuid,
                category=self.provision_str,
                enabled=self.true_str, subcategory__iendswith=feature_key_str).order_by(self.sequence_str)
            for ds in dsl:
                vendor_key = ds.subcategory.split('_', 1)[0]
                if ds.value in sync_enabled:
                    fsvs[vendor_key] = True
                    fsvs[any_set_str] = True
                else:
                    fsvs[vendor_key] = False
        return fsvs

    def default_settings(self, cat, subcat, settingtype='text', defaultsetting='', usedefault=False):
        settingList = DefaultSetting.objects.values_list('value', flat=True).filter(
                category=cat,
                subcategory=subcat,
                value_type=settingtype,
                enabled=self.true_str).order_by(self.sequence_str)
        if settingList.count() == 0:
            if usedefault:
                return [defaultsetting]
            else:
                return False
        return settingList

    def domain_settings(self, uuidstr, cat, subcat, settingtype='text', defaultsetting='', usedefault=False):
        settingList = DomainSetting.objects.values_list('value', flat=True).filter(
                domain_id=uuid.UUID(uuidstr),
                category=cat,
                subcategory=subcat,
                value_type=settingtype,
                enabled=self.true_str).order_by(self.sequence_str)

        if settingList.count() == 0:
            if usedefault:
                return [defaultsetting]
            else:
                return False
        return settingList

    def user_settings(self, uuidstr, cat, subcat, settingtype='text', defaultsetting='', usedefault=False):
        settingList = ProfileSetting.objects.values_list('value', flat=True).filter(
                user_id=uuid.UUID(uuidstr),
                category=cat,
                subcategory=subcat,
                value_type=settingtype,
                enabled=self.true_str).order_by(self.sequence_str)

        if settingList.count() == 0:
            if usedefault:
                return [defaultsetting]
            else:
                return False
        return settingList

    def settings(
            self, useruuidstr, domainuuidstr, cat, subcat,
            settingtype='text', defaultsetting='', usedefault=False
            ):
        settingList = self.user_settings(useruuidstr, cat, subcat, settingtype, defaultsetting, False)
        if settingList:
            return settingList
        settingList = self.domain_settings(domainuuidstr, cat, subcat, settingtype, defaultsetting, False)
        if settingList:
            return settingList
        settingList = self.default_settings(cat, subcat, settingtype, defaultsetting, usedefault)
        return settingList

    def dd_settings(
            self, domainuuidstr, cat, subcat,
            settingtype='text', defaultsetting='', usedefault=False
            ):
        settingList = self.domain_settings(domainuuidstr, cat, subcat, settingtype, defaultsetting, False)
        if settingList:
            return settingList
        settingList = self.default_settings(cat, subcat, settingtype, defaultsetting, usedefault)
        return settingList

    def get_domains(self):
        qs_dict = [{i.name: str(i.id)} for i in Domain.objects.filter(enabled=self.true_str)]
        if qs_dict is not None:
            return qs_dict
        return False

    def get_domain(self, dname):
        try:
            d = Domain.objects.get(name=dname)
        except Domain.DoesNotExist:
            d = None
        return d
