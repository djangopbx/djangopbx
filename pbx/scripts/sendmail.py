#!/usr/bin/python3
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

import sys
import smtplib
from email.parser import Parser
from email.policy import default
from email.utils import formatdate
from resources.db.pgdb import PgDb

debug = False

dbh = PgDb('djangopbx')
if not dbh.connect():
    sys.exit('Database connection/login error')
mail_settings = {}
with dbh.cursor() as c:
    c.execute('select subcategory, value from pbx_default_settings where enabled = %s and category = %s', ('true', 'email'))
    while True:
        record = c.fetchone()
        if not record:
            break
        if debug:
            print(record)
        mail_settings[record[0]] = record[1]
if debug:
    print(mail_settings)
mail_msg = sys.stdin.read()
msg = Parser(policy=default).parsestr(mail_msg)
if debug:
    print(msg)
if not msg.get('Date'):
    msg['Date'] = formatdate(localtime=True)
if msg.get('From'):
    del msg['From']
    msg['From'] = mail_settings['smtp_from']
msg['X-DjangoPBX-sendmail'] = 'sendmail.py'
with smtplib.SMTP(mail_settings['smtp_host'], int(mail_settings['smtp_port'])) as server:
    try:
        if not server.starttls()[0] == 220:  # Secure the connection
            print('Warning! connection may not be secure.')
        server.login(mail_settings['smtp_user_name'], mail_settings['smtp_password'])
        server.send_message(msg)
        server.quit()
    except smtplib.SMTPResponseException as e:
        print('Error! code- %s Text- %s' % (e.smtp_code, e.smtp_error))
        sys.exit(1)
