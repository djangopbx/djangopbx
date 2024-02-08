#
#    DjangoPBX
#
#    MIT License
#
#    Copyright (c) 2016 - 2024 James Creese <jcre@djangopbx.com>
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
#    James Creese <jcre@djangopbx.com>
#    Adrian Fretwell <adrian@djangopbx.com>
#

from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from rest_framework.authtoken.models import Token

UserModel = get_user_model()


class Command(BaseCommand):
    help = 'Create DRF Token for a given user'

    def create_user_token(self, username, reset_token):
        if username == "initial-install":
            user = UserModel._default_manager.all().first()
        else:
            user = UserModel._default_manager.get_by_natural_key(username)

        if reset_token:
            Token.objects.filter(user=user).delete()

        token = Token.objects.get_or_create(user=user)
        self.stdout.write(_('Generated token {} for user {}'.format(token[0], user)))
        return True

    def add_arguments(self, parser):
        parser.add_argument('--user',
            type=str,
            dest='username',
            default=False,
            help=_('User needing API key (--user adrian@djangopbx.com)'),
        )

        parser.add_argument(
            '--reset',
            action='store_true',
            dest='reset_token',
            default=False,
            help=_('Reset existing User token and create a new one'),
        )

    def handle(self, *args, **options):
        username = options['username']
        reset_token = options['reset_token']

        try:
            token = self.create_user_token(username, reset_token)
        except UserModel.DoesNotExist:
            raise CommandError(
                _('Cannot create the Token: user {} does not exist'.format(
                    username))
            )

