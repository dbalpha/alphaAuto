#!/usr/bin/env python3
# -*-coding: utf-8 -*-

from datetime import datetime

class oracle_handle(object):

    version='12.1.0.2.0'
    port = '1521'
    localhost = '127.0.0.1'
    __tables = None
    @property
    def tables(self):
        return self.__tables
    @tables.setter
    def tables(self,value):
        if isinstance(value,list):
            self.__tables=','.join([self.schemas+'.'+x for x in value])
        else:
            self.__tables = value

    def __init__(self,data):
        self.host = data['host']
        self.con_name = data['con_name']
        self.passwd = data['passwd']
        self.service_name = data['service_name']
        self.directory = data['directory']
        self.schemas = data['schemas']
        self.directory_dir = data['directory_dir']
        self.osname = data['osname']
        self.ospasswd = data['ospasswd']
        self.version = data['version']
#返回导出命令
    def get_expdpcmd(self,content='All'):
        now=datetime.now()
        prefix='auto'+self.service_name+now.strftime('%Y%m%d%H%M%S')
        dmpname=prefix+'.dmp'
        logname=prefix+'.log'
        if self.localhost:
            url='%s/%s@%s:%s/%s'%(self.con_name, self.passwd, self.localhost, self.port, self.service_name)
        else:
            url='%s/%s'%(self.con_name, self.passwd)
        if self.tables:
            rumcmd='expdp %s tables=%s dumpfile=%s logfile=%s CONTENT=%s directory=%s version=%s'%(url,self.tables,dmpname,logname,content,self.directory,self.version)
        else:
            rumcmd='expdp %s schemas=%s dumpfile=%s logfile=%s CONTENT=%s directory=%s version=%s'%(url,self.schemas,dmpname,logname,content,self.directory,self.version)

        return rumcmd,dmpname

    #返回导入命令
    def get_impdpcmd(self,dmpname,table_exists_action='REPLACE',content='All'):
        logname=dmpname.replace('.dmp','.log')
        if self.localhost:
            url='%s/%s@%s:%s/%s'%(self.con_name, self.passwd, self.localhost, self.port, self.service_name)
        else:
            url='%s/%s'%(self.con_name, self.passwd)
        if self.tables:
            rumcmd='impdp %s tables=%s dumpfile=%s logfile=%s CONTENT=%s directory=%s table_exists_action=%s version=%s'%(url,self.tables,dmpname,logname,content,self.directory,table_exists_action,self.version)
        else:
            rumcmd='impdp %s schemas=%s dumpfile=%s logfile=%s CONTENT=%s directory=%s table_exists_action=%s version=%s'%(url,self.schemas,dmpname,logname,content,self.directory,table_exists_action,self.version)

        return rumcmd


if __name__=='__main__':
    pass
