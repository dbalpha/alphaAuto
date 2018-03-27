#!/usr/bin/env python3
# -*-coding: utf-8 -*-

from Remote_linux import Linux
from oracle_handle import oracle_handle as oracle
import functools
import json

#拒绝向生产库自动导入
deny_host=('192.168.10.240','192.168.10.241')
def audit(orades):
    for x in deny_host:
        if orades.host==x and orades.service_name.lower()=='dz':
            raise ValueError(('%s insufficient privileges' % json.dumps(orades,default=lambda obj: obj.__dict__)))

def drop_user(orades):
    if not isinstance(orades,oracle):
        raise ValueError(('%s in not an oracle' % orades))
    audit(orades)
    host = Linux(orades.host, 'oracle', 'alpha',timeout=30)
    host.connect()
    host.send('sqlplus sys/%s@%s:%s/%s as sysdba'%(orades.passwd, orades.localhost, orades.port, orades.service_name),r'SQL> ')
    host.send('alter user %s account lock;' % orades.schemas,r'SQL> ')
    host.send('startup force;',r'SQL> ')
    host.send('drop user dianshang315 cascade;',r'SQL> ')
    host.close()


def alter_user(orades):
    if not isinstance(orades,oracle):
        raise ValueError(('%s in not an oracle' % orades))
    audit(orades)
    host = Linux(orades.host, 'oracle', 'alpha',timeout=30)
    host.connect()
    host.send('sqlplus %s/%s@%s:%s/%s' % (orades.con_name, orades.passwd, orades.localhost, orades.port, orades.service_name), r'SQL> ')
    host.send('alter user %s identified by dianshang315 account unlock;' % orades.schemas, r'SQL> ')
    host.close()

    # 远程数据库导出
def oracle_trancs(orasource,orades):

    if not isinstance(orasource,oracle):
        raise ValueError(('%s in not an oracle' % json.dumps(orasource,default=lambda obj: obj.__dict__)))
    if not isinstance(orades,oracle):
        raise ValueError(('%s in not an oracle' % json.dumps(orades,default=lambda obj: obj.__dict__)))
    audit(orades)
    hostsource = Linux(orasource.host, orasource.osname, orasource.ospasswd,timeout=60)
    hostdes = Linux(orades.host, orades.osname, orades.ospasswd,timeout=60)
    #拼接导出数据库命令
    expdpcmd,dmpname=orasource.get_expdpcmd()
    #拼接导入数据库命令

    impdpcmd=orades.get_impdpcmd(dmpname)

    #print(expdpcmd)
    hostsource.connect()
    p1=hostsource.send(expdpcmd)
    if hostsource.ip==hostdes.ip:
        impdpcmd=orades.get_impdpcmd(dmpname)
        #print(impdpcmd)
        p2=hostsource.send(impdpcmd)
        hostsource.send('rm -f '+orasource.directory_dir+dmpname)
        hostsource.close()
        return

    tardmpname=hostsource.compress(dmpname,orasource.directory_dir)
    #下载数据压缩文件
    hostsource.sftp_get(orasource.directory_dir+tardmpname,'/tmp/'+tardmpname)
    hostsource.send('rm -f '+orasource.directory_dir+tardmpname)
    #传送至远程数据库
    hostdes.connect()
    hostdes.sftp_put('/tmp/'+tardmpname,orades.directory_dir+tardmpname)
    hostdes.uncompress(tardmpname,orades.directory_dir)
    #拼接导入数据库命令
    #print(impdpcmd)
    p2=hostdes.send(impdpcmd)
    #删除数据泵文件和压缩文件
    hostsource.send('rm -f '+orasource.directory_dir+dmpname)
    hostsource.send('rm -f '+orasource.directory_dir+tardmpname)
    hostdes.send('rm -f '+orades.directory_dir+tardmpname)
    hostdes.send('rm -f '+orades.directory_dir+dmpname)
    hostsource.close()
    hostdes.close()