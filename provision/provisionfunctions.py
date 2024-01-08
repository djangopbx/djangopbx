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

import os
#import socket
from django.apps import apps
from django.conf import settings
#from lxml import etree
#from io import StringIO
import provision.models
#from tenants.pbxsettings import PbxSettings
#from pbx.commonfunctions import shcommand
from .models import (
    DeviceVendors, DeviceVendorFunctions, DeviceProfiles,
    DeviceProfileSettings, DeviceProfileKeys, DeviceLines, DeviceKeys, DeviceSettings
)


class DeviceVendorFunctionChoice():
    def choices(self, vendor=None):
        # This try/except is a workaround to prevent a relation not found error on initial migrate
        try:
            if vendor:
                return [(c.value, c.name) for c in DeviceVendorFunctions.objects.filter(enabled='true', vendor_id_id=vendor)]
            return [(c.value, '%s -> %s' % (c.vendor_id.name, c.name)) for c in DeviceVendorFunctions.objects.filter(enabled='true')]
        except:
            return [('None', 'None')]


class ProvisionFunctions():
    template_list = []

    def __init__(self):
        self.path_of_templates = settings.BASE_DIR / 'provision/templates/provision'

    def get_template_list(self):
        if apps.ready:
            # This try/except is a workaround to prevent a relation not found error on initial migrate
            try:
                vendor_list = DeviceVendors.objects.filter(enabled='true')
                for v in vendor_list:
                    for it in os.scandir(os.path.join(self.path_of_templates, v.name)):
                        if it.is_dir():
                            relpath = os.path.relpath(it.path, start=self.path_of_templates)
                            self.template_list.append((relpath, relpath))
            except:
                pass
        self.template_list.sort()
        return self.template_list

    def device_settings(self, ps_dict):
        dsl = DeviceSettings.objects.filter(
                enabled='true').order_by('name')
        for ds in dsl:
            ps_dict[ds.name] = ds.value
        return ps_dict

    def device_profile_settings(self, ps_dict, profile_id):
        dsl = DeviceProfileSettings.objects.filter(
                profile_id=profile_id,
                enabled='true').order_by('name')
        for ds in dsl:
            ps_dict[ds.name] = ds.value
        return ps_dict

    def device_keys(self, device, category):
        if device.profile_id:
            dk = DeviceKeys.objects.values(
                'key_id', 'key_type', 'line', 'value', 'extension', 'label', 'icon'
                ).filter(device_id=device, category=category, key_type__isnull=False).order_by('key_id').union(
                    DeviceProfileKeys.objects.values(
                    'key_id', 'key_type', 'line', 'value', 'extension', 'label', 'icon'
                    ).filter(profile_id=device.profile_id, category=category, key_type__isnull=False))
        else:
            dk = DeviceKeys.objects.values(
                'key_id', 'key_type', 'line', 'value', 'extension', 'label', 'icon'
                ).filter(device_id=device, category=category, key_type__isnull=False).order_by('key_id')
        return dk
