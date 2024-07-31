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

from django.core.files.uploadhandler import StopFutureHandlers

def putuploadhandler(request):
    if not request.method == 'PUT':
        return False
    content_type   = str(request.headers.get('CONTENT_TYPE', ''))
    content_length = int(request.headers.get('CONTENT_LENGTH', 0))
    file_name = request.path.split('/')[-1:][0]
    field_name = file_name
    content_type_extra = None

    if content_type == '':
        return HttpResponse(status=400)
    if content_length == 0:
        return HttpResponse(status=400)

    content_type = content_type.split(';')[0].strip()
    try:
        charset = content_type.split(';')[1].strip()
    except IndexError:
        charset = ''

    upload_handlers = request.upload_handlers

    for handler in upload_handlers:
        result = handler.handle_raw_input(
            None,
            None,
            content_length,
            boundary=None,
            encoding=None,
        )
    for handler in upload_handlers:
        try:
            handler.new_file(
                field_name,
                file_name,
                content_type,
                content_length,
                charset,
                content_type_extra,
            )
        except StopFutureHandlers:
            break

    counter = 0
    chunk_size = handler.chunk_size
    while True:
        chunk = request.read(chunk_size)
        if chunk:
            handler.receive_data_chunk(chunk, counter)
            counter += len(chunk)
        else:
            # Don't continue if the chunk received by
            # the handler is None.
            break

    file_obj = handler.file_complete(counter)
    if file_obj:
        # If it returns a file object, then set the files dict.
        request.FILES.appendlist(file_name, file_obj)
        return True
    return False
