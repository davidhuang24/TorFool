

# Tor2web安装脚本
# 下载Tor2web自动安装脚本
wget https://deb.globaleaks.org/install-tor2web.sh
# 授权脚本可执行
chmod +x install-tor2web.sh
# 安装Tor2web
./install-tor2web.sh

# 设置软链接和修改权限操作
# 设置软链接
ln -s /etc/letsencrypt/live/overtime.icu/privkey.pem /home/tor2web/certs/tor2web-key.pem
ln -s /etc/letsencrypt/live/overtime.icu/cert.pem /home/tor2web/certs/tor2web-certificate.pem
ln -s /etc/letsencrypt/live/overtime.icu/fullchain.pem /home/tor2web/certs/tor2web-intermediate.pem
ln -s /etc/letsencrypt/live  /etc/letsencrypt/archive/
# 修改权限
chgrp tor2web /etc/letsencrypt/live/
chgrp tor2web /etc/letsencrypt/archive
chmod g+rx /etc/letsencrypt/archive
chmod g+rx /etc/letsencrypt/live
listen_port_https = 443

# 设置Tor2web 自启动
update-rc.d tor2web defaults
# 启动Tor2web
service tor2web start





