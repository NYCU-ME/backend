# backend-flask-server

運行環境在 [backend](https://github.com/NYCU-ME/backend)，此 repo 乃 API server 之原始碼。

## Architecture

MVC 架構加上 Service Layer 與 SQLAlchemy ORM。

`main.py` 是主程式，`launch_thread` 是 backend_app（詳看 [backend](https://github.com/NYCU-ME/backend)）會開啓的 process，主要工作回收過期 domains。
`models` 負責與資料庫、資料來源互動，`models/db.sql` 是 ORM 的本體，而 `models/users.py`、`models/domains.py`、`models/records.py`……則類似 Repository Pattern 中的 Repository。
`services` 中負責簡化 Controller 的邏輯，將一部分邏輯和功能放入 Services，如與 DNS 相關的認證、註冊功能放入 DNSService 中。
`controllers` 負責處理 API 請求，會使用 services 中寫好的邏輯，在大多數的情況下，`controllers` 不該直接與 `models` 互動。
`tests` 則存放 Unit Tests。

## References

[Flask Docs](https://flask.palletsprojects.com/en/3.0.x/)
