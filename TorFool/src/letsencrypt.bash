

git clone https://github.com/letsencrypt/letsencrypt
cd letsencrypt
# 申请证书
./letsencrypt-auto certonly --preferred-challenges dns --manual --email hellodavidhuang@163.com -d *.overtime.icu
