# backend

## 架構

有 6 個 Containers：
- mysqld：資料的儲存
- named：BIND9 DNS server
- flask_app：API server
- backend_app：domain 回收機制
- fluentd：log 收集器
- elasticsearch：log 分析工具

有 1 個 submodule，是 flask_app 和 backend_app 的原始碼，請看：
- [backend/images/flask/app](https://github.com/NYCU-ME/backend-flask-server/tree/main)

## CICD Flow

在 [backend/images/flask/app](https://github.com/NYCU-ME/backend-flask-server/tree/main) 發送 PR，同時會在 backend（本 repo）發送一個 PR，待管理員通過后，程式碼會自動部署到 production 上。

## 請執行以下指令

```
# make pull
# make init
```

## 建構
```
# sudo make build
```

## 運行

```
# sudo make run
```

## 測試

```
# sudo make test
```

## 清除測試資料

```
# make rm-db
```
