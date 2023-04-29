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
#  These are Choices classes used by more than one application
#

from django.db import models
from django.utils.translation import gettext_lazy as _


class PlaceholderChoice(models.TextChoices):
    CNONE  = '',  ''              # noqa: E221


class EnabledTrueFalseNoneChoice(models.TextChoices):
    CNONE  = '',  ''              # noqa: E221
    CTRUE  = 'true',  _('True')   # noqa: E221
    CFALSE = 'false', _('False')  # noqa: E221


class EnabledTrueFalseChoice(models.TextChoices):
    CFALSE = 'false', _('False')  # noqa: E221
    CTRUE  = 'true',  _('True')   # noqa: E221


class PrimaryTrueFalseChoice(models.IntegerChoices):
    CTRUE  = 1, _('True')   # noqa: E221
    CFALSE = 0, _('False')  # noqa: E221


class EnabledDisabledChoice(models.TextChoices):
    CENABLED  = 'true',  _('Enabled')   # noqa: E221
    CDISABLED = 'false', _('Disabled')  # noqa: E221


class ConfirmChoice(models.TextChoices):
    CNONE    = '',  _('')         # noqa: E221
    CCONFIRM = '1', _('Confirm')  # noqa: E221


class SettingTypeChoice(models.TextChoices):
    CTEXT    = 'text',    _('text')     # noqa: E221
    CNUMERIC = 'numeric', _('numeric')  # noqa: E221
    CARRAY   = 'array',   _('array')    # noqa: E221
    CBOOLEAN = 'boolean', _('boolean')  # noqa: E221
    CCODE    = 'code',    _('code')     # noqa: E221
    CUUID    = 'uuid',    _('uuid')     # noqa: E221
    CNAME    = 'name',    _('name')     # noqa: E221
    CVAR     = 'var',     _('var')      # noqa: E221
    CDIR     = 'dir',     _('dir')      # noqa: E221


class StatusDefaultChoice(models.TextChoices):
    CNONE         = '',                       _('Not Set')                # noqa: E221
    CAVAILABLE    = 'Available',              _('Available')              # noqa: E221
    CAVAILABLEOD  = 'Available (On Demand)',  _('Available (On Demand)')  # noqa: E221
    CLOGGEDOUT    = 'Logged Out',             _('Logged Out')             # noqa: E221
    CONBREAK      = 'On Break',               _('On Break')               # noqa: E221
    CDONOTDISTURB = 'Do Not Disturb',         _('Do Not Disturb')         # noqa: E221


class TargetCategoryChoice(models.TextChoices):
    CINTERNAL = 'internal',  _('Internal')  # noqa: E221
    CEXTERNAL = 'external',  _('External')  # noqa: E221
    CEMAIL    = 'e-mail',    _('E-Mail')    # noqa: E221


class CallDirectionChoice(models.TextChoices):
    CINBOUND  = 'inbound',  _('Inbound')   # noqa: E221
    COUTBOUND = 'outbound', _('Outbound')  # noqa: E221
