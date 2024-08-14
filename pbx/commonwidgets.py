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

#
#  These are Widget classes used by more than one application
#

from django.forms.widgets import Select
from django.forms.widgets import ClearableFileInput
from django.db.models import FileField


# ============= Common Widgets ============================
class ListTextWidget(Select):
    template_name = 'portal/widgets/listtxt.html'

    def format_value(self, value):
        # Copied from forms.Input - makes sure value is rendered properly
        if value == '' or value is None:
            return ''
        if self.is_localized:
            return format.localize_input(value)
        return str(value)


class PlayerAdminFileFieldWidget(ClearableFileInput):
    template_name = 'portal/widgets/player_admin_clearable_file_input.html'


# ============= Common Model Fields =======================
class PbxFileField(FileField):
    def __init__(self, * args, ** kwargs):
        super().__init__(* args, ** kwargs)

    def db_type(self, connection):
        return 'text'
