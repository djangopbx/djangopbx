--
--    DjangoPBX
--
--    MIT License
--
--    Copyright (c) 2016 - 2022 Adrian Fretwell <adrian@djangopbx.com>
--
--    Permission is hereby granted, free of charge, to any person obtaining a copy
--    of this software and associated documentation files (the "Software"), to deal
--    in the Software without restriction, including without limitation the rights
--    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
--    copies of the Software, and to permit persons to whom the Software is
--    furnished to do so, subject to the following conditions:
--
--    The above copyright notice and this permission notice shall be included in all
--    copies or substantial portions of the Software.
--
--    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
--    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
--    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
--    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
--    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
--    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
--    SOFTWARE.
--
--    Contributor(s):
--    Adrian Fretwell <adrian@djangopbx.com>
--

-- include config.lua
    require "resources.pbx.config"
    require "resources.functions.http_utils"

-- prepare the API object
    local api = freeswitch.API();

-- filter events
    cc_action = event:getHeader('CC-Action');

    if cc_action == 'agent-status-change' then
        cc_agent = event:getHeader('CC-Agent');
        agent_status = event:getHeader('CC-Agent-Status');
        post_vars = 'session_id=' .. event:getHeader('Core-UUID');
        post_vars = post_vars .. '&CC-Action=agent-status-change';
        post_vars = post_vars .. '&CC-Agent=' .. cc_agent;
        post_vars = post_vars .. '&CC-Agent-Status=' .. url_escape(agent_status);
        api:execute('memcache', 'set pbx:1:fs:cc:a:' .. cc_agent .. ':agent-status ' .. url_escape(agent_status) .. ' 0');
        api:execute('memcache', 'set pbx:1:fs:cc:a:' .. cc_agent .. ':agent-status-time ' .. event:getHeader('Event-Date-Timestamp') .. ' 0');
        -- post the data to webserver for status change log
        post_response = api:execute('curl', httapi_url .. '/httapihandler/ccevent/ timeout 1 post ' .. post_vars);

    elseif cc_action == 'agent-state-change' then
        api:execute('memcache', 'set pbx:1:fs:cc:a:' .. event:getHeader('CC-Agent') .. ':agent-state-change ' .. url_escape(event:getHeader('CC-Agent-State')) .. ' 0');
    --elseif cc_action == 'agent-offering' then
    --    api:execute('memcache', 'set pbx:1:fs:cc:q:' .. event:getHeader('CC-Queue') .. ':agent-offering ' .. event:getHeader('CC-Agent') .. ' 0');
    elseif cc_action == 'bridge-agent-start' then
        api:execute('memcache', 'increment pbx:1:fs:cc:q:' .. event:getHeader('CC-Queue') .. ':ctrs:answered' .. ' 1 0');
    --elseif cc_action == 'bridge-agent-end' then
    --    nop = true;
    --elseif cc_action == 'bridge-agent-fail' then
    --    nop = true;
    --elseif cc_action == 'member-queue-start' then
    --    nop = true;
    elseif cc_action == 'member-queue-end' then
        cc_queue = event:getHeader('CC-Queue');
        cc_cancel_reason = event:getHeader('CC-Cancel-Reason');
        api:execute('memcache', 'increment pbx:1:fs:cc:q:' .. cc_queue .. ':ctrs:' .. event:getHeader('CC-Cause') .. ' 1 0');
        if not (cc_cancel_reason == nil or cc_cancel_reason == '') then
            api:execute('memcache', 'increment pbx:1:fs:cc:q:' .. cc_queue .. ':ctrs:' .. event:getHeader('CC-Cancel-Reason') .. ' 1 0');
        end
    elseif cc_action == 'members-count' then
        api:execute('memcache', 'set pbx:1:fs:cc:q:' .. event:getHeader('CC-Queue') .. ':members-count ' .. event:getHeader('CC-Count') .. ' 0');
    end
