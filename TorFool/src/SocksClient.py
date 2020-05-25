#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 9000))

# client -> server      初始化
# ver(1byte)            client版本，默认 \x05
# nmethods(1byte)       认证方式个数，默认 \x01
# methods(1-255byte)    认证方式种类，默认 \x00 不需要认证
client.send(b'\x05\x01\x00')

# server -> client      服务器回复
# ver(1byte)            client版本，默认 \x05
# method(1byte)         认证方式，默认 \x00 不需要认证
data = client.recv(2)
# b'\x05\x00'

# client -> server      客户端发送代理请求
# ver(1byte)            client版本，默认 \x05
# cmd(1byte)            代理方式 \x01(CONNECT) \x02(BIND) \x03(UDP)
# rsv(1byte)            保留字段，默认 \x00
# atype(1byte)          请求地址类型 \x01(IPV4 4byte) \x03(域名 1byte长度加域名) \x04(IPV6 16byte)
# addr()                目标地址
# port(2byte)           目标端口
client.send(b'\x05\x01\x00\x01\x08\x08\x08\x08\x00\x50')

# server -> client      服务器回复
# ver(1byte)            client版本，默认 \x05
# rep(1byte)            应答字段 0x00表示成功 0x01普通client服务器连接失败 0x02现有规则不允许连接 0x03网络不可达 0x04主机不可达 0x05连接被拒 0x06 TTL超时 0x07不支持的命令 0x08不支持的地址类型 0x09 - 0xFF未定义
# rsv(1byte)            保留字段，默认 \x00
# atype(1byte)          请求地址类型 \x01(IPV4 4byte) \x03(域名 1byte长度加域名) \x04(IPV6 16byte)
# addr()                目标地址，默认 \x00\x00\x00\x00
# port(2byte)           目标端口，默认 \x00\x00
data = client.recv(120)
# b'\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00'

# client -> server      客户端发送代理请求
client.send(b'GET / HTTP/1.1\r\nHost: www.mogublog.net\r\nConnection: close\r\n\r\n')

# server -> client      服务器回复
data = client.recv(10240)

client.close()

print(data)