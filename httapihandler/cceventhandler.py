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

from .httapihandler import HttApiHandler
from callcentres.models import  CallCentreAgents, CallCentreAgentStatusLog
from django.shortcuts import get_object_or_404


class CcEventHandler(HttApiHandler):

    handler_name = 'ccevent'

    def get_data(self):
        action = self.qdict.get('CC-Action', 'None')
        if action == 'agent-status-change':
            agent = self.qdict.get('CC-Agent')
            if agent:
                q = get_object_or_404(CallCentreAgents, pk=agent)
                status = self.qdict.get('CC-Agent-Status', 'Unknown')
                CallCentreAgentStatusLog.objects.create(
                        agent_id=q,
                        status=status,
                        updated_by='system'
                    )
        return self.return_data('Ok\n')
