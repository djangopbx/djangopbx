import smtplib

from email.message import EmailMessage
from email.utils import formatdate
from resources.pbx.settings import Settings

class Message:

    cfg  = None
    info = list()
    ok = True

    def __init__(self):
        self.info.append('[SMTP Sender]')
        self.s = Settings()
        cfg = self.s.DefaultSettings('email', None, 'text')
        if cfg:
            self.cfg = dict(cfg)
        else:
            self.ok = False
            self.info.append('No Config')


    def GetTemplate(self, domain_id, lang, cat, subcat):
        return self.s.EmailTemplates(domain_id, lang, cat, subcat)


    def Send(self, rps, sub, msg, msg_type):
        if not self.ok:
            return (self.ok, ': '.join(self.info))
        try:
            m = EmailMessage()
            m['Subject'] = sub
            m['From'] = self.cfg['smtp_from']
            m['To'] = rps
            m['Date'] = formatdate(localtime=True)
        except:
            self.info.append('Error with message parameters')
            return (False, ': '.join(self.info))

        try:
            if msg_type == 'html':
                m.set_content('Sorry!\n\nThis mail is intended for HTML capable mail clients only.')
                m.add_alternative(msg, subtype='html')
            else:
                m.set_content(msg)
        except:
            self.info.append('Error with message body')
            return (False, ': '.join(self.info))

        with smtplib.SMTP(self.cfg['smtp_host'], int(self.cfg['smtp_port'])) as server:
            try:
                if not server.starttls()[0] == 220: # Secure the connection
                    self.info.append('Warning! connection may not be secure.')
                server.login(self.cfg['smtp_user_name'], self.cfg['smtp_password'])
                server.send_message(m)
                server.quit()
            except smtplib.SMTPResponseException as e:
                self.info.append('Error! code- %s Text- %s'  % (e.smtp_code, e.smtp_error))
                self.ok = False

        if self.ok:
            self.info.append('Email sent OK')
        return (self.ok, ': '.join(self.info))
