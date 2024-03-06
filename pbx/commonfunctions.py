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
#  These are functions and classes used by more than one application
#

from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from tenants.models import Domain
import subprocess
import os
import re


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    try:
        with open(os.path.join(package, '__init__.py')) as i:
            init_py = i.read()
        v = re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)
    except (IOError, TypeError, AttributeError, KeyError):
        v = '0.0.0'
    return v


def shcommand(cmd, env=None):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    stdout, stderr = proc.communicate()
    if stderr:
        return stdout.decode() + stderr.decode()
    return stdout.decode('utf-8', 'ignore')


def str2regex(dst, pre=''):
    # excape the +
    if dst[0] == '+':
        dst = '^\\+(%s)$' % dst[1:]
    # add prefix
    if len(pre) > 0:
        if len(pre) < 4:
            if '+' in dst:
                pre = '\\+?%s?' % pre
            else:
                pre = '(?:%s)?' % pre
    # conver N,X,Z sytax to regex
    dst = dst.replace('N', '[2-9]')
    dst = dst.replace('X', '[0-9]')
    dst = dst.replace('Z', '[1-9]')

    # check for ^ and $ at start and end of string respectively
    if not dst[0] == '^':
        dst = '^%s' % dst

    if not dst[-1] == '$':
        dst = '%s$' % dst

    # add the brackets
    if '(' not in dst:
        dst = dst.replace('^', '^%s(' % pre)
        dst = dst.replace('$', ')$')

    return dst


class DomainUtils():

    def domain_from_session(self, request):
        try:
            d = Domain.objects.get(name=request.session['domain_name'])
        except Domain.DoesNotExist:
            return None
        return d

    def domain_from_name(self, name):
        try:
            d = Domain.objects.get(name=name)
        except Domain.DoesNotExist:
            return None
        return d


class DomainFilter(admin.SimpleListFilter):
    title = _('Domain')
    parameter_name = 'workarea'

    def lookups(self, request, model_admin):
        doms = [(c.id, c.name) for c in Domain.objects.all()]
        return [('all', _('All')), (None, _('Selected Domain')), ('global', _('Global'))] + doms

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset.filter(domain_id__exact=request.session['domain_uuid'])
        if self.value() == 'global':
            return queryset.filter(domain_id__exact=None)
        if not ((self.value() is None) or (self.value() == 'all')):
            return queryset.filter(domain_id__exact=self.value())
