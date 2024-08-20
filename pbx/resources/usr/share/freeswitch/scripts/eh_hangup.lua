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

-- take action based on originate_disposition
    originate_disposition = env:getHeader("originate_disposition");

    if (originate_disposition ~= nil) then
        if (originate_disposition ~= "ORIGINATOR_CANCEL") then
            return
        end
    end

-- get the POST vars ready from env.
    post_vars = 'session_id=' .. env:getHeader('uuid');
    post_vars = post_vars .. post_add('domain_uuid', true);
    post_vars = post_vars .. post_add('domain_name', true);
    post_vars = post_vars .. post_add('sip_to_user', true);
    post_vars = post_vars .. post_add('dialed_user', true);
    post_vars = post_vars .. post_add('missed_call_app', true);
    post_vars = post_vars .. post_add('missed_call_data', true);
    post_vars = post_vars .. post_add('default_language', true);
    post_vars = post_vars .. post_add('default_dialect', true);
    post_vars = post_vars .. post_add('originate_disposition', true);

-- get the Caller ID
    caller_id_name = env:getHeader("caller_id_name");
    caller_id_number = env:getHeader("caller_id_number");
    if (caller_id_name == nil) then
        caller_id_name = env:getHeader("Caller-Caller-ID-Name");
    end
    if (caller_id_number == nil) then
        caller_id_number = env:getHeader("Caller-Caller-ID-Number");
    end

    if (caller_id_name ~= nil) then
        post_vars = post_vars .. '&variable_caller_id_name=' .. caller_id_name;
    end
    if (caller_id_number ~= nil) then
        post_vars = post_vars .. '&variable_caller_id_number=' .. caller_id_number;
    end

-- post the data to webserver
    post_response = api:execute('curl', httapi_url .. '/httapihandler/hangup/ timeout 2 post ' .. post_vars);
