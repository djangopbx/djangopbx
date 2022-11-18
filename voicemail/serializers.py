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

from  rest_framework  import serializers
from .models import (
    Voicemail, VoicemailGreeting,
)


class VoicemailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voicemail
        fields =['url', 'id', 'domain_id', 'vm_id', 'password', 'greeting_id', 'alternate_greeting_id', 'mail_to', 'sms_to', 'cc', 'attach_file', 'local_after_email', 'enabled', 'description',
                'created', 'updated', 'synchronised', 'updated_by']


class VoicemailGreetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoicemailGreeting
        fields =['url', 'id', 'voicemail_id', 'filename', 'name', 'description',
                'created', 'updated', 'synchronised', 'updated_by']

