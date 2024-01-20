#
#    DjangoPBX
#
#    MIT License
#
#    Copyright (c) 2016 - 2024 Adrian Fretwell <adrian@djangopbx.com>
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

class DeviceCfgEvent:
    device_lookup = {
                'aastra': {'reboot': 'check-sync;reboot=true', 'check_sync': 'check-sync;reboot=true'},
                'cisco': {'reboot': 'check-sync', 'check_sync': 'check-sync'},
                'cisco-spa': {'reboot': 'reboot=true', 'check_sync': 'reboot=true'},
                'diguim': {'reboot': 'check-sync', 'check_sync': 'check-sync'},
                'fanvil': {'reboot': 'check-sync;reboot=true', 'check_sync': 'resync'},
                'grandstream': {'reboot': 'check-sync;reboot=true', 'check_sync': 'resync'},
                'htek': {'reboot': 'check-sync;reboot=true', 'check_sync': 'resync'},
                'sangoma': {'reboot': 'check-sync;reboot=true', 'check_sync': 'resync'},
                'linksys': {'reboot': 'reboot=true', 'check_sync': 'reboot=true'},
                'panasonic': {'reboot': 'check-sync;reboot=true', 'check_sync': 'check-sync;reboot=true'},
                'polycom': {'reboot': 'check-sync', 'check_sync': 'check-sync'},
                'snom': {'reboot': 'check-sync;reboot=true', 'check_sync': 'check-sync;reboot=false'},
                'yealink': {'reboot': 'check-sync;reboot=true', 'check_sync': 'check-sync;reboot=false'}
                }

    def buildevent(self, user, realm, profile, action, vendor):
        event = []
        event.append('sendevent NOTIFY')
        event.append('profile: %s' % profile)
        event.append('event-string: %s' % self.device_lookup[vendor][action])
        event.append('user: %s' % user)
        event.append('host: %s' % realm)
        event.append('content-type: application/simple-message-summary')
        return '\n'.join(event)

    def buildfeatureevent(self, user, realm, profile, feature_event, **kwargs):
        event = []
        event.append('sendevent SWITCH_EVENT_PHONE_FEATURE')
        event.append('profile: %s' % profile)
        event.append('user: %s' % user)
        event.append('host: %s' % realm)
        #event.append('device: ')
        event.append('Feature-Event: %s' % feature_event)
        for key, value in kwargs.items():
            event.append('%s: %s' % (key, value))
        return '\n'.join(event)
