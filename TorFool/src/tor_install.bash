# 编译源码方式安装Tor流程

# 安装make编译工具
apt-get update
apt-get install make
# 安装Tor编译的依赖库
apt-get install build-essential libevent-dev libssl-dev
# 创建一个普通用户proxyuser，设置uid为1000并设置密码
adduser -u 1000 proxyuser
# 切换系统用户为proxyuser
su proxya
cd ~
#下载并解压Tor源码包
wget https://dist.torproject.org/tor-0.4.2.5.tar.gz
tar zxvf tor-0.4.2.5.tar.gz
# 运行配置文件，避免安装asciidoc来编译manpage
./tor-0.4.2.5/configure --disable-asciidoc
Make # 编译源码
# 退出到root用户下，将/usr/bin目录下所有文件拥有者改为proxyuser
exit
chown -R proxya /usr/bin/
# 切换用户
su proxyuser
cd ~
# 设置一个软链接，以便 proxyuser用户可在任意路径下启动tor
ln -s /home/proxya/tor-0.4.2.5/src/app/tor /usr/bin/tor
# 不挂断启动tor服务 并将启动日志写入文件中，避免重开终端的麻烦
nohup tor >> tor.log 2>&1 &
