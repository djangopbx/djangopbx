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


class EnabledTrueFalseNoneChoice(models.TextChoices):
    CNONE  = '',  ''
    CTRUE  = 'true',  _('True')
    CFALSE = 'false', _('False')


class EnabledTrueFalseChoice(models.TextChoices):
    CFALSE = 'false', _('False')
    CTRUE  = 'true',  _('True')


class PrimaryTrueFalseChoice(models.IntegerChoices):
    CTRUE  = 1, _('True')
    CFALSE = 0, _('False')


class EnabledDisabledChoice(models.TextChoices):
    CENABLED  = 'true',  _('Enabled')
    CDISABLED = 'false', _('Disabled')


class ConfirmChoice(models.TextChoices):
    CNONE    = '',  _('')
    CCONFIRM = '1', _('Confirm')


class SettingTypeChoice(models.TextChoices):
    CTEXT    = 'text'   , _('text')
    CNUMERIC = 'numeric', _('numeric')
    CARRAY   = 'array'  , _('array')
    CBOOLEAN = 'boolean', _('boolean')
    CCODE    = 'code'   , _('code')
    CUUID    = 'uuid'   , _('uuid')
    CNAME    = 'name'   , _('name')
    CVAR     = 'var'    , _('var')
    CDIR     = 'dir'    , _('dir')


class StatusDefaultChoice(models.TextChoices):
    CNONE         = ''                      , _('Not Set')
    CAVAILABLE    = 'Available'             , _('Available')
    CAVAILABLEOD  = 'Available (On Demand)' , _('Available (On Demand)')
    CLOGGEDOUT    = 'Logged Out'            , _('Logged Out')
    CONBREAK      = 'On Break'              , _('On Break')
    CDONOTDISTURB = 'Do Not Disturb'        , _('Do Not Disturb')


class TargetCategoryChoice(models.TextChoices):
    CINTERNAL = 'internal' , _('Internal')
    CEXTERNAL = 'external' , _('External')
    CEMAIL    = 'e-mail'   , _('E-Mail')


class CallDirectionChoice(models.TextChoices):
    CINBOUND  = 'inbound' , _('Inbound')
    COUTBOUND = 'outbound', _('Outbound')

