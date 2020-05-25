# 传出流量规则匹配流程
# 在nat表新建一条子链
iptables -t nat -N REDSOCKS
# 在子链头部添加若干跳规则，用于忽略目的为保留地址的流量
iptables -t nat -A REDSOCKS -d 0.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 10.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 100.64.0.0/10 -j RETURN
iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 169.254.0.0/16 -j RETURN
iptables -t nat -A REDSOCKS -d 172.16.0.0/12 -j RETURN
iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN
iptables -t nat -A REDSOCKS -d 198.18.0.0/15 -j RETURN
iptables -t nat -A REDSOCKS -d 224.0.0.0/4 -j RETURN
iptables -t nat -A REDSOCKS -d 240.0.0.0/4 -j RETURN
# 在子链尾部追加一条规则，所有其他TCP流量都会被重定向到2020端口
iptables -t nat -A REDSOCKS -p tcp -j REDIRECT --to-ports 2020
# 让OUTPUT链引用REDSOCKS链
iptables -t nat -A OUTPUT -j REDSOCKS
# 在子链尾部追加规则，用于忽略Tor构建流量
iptables -t nat -I REDSOCKS -p all -m owner --uid-owner proxyuser -j RETURN
# 保存iptables的当前规则
Service iptables save
