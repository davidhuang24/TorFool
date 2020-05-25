# coding=utf-8
import logging
import select
import socket
import struct
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler

# Socks服务端代码
logging.basicConfig(level=logging.DEBUG)
SOCKS_VERSION = 5


# 使用连接池的 Socks5Server，继承了ThreadingMixIn线程池和TCPServer
class MySocks5Server(ThreadingMixIn, TCPServer):
    pass


# 生成一个拒绝连接的响应
def conn_failed_reply(address_type, error_code):
    return struct.pack("ss", SOCKS_VERSION, error_code, 0, address_type, 0, 0)


# 传输数据
def exchange_loop(client, remote):
    while True:
        # 等待客户端和目标服务器都准备好，r-可读的list,w-可写的list,e-错误list
        r, w, e = select.select([client, remote], [], [])
        if client in r:
            data = client.recv(10240)
            if remote.send(data) <= 0:
                break
        if remote in r:
            data = remote.recv(10240)
            if client.send(data) <= 0:
                break


# 请求处理器：处理来自客户端的TCP请求，为每个请求在一个单独线程里产生一个处理器实例
class MySocksRequestHandler(StreamRequestHandler):
    # 服务器设置的用户名和密码
    username = 'username'
    password = 'password'

    # 复写父类的方法，用于处理来自客户端的TCP请求
    def handle(self):
        logging.info('Accepting connection from %s:%s' % self.client_address)
        # 握手协商
        self.greet_for_negotiation()
        # 用户验证
        if not self.verify_credentials():
            return
        # 创建连接
        reply, remote, cmd = self.establish_connection()
        # 传输数据
        if reply[1] == 0 and cmd == 1:
            exchange_loop(self.connection, remote)
        # 关闭连接
        self.server.close_request(self.request)

    # 从协商请求报文读取客户端支持的验证方法
    def get_available_methods(self, n):
        methods = []
        for i in range(n):
            methods.append(ord(self.connection.recv(1)))
        return methods

    # 握手协商
    def greet_for_negotiation(self):
        # 从来自客户端的连接读取协商请求报文的前2字节
        header = self.connection.recv(2)
        # 解析协商请求报文的头部
        version, n_method = struct.unpack("ss", header)
        # socks 5
        assert version == SOCKS_VERSION
        assert n_method > 0
        # 服务端获取客户端可用的验证方法
        methods = self.get_available_methods(n_method)
        # 只接受用户名/密码验证
        if 2 not in set(methods):
            # close connection
            self.server.close_request(self.request)
            return
        # 服务端发送协商响应报文
        self.connection.sendall(struct.pack("ss", SOCKS_VERSION, 2))

    # 用户验证，返回验证结果
    def verify_credentials(self):
        # 子协议
        version = ord(self.connection.recv(1))
        assert version == 1
        # 解析用户名长度和用户名
        username_len = ord(self.connection.recv(1))
        username = self.connection.recv(username_len).decode('utf-8')
        # 解析密码长度和密码
        password_len = ord(self.connection.recv(1))
        password = self.connection.recv(password_len).decode('utf-8')
        # 验证成功，返回0x00的状态码
        if username == self.username and password == self.password:
            # success, status = 0
            response = struct.pack("ss", version, 0)
            self.connection.sendall(response)
            return True

        # 验证失败，返回不为0x00的状态码，关闭连接
        response = struct.pack("ss", version, 0xFF)
        self.connection.sendall(response)
        self.server.close_request(self.request)
        return False

    # 创建Socks连接，包括Socks请求和响应俩过程
    def establish_connection(self):
        # Socks请求
        version, cmd, _, a_type = struct.unpack("ss", self.connection.recv(4))
        assert version == SOCKS_VERSION

        if a_type == 1:  # IPv4
            dst_address = socket.inet_ntoa(self.connection.recv(4))
        elif a_type == 3:  # Domain name
            domain_length = ord(self.connection.recv(1)[0])
            dst_address = self.connection.recv(domain_length)
        # 端口号
        dst_port = struct.unpack('ss', self.connection.recv(2))[0]

        # Socks响应
        try:
            if cmd == 1:  # 只支持CONNECT请求类型
                # 服务端与目标服务器建立TCP连接
                remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote.connect((dst_address, dst_port))
                remote_address = remote.getsockname()
                logging.info('Connected to %s %s' % (dst_address, dst_port))
            else:
                self.server.close_request(self.request)
            # 从remote_address解析bnd_addr和bnd_port
            bnd_address = struct.unpack("ss", socket.inet_aton(remote_address[0]))[0]
            bnd_port = remote_address[1]
            # Socks响应：Ver,Rep,RSV,AType,BND_ADDR,BND_PORT
            reply = struct.pack("ss", SOCKS_VERSION, 0, 0, a_type, bnd_address, bnd_port)
        except Exception as err:
            logging.error(err)
            # 若目标服务器拒绝连接，Socks响应状态码为5表示拒绝连接
            reply = conn_failed_reply(a_type, 5)
        finally:
            # 服务端发送Socks响应
            self.connection.sendall(reply)
            return reply, remote, cmd


if __name__ == '__main__':
    # 生成一个服务端实例，该实例引用一个请求处理器实例
    with MySocks5Server(('127.0.0.1', 9011), MySocksRequestHandler) as server:
        # 开启服务
        server.serve_forever()
