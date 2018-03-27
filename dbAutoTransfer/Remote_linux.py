#!/usr/bin/env python3
# -*-coding: utf-8 -*-

# 定义一个类，表示一台远端linux主机
import paramiko
import os
import re
import sys
from stat import S_ISDIR
from time import sleep
from paramiko.py3compat import u,b

class Linux(object):
    # 通过IP, 用户名，密码，超时时间初始化一个远程Linux主机
    def __init__(self, ip, username, password,port=22, timeout=10):
        self.ip = ip
        self.username = username
        self.password = password
        self.timeout = timeout
        self.port = port
        # transport和chanel
        self.t = ''
        self.chan = ''
        # 链接失败的重试次数
        self.try_times = 3

    # 调用该方法连接远程主机
    def connect(self):
        while True:
            # 连接过程中可能会抛出异常，比如网络不通、链接超时
            try:
                self.t = paramiko.Transport(sock=(self.ip, 22))
                self.t.connect(username=self.username, password=self.password)
                self.chan = self.t.open_session()
                self.chan.settimeout(self.timeout)
                # 获取终端
                self.chan.get_pty()
                # 激活终端，这样就可以登录到终端了
                self.chan.invoke_shell()
                # 如果没有抛出异常说明连接成功，直接返回
                print(u'连接%s成功' % self.ip)
                # 接收到的网络数据解码为str
                print(self.chan.recv(1024).decode('utf-8'))
                return
            # 这里不对可能的异常如socket.error, socket.timeout细化，直接一网打尽
            except Exception as e1:
                if self.try_times != 0:
                    print(u'连接%s失败，进行重试' %self.ip)
                    self.try_times -= 1
                else:
                    print(u'重试3次失败，结束程序')
                    exit(1)

    # 断开连接
    def close(self):
        self.chan.close()
        self.t.close()
        print()


    # 发送要执行的命令
    def send(self, cmd,termi_re=r'(~]# |~]\$ )'):
        cmd +='\r'
        # 通过命令执行提示符来判断命令是否执行完成
        p = re.compile(termi_re+'$')
        result = ''
        # 发送要执行的命令
        self.chan.send(cmd)
        # 回显很长的命令可能执行较久，通过循环分批次取回回显
        while True :
            while not self.chan.recv_ready():
                sleep(0.5)
            ret = self.chan.recv(10240)
            ret= u(ret.replace(b' \r',b''))
            result += ret
            if p.search(ret):
                print(ret.strip(), end='')
                return result
            else:
                print(ret.strip())

    # get单个文件
    def sftp_get(self, remotefile, localfile):
        t = paramiko.Transport(sock=(self.ip, self.port))
        t.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.get(remotefile, localfile)
        t.close()

    # put单个文件
    def sftp_put(self, localfile, remotefile):
        t = paramiko.Transport(sock=(self.ip, self.port))
        t.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.put(localfile, remotefile)
        t.close()
    # ------获取远端linux主机上指定目录及其子目录下的所有文件------
    def __get_all_files_in_remote_dir(self, sftp, remote_dir):
        # 保存所有文件的列表
        all_files = list()

        # 去掉路径字符串最后的字符'/'，如果有的话
        if remote_dir[-1] == '/':
            remote_dir = remote_dir[0:-1]

        # 获取当前指定目录下的所有目录及文件，包含属性值
        files = sftp.listdir_attr(remote_dir)
        for x in files:
            # remote_dir目录中每一个文件或目录的完整路径
            filename = remote_dir + '/' + x.filename
            # 如果是目录，则递归处理该目录，这里用到了stat库中的S_ISDIR方法，与linux中的宏的名字完全一致
            if S_ISDIR(x.st_mode):
                all_files.extend(self.__get_all_files_in_remote_dir(sftp, filename))
            else:
                all_files.append(filename)
        return all_files
    def sftp_get_dir(self, remote_dir, local_dir):
        t = paramiko.Transport(sock=(self.ip, self.port))
        t.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(t)

        # 获取远端linux主机上指定目录及其子目录下的所有文件
        all_files = self.__get_all_files_in_remote_dir(sftp, remote_dir)
        # 依次get每一个文件
        for x in all_files:
            filename = x.split('/')[-1]
            local_filename = os.path.join(local_dir, filename)
            print(u'Get文件%s传输中...' % filename)
            sftp.get(x, local_filename)
    # ------获取本地指定目录及其子目录下的所有文件------
    def __get_all_files_in_local_dir(self, local_dir):
        # 保存所有文件的列表
        all_files = list()

        # 获取当前指定目录下的所有目录及文件，包含属性值
        files = os.listdir(local_dir)
        for x in files:
            # local_dir目录中每一个文件或目录的完整路径
            filename = os.path.join(local_dir, x)
            # 如果是目录，则递归处理该目录
            if os.path.isdir(x):
                all_files.extend(self.__get_all_files_in_local_dir(filename))
            else:
                all_files.append(filename)
        return all_files

    def sftp_put_dir(self, local_dir, remote_dir):
        t = paramiko.Transport(sock=(self.ip, self.port))
        t.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(t)

        # 去掉路径字符穿最后的字符'/'，如果有的话
        if remote_dir[-1] == '/':
            remote_dir = remote_dir[0:-1]

        # 获取本地指定目录及其子目录下的所有文件
        all_files = self.__get_all_files_in_local_dir(local_dir)
        # 依次put每一个文件
        for x in all_files:
            filename = os.path.split(x)[-1]
            remote_filename = remote_dir + '/' + filename
            print(u'Put文件%s传输中...' % filename)
            sftp.put(x, remote_filename)
    #压缩
    def compress(self,filename,filedir=None):
        if filedir :
            tarcmd='tar -C '+filedir+' -zcvf '+filedir+'/'+filename+'.tar.gz'+' '+filename
        else :
            tarcmd='tar zcvf '+filename+'.tar.gz'+' '+filename
        self.send(tarcmd)
        return filename+'.tar.gz'
    #解压
    def uncompress(self,filename,filedir=None):
        if filedir :
            tarcmd='tar zxvf '+filedir+'/'+filename+' -C '+filedir
        else :
            tarcmd='tar zxvf '+filename
        p=self.send(tarcmd)
        return p
if __name__ == '__main__':
    remote_path = r'/home/sea'
    local_path = r'E:\PythonFiles\Learn\testsftp'

    host = Linux('192.168.180.128', 'root', '1234')

    # 将远端remote_path目录中的所有文件get到本地local_path目录
    host.sftp_get_dir(remote_path, local_path)
    # # 将本地local_path目录中的所有文件put到远端remote_path目录
    # host.sftp_put_dir(remote_path, local_path)
