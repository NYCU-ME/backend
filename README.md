# new-backend

## 請更改下列文件

1. docker-compose.yaml
2. config/init.sql

並且透過 `sudo tsig-keygen -a hmac-sha512  ddnskey` 生成一個 ddnskey.conf 取代掉 `config/named/ddnskey.conf`，請注意爲了執行此指令你必須安裝 bind9。


