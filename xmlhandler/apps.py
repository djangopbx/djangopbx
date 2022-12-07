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

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class XmlhandlerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'xmlhandler'
    verbose_name = _('XML Handler')
    pbx_uuid = '847714e5-8cdf-32fd-462c-cbe7e3d633bf'
    pbx_category = 'Switch'
    pbx_subcategory = ''
    pbx_version = '1.0'
    pbx_license = 'MIT License'
    xml_config_allowed_addresses = ['127.0.0.1', '::1']
    context_type = 'multiple'  # Can be multiple or single
    number_as_presence_id = False