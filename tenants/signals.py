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

from .models import Profile, Domain
from django.contrib.auth.models import Group

def create_or_edit_user_profile(sender, instance, created, **kwargs):
    if created:
        p = Profile.objects.create(user=instance)
        try:
            user_group = Group.objects.get(name='user')
        except Group.DoesNotExist:
            user_group = False
        if user_group:
            user_group.user_set.add(instance)
        if '@' in instance.username:
            d_name = instance.username.split('@')[1]
            try:
                d = Domain.objects.get(name=d_name)
            except (Domain.DoesNotExist):
                d = None
            if d:
                p.domain_id = d

    try:
        instance.profile.username = instance.username
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)
        instance.profile.username = instance.username

    instance.profile.email = instance.email
    if instance.is_active:
        instance.profile.user_enabled = 'true'
    else:
        instance.profile.user_enabled = 'false'

    instance.profile.save()
