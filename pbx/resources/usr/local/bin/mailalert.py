#!/usr/bin/python3

import smtplib
import sys

from email.message import EmailMessage
from email.utils import formatdate

if len(sys.argv) < 3:
    print("You must provide title and text: Eg. " + sys.argv[0] + " \"Some warning\" \"Some text\"")
    sys.exit(1)

authmailuser = 'me@mydomain.com'
password = 'XXXXXXXX'
recipients = ['adrian@djangopbx.com', 'postmaster@djangopbx.com']
sender = 'me@mydomain.com'

msg = EmailMessage()
msg['Subject'] = 'DjangoPBX Server Alert'
msg['From'] = 'system@djangopbx.com'
msg['To'] = ', '.join(recipients)
msg['Date'] = formatdate(localtime=True)
msg.set_content("""\
Sorry!

This mail is intended for HTML capable mail clients only.
""")

msg.add_alternative("""\
<html>
  <head>
 <style type="text/css">
 <!--

BODY
{{
    color: #000000;
    background-color: #FFFFFF;
    font-family: verdana, arial, sans-serif;
    font-size: 12px;
    line-height: 14px;
}}

.text {{font-family:verdana,arial,sans-serif;font-size:12px;color:#000000}}
.textsp {{font-family:verdana,arial,sans-serif;font-size:10px;color:#BBBBBB}}
.textsm {{font-family:verdana,arial,sans-serif;font-size:8px;color:#000000}}
.texttitle {{font-family:verdana,arial,sans-serif;font-weight:bold;font-size:20px;color:#4F6313}}
.textsubtitle1 {{font-family:verdana,arial,sans-serif;font-size:20px;color:#4F6313}}
.textsubtitle2 {{font-family:verdana,arial,sans-serif;font-size:18px;color:#4F6313}}
.th {{font-family:verdana,arial,sans-serif;font-size:10pt;font-weight: bold; background-color:#D3DCE3;}}
.th1 {{
  font-family:verdana,arial,sans-serif;
  font-size:10pt;color:#838C93;
  font-weight: bold;
  background-color:#D3DCE3;}}
.td {{font-family:verdana,arial,sans-serif;font-size:10pt;white-space:nowrap;}}
.hr {{background-color:#7A8F39}}

 -->
 </style>
</head>
<body>
<p><b>DjangoPBX Server Alert. {alert_timestamp}</b></p>
<p><br><b>{alert_heading}</b><br><pre>{alert_text}</pre><br><br></p>
<p class=textsp>My Company<br>
My Address<br>
Tel: My Telephone.<br><br>

This electronic message contains information from My Company which may be privileged or confidential.
  The information is intended to be for the use of the individual(s) or entity named above.
  If you are not the intended recipient be aware that any disclosure, copying, distribution or use of
 the contents of this information is prohibited.
  If you have received this electronic message in error, please notify us by telephone or email to
 me@mydomain.com immediately.<br></p></body>
</html>
""".format(
    alert_timestamp=formatdate(localtime=True),
    alert_heading=sys.argv[1],
    alert_text=sys.argv[2]
    ), subtype='html')


with smtplib.SMTP("my-mail-server.com", 587) as server:

    try:
        if not server.starttls()[0] == 220:  # Secure the connection
            print("Warning! connection may not be secure.")
        out = server.login(authmailuser, password)
        out = server.send_message(msg)
        out = server.quit()
    except smtplib.SMTPResponseException as e:
        print("Error! code:" + str(e.smtp_code) + " Text:" + e.smtp_error)
