# coding: utf-8
import paramiko
import os
import select
import sys


# 定义一个类，表示一台远端linux主机
class Linux(object):
    # 通过IP, 用户名，密码，超时时间初始化一个远程Linux主机
    def __init__(self, ip, username, password, timeout=3000):
        self.ip = ip
        self.username = username
        self.password = password
        self.timeout = timeout
        # 链接失败的重试次数
        self.try_times = 3

    # 调用该方法连接远程主机
    def info(self):
        while True:
            # 连接过程中可能会抛出异常，比如网络不通、链接超时
            try:
                t = paramiko.Transport(sock=(self.ip, 22))
                t.connect(username=self.username, password=self.password)
                channel = t.open_session()
                channel.settimeout(self.timeout)
                channel.get_pty()
                channel.invoke_shell()
                # 如果没有抛出异常说明连接成功，直接返回
                print(u'连接%s成功' % self.ip)
                # 接收到的网络数据解码为str
                print(channel.recv(65535).decode('utf-8'))
                channel.close()
                t.close()
                return
            # 这里不对可能的异常如socket.error, socket.timeout细化，直接一网打尽
            except Exception as e1:
                if self.try_times != 0:
                    print(u'连接%s失败，进行重试' % self.ip)
                    self.try_times -= 1
                else:
                    print(u'重试3次失败，结束程序')
                    exit(1)

    def xshell(self):

        # 建立一个socket
        trans = paramiko.Transport((self.ip, 22))
        # 启动一个客户端
        trans.start_client()

        # 如果使用rsa密钥登录的话
        '''
        default_key_file = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa')
        prikey = paramiko.RSAKey.from_private_key_file(default_key_file)
        trans.auth_publickey(username='super', key=prikey)
        '''
        # 如果使用用户名和密码登录
        trans.auth_password(username=self.username, password=self.password)
        # 打开一个通道
        channel = trans.open_session()
        # 获取终端
        channel.get_pty()
        # 激活终端，这样就可以登录到终端了，就和我们用类似于xshell登录系统一样
        channel.invoke_shell()
        # 下面就可以执行你所有的操作，用select实现
        # 对输入终端sys.stdin和 通道进行监控,
        # 当用户在终端输入命令后，将命令交给channel通道，这个时候sys.stdin就发生变化，select就可以感知
        # channel的发送命令、获取结果过程其实就是一个socket的发送和接受信息的过程
        while True:
            readlist, writelist, errlist = select.select(
                [channel, sys.stdin, ], [], [])
            # 如果是用户输入命令了,sys.stdin发生变化
            if sys.stdin in readlist:
                # 获取输入的内容
                input_cmd = sys.stdin.read(1)
                # 将命令发送给服务器
                channel.sendall(input_cmd)

            # 服务器返回了结果,channel通道接受到结果,发生变化 select感知到
            if channel in readlist:
                # 获取结果
                result = channel.recv(1024)
                # 断开连接后退出
                if len(result) == 0:
                    print("\r\n**** EOF **** \r\n")
                    break
                # 输出到屏幕
                sys.stdout.write(result.decode())
                sys.stdout.flush()

        # 关闭通道
        channel.close()
        # 关闭链接
        trans.close()

    # ------获取本地指定目录及其子目录下的所有文件------
    def __get_all_files_in_local_dir(self, local_dir):
        # 保存所有文件的列表
        all_files = list()
        # 获取当前指定目录下的所有目录及文件，包含属性值
        for x in os.listdir(local_dir):
            # local_dir目录中每一个文件或目录的完整路径
            # os.path.join()在Linux/macOS下会以斜杠（/）分隔路径，而在Windows下则会以反斜杠（\）分隔路径。
            filename = os.path.join(local_dir, x)
            filename = filename.replace('\\', '/')
            # 如果是目录，则递归处理该目录
            if os.path.isdir(filename):
                all_files.extend(self.__get_all_files_in_local_dir(filename))
            else:
                all_files.append(filename)
        return all_files

    def sftp_put_dir(self, local_dir, remote_dir):
        t = paramiko.Transport(sock=(self.ip, 22))
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
            print(u'文件%s传输到%s中...' % (filename, self.ip))
            sftp.put(x, remote_filename)
        sftp.close()
        t.close()


if __name__ == '__main__':
    remote_path = r'/home/pi/Downloads/Test'
    local_path = r'./Test'
    host = Linux('192.168.1.7', 'pi', 'pi')
    host.xshell()
    # host.info()
    # host.sftp_put_dir(local_path, remote_path)
