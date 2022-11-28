import psycopg2
from psycopg2 import Error
from freeswitch import *
from resources.db import pbxdb

class Settings:

    def __init__(self):
        self.db_conn = pbxdb.connect('djangopbx')


    def __del__(self):
        if (self.db_conn):
            self.db_conn.close()


    def EmailTemplates(self, domain_id, lang, cat, subcat):
        with self.db_conn.cursor() as c:
            c.execute('select subject, body, type from pbx_email_templates where (domain_id_id = %s or domain_id_id is null) and enabled = %s and language = %s and category = %s and subcategory = %s', (domain_id, 'true', lang, cat, subcat))
            if c.rowcount == 0:
                return False
            return c.fetchone()


    def DefaultSettings(self, cat, subcat = None, settingtype = 'text', defaultsetting = '', usedefault = False):
        with self.db_conn.cursor() as c:
            if subcat:
                c.execute('select value from pbx_default_settings where enabled = %s and category = %s and subcategory = %s and value_type = %s order by sequence', ('true', cat, subcat, settingtype))
            else:
                c.execute('select subcategory, value from pbx_default_settings where enabled = %s and category = %s order by sequence', ('true', cat))
            if c.rowcount == 0:
                if usedefault:
                    return list((defaultsetting,))
                else:
                    return False
            records = c.fetchall()
        return records


    def DomainSettings(self, domain_id, cat, subcat = None, settingtype = 'text', defaultsetting = '', usedefault = False):
        with self.db_conn.cursor() as c:
            if subcat:
                c.execute('select value from pbx_domain_settings where domain_id_id = %s and enabled = %s and category = %s and subcategory = %s and value_type = %s order by sequence', (domain_id, 'true', cat, subcat, settingtype))
            else:
                c.execute('select subcategory, value from pbx_domain_settings where domain_id_id = %s and enabled = %s and category = %s order by sequence', (domain_id, 'true', cat))
            if c.rowcount == 0:
                if usedefault:
                    return list((defaultsetting,))
                else:
                    return False
            records = c.fetchall()
        return records


    def UserSettings(self, user_id, cat, subcat = None, settingtype = 'text', defaultsetting = '', usedefault = False):
        with self.db_conn.cursor() as c:
            if subcat:
                # Note: user_id_id is a bigint not a uuid
                c.execute('select value from pbx_user_settings where user_id_id = %s and enabled = %s and category = %s and subcategory = %s and value_type = %s order by sequence', (user_id, 'true', cat, subcat, settingtype))
            else:
                c.execute('select subcategory, value from pbx_user_settings where user_id_id = %s and enabled = %s and category = %s order by sequence', (user_id, 'true', cat))
            if c.rowcount == 0:
                if usedefault:
                    return list((defaultsetting,))
                else:
                    return False
            records = c.fetchall()
        return records


    def Settings(self, cat, subcat = None, settingtype = 'text', level = 1, useruuidstr = None, domainuuidstr = None,  defaultsetting = '', usedefault = False):
        if level > 2:
            settingList = self.user_settings(useruuidstr, cat, subcat, settingtype, defaultsetting, False)
            if settingList:
                return settingList
        if level > 1:
            settingList = self.domain_settings(domainuuidstr, cat, subcat, settingtype, defaultsetting, False)
            if settingList:
                return settingList
        settingList = self.default_settings(cat, subcat, settingtype, defaultsetting, usedefault)
        return settingList

