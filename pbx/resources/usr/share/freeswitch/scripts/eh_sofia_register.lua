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
    local api = freeswitch.API()

-- get the POST vars ready from event.
    post_vars = 'session_id=' .. event:getHeader('Core-UUID')
    post_vars = post_vars .. '&status=' .. url_escape(event:getHeader('status'))
    post_vars = post_vars .. '&network-ip=' .. url_escape(event:getHeader('network-ip'))

-- post the data to webserver
    post_response = api:execute('curl', httapi_url .. '/httapihandler/register/ timeout 2 post ' .. post_vars)
