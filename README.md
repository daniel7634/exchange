
# Exchange

這是一個用於提供匯率轉換的 Django API 的專案。

## 安裝前置條件
確保系統已安裝 Python 3.8 和 pip。

## 下載專案
從 GitHub 下載專案：
```
git clone https://github.com/daniel7634/exchange.git
```

## 安裝套件
使用 pip 安裝專案的相依套件
```
pip install -r requirements.txt
```

## 啟動 Django 伺服器
在終端機中，使用以下命令來啟動 Django 伺服器：
```
python manage.py runserver 8080
```
Django 伺服器將在 http://127.0.0.1:8080/ 上運行。
打開瀏覽器，前往 `http://127.0.0.1:8080/rate/`，就可以用 GET 使用此 API。

### 範例
http://127.0.0.1:8080/rate/?source=JPY&target=USD&amount=%C2%A512,123,235

## 執行 testcase
在專案目錄中使用以下命令來執行測試案例：
```
python manage.py test rate
```

## 檔案位置介紹
- api 邏輯在 rate/views.py 底下
- testcase 在 rate/tests.py 底下

## 特別註記
- amount 的格式會嚴格限制千分位和 currency symbol
- 匯率部分先直接 hardcoding

