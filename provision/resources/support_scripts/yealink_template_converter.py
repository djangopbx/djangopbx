#
#    DjangoPBX
#
#    MIT License
#
#    Copyright (c) 2016 - 2023 Adrian Fretwell <adrian@djangopbx.com>
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
#   This is a simple script to convert smarty php Yealink provision templates to the Django
#   template format.  It works with an In and Out directory structure.
#   Copy this file to a temporary directory along with mac.cfg, create two sub directories
#   templates_in and templates_out.
#   Place Yealink provision template directories into the templates_in directory and run
#   python3 yealink_template_converter.py
#

import os
import re
import shutil

dir_in = 'templates_in'
dir_out = 'templates_out'

t_d = {'if': 'if', 'else': 'else', 'elseif': 'elif', 'foreach': 'for', '/if': 'endif', '/foreach': 'endfor', 'var': 'var', '\"\"': 'err'}

var_name_conv = {}
var_name_conv['row in keys[\"expansion\"]'] = 'row in expansion_1_keys'
var_name_conv['row in keys[\"expansion-1\"]'] = 'row in expansion_1_keys'
var_name_conv['row in keys[\"expansion-2\"]'] = 'row in expansion_2_keys'
var_name_conv['row in keys[\"expansion-3\"]'] = 'row in expansion_3_keys'
var_name_conv['row in keys[\"expansion-4\"]'] = 'row in expansion_4_keys'
var_name_conv['row in keys[\"expansion-5\"]'] = 'row in expansion_5_keys'
var_name_conv['row in keys[\"expansion-6\"]'] = 'row in expansion_6_keys'
var_name_conv['row.device_key_id'] = 'row.key_id'
var_name_conv['row.device_key_type'] = 'row.key_type'
var_name_conv['row.device_key_line'] = 'row.line'
var_name_conv['row.device_key_value'] = 'row.value'
var_name_conv['row.device_key_extension'] = 'row.extension'
var_name_conv['row.device_key_label'] = 'row.label'
var_name_conv['row in keys[\"programmable\"]'] = 'row in programmable_keys'


def token_replace(l, l1):
    for i in range(len(l1)):
        l = l.replace(l1[i], 'dpbx-%s' % str(i))
    return l

def tag_replace(l):
    for i in range(len(l)):
        if l[i][0].startswith('$'):
            l[i] = ('var', l[i][0])
        if l[i][0] == 'foreach':
            l[i] = (l[i][0], re.sub(r'\$(.+)\s+as\s+\$(.+)', r'\2 in \1', l[i][1]))
        t_var = l[i][1].replace('$', '').replace('isset', '').replace('(', '').replace(')', '')
        if t_var in var_name_conv:
            t_var = var_name_conv[t_var]
        if t_var.startswith('yealink_'):
            t_var = 'prov_defs.%s' % t_var
        if t_var.startswith('http_'):
            t_var = 'prov_defs.%s' % t_var
        if t_var.startswith('domain_'):
            t_var = 'prov_defs.%s' % t_var
        if t_var.startswith('ntp_'):
            t_var = 'prov_defs.%s' % t_var
        if t_var.startswith('dns_'):
            t_var = 'prov_defs.%s' % t_var
        if t_var.startswith('stun_'):
            t_var = 'prov_defs.%s' % t_var
        l[i] = (t_d[l[i][0]], t_var)

def line_reassemble(l,l1):

    for i in range(len(l1)):
        if l1[i][0] == 'err':
            l = l.replace('dpbx-%s' % str(i), '')
            continue
        if l1[i][0] == 'var':
            l = l.replace('dpbx-%s' % str(i), '{{ %s }}' % l1[i][1])
        else:
            if l1[i][1]:
                l = l.replace('dpbx-%s' % str(i), '{%% %s %s %%}' % (l1[i][0], l1[i][1]))
            else:
                l = l.replace('dpbx-%s' % str(i), '{%% %s %%}' % l1[i][0])
    l = l.replace('/app/provision/?file=', '/provision/device_config/')
    l = l.replace('/provision/device_config/directory.xml&contacts=users', '/provision/device_config/contacts/users/directory.xml')
    l = l.replace('/provision/device_config/directory.xml&contacts=groups', '/provision/device_config/contacts/groups/directory.xml')
    l = l.replace('/provision/device_config/directory.xml&contacts=extensions', '/provision/device_config/contacts/extensions/directory.xml')
    l = l.replace('{{ mac }}', '{{ prov_defs.mac }}')
    l = l.replace('&&', 'and').replace('||', 'or')
    l = l.replace('smarty.get.contacts == \"users\" and ', '')
    l = l.replace('smarty.get.contacts == \"groups\" and ', '')
    l = l.replace('smarty.get.contacts == \"extensions\" and ', '')
    l = l.replace('smarty.get.contacts == \"all\"', 'row.category == \"all\"')
    return l

def file_action(op, f):
    if f.name == '{$mac}.cfg':
        shutil.copy('mac.cfg', op)
        return
    fi = open(f)
    fo = open('%s/%s' % (op, f.name), 'w')
    for l in fi:
        tag_tuples = re.findall(r'{([^\s}]*)\s*([^}]*)}', l)
        tags = re.findall(r'{[^\s}]*[^}]*}', l)
        l = token_replace(l, tags)
        tag_replace(tag_tuples)
        l = line_reassemble(l, tag_tuples)
        fo.write(l)
    fo.close()
    fi.close()
    return

if __name__ == "__main__":

    for f1 in os.scandir(dir_in):
        if f1.is_dir():
            d1 = os.path.relpath(f1.path, start=dir_in)
            out_path = '%s/%s' % (dir_out, d1)
            os.makedirs(out_path, exist_ok=True)
            for f2 in os.scandir(f1.path):
                if f2.is_file():
                    file_action(out_path, f2)



