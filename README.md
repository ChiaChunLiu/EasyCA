# Easy CA - 內網 SSL 憑證自助中心 🔒

這是一個基於 Docker 的輕量級內部憑證管理服務 (Private CA)。它允許您透過簡單的網頁介面，為區域網路內的服務快速簽發 SSL 憑證，並實現瀏覽器信任的 HTTPS 連線 (綠色鎖頭)。

## 🛠️ 核心技術

本專案核心使用 [mkcert](https://github.com/FiloSottile/mkcert) 工具。

  * **mkcert**：一個無需配置的工具，用於製作本地信任的開發憑證。
  * **Flask**：提供網頁介面與 API 邏輯。
  * **Docker**：容器化部署，確保環境一致且資料持久化。

-----

## 🚀 快速啟動 (Docker)

### 1\. 準備環境

確保您的電腦已安裝 Docker Desktop 或 Docker Compose。

### 2\. 啟動服務

在專案根目錄下開啟終端機，執行以下指令：

```bash
docker-compose up -d --build
```

### 3\. 訪問服務

開啟瀏覽器，輸入以下網址 (預設使用 Port 7777)：

  * **HTTP 模式 (預設)**: `http://localhost:7777` 或 `http://<您的區域網路IP>:7777`

-----

## 🔐 啟用 Easy CA 自身的 HTTPS

為了讓本服務也具備 HTTPS 保護 (自我簽署)，請依照以下步驟操作：

1.  **生成憑證**：

      * 先以 HTTP 方式進入網站。
      * 在輸入框輸入**本機的區域網路 IP** (例如 `192.168.1.50`)。
      * 點擊下載並解壓縮 ZIP 檔。

2.  **部署憑證**：

      * 在專案根目錄下建立一個名為 `ssl` 的資料夾。
      * 將解壓後的 `server.crt` 和 `server.key` 放入該資料夾。
      * **注意**：檔名必須完全一致，不能是 `192.168...pem`。

    <!-- end list -->

    ```text
    lancert/
    ├── ssl/
    │   ├── server.crt  <-- 您的公開憑證
    │   └── server.key  <-- 您的私鑰
    └── ...
    ```

3.  **重啟服務**：

    ```bash
    docker-compose restart
    ```

4.  **驗證**：
    現在您可以使用 HTTPS 訪問：`https://<您的區域網路IP>:7777`。
    *(若移除 ssl 資料夾內的檔案並重啟，系統會自動降級回 HTTP 模式)*

-----

## 📥 安裝 Root CA (信任憑證)

為了讓瀏覽器顯示綠色鎖頭，每台裝置只需執行一次此步驟。

請在網頁首頁點擊 **「下載 Root CA」** 取得 `rootCA.pem`。

### 💻 Windows 使用者 (重要)

Windows 預設無法直接安裝 `.pem` 檔，請依照以下步驟：

1.  **改名**：將下載的 `rootCA.pem` 副檔名改為 `.crt` (即 `rootCA.crt`)。
2.  **安裝**：雙擊檔案 -\> 點選 **「安裝憑證」**。
3.  **位置**：
      * 儲存位置選 **「本機電腦 (Local Machine)」**。
      * **❌ 切勿選自動**。請選 **「將所有憑證放入以下的存放區」**。
      * 瀏覽並選擇 **「受信任的根憑證授權單位 (Trusted Root Certification Authorities)」**。
4.  完成後重啟瀏覽器。

### 🍎 macOS 使用者

1.  雙擊 `rootCA.pem` 加入鑰匙圈。
2.  開啟「鑰匙圈存取」，找到該憑證。
3.  雙擊憑證 -\> 展開「信任」 -\> 將 **「使用此憑證時」** 改為 **「永遠信任」**。

### 📱 iOS / Android

  * **iOS**: 下載後至「設定」-\>「已下載描述檔」安裝。安裝後需至「一般」-\>「關於本機」-\>「憑證信任設定」中將其開啟。
  * **Android**: 至「設定」-\>「安全性」-\>「加密與憑證」-\>「安裝憑證」-\> 選取「CA 憑證」並匯入檔案。

-----

## 📂 專案結構

```text
.
├── docker-compose.yml   # Docker 設定檔 (定義 Port 與 Volume)
├── Dockerfile           # 映像檔建置 (安裝 Python & mkcert)
├── app.py               # 核心邏輯 (智慧切換 HTTP/HTTPS)
├── requirements.txt     # Python 依賴
├── templates/
│   └── index.html       # 前端介面
├── data/                # [自動生成] 存放 Root CA 私鑰 (請勿刪除)
└── ssl/                 # [手動建立] 存放本服務的 server.crt/key
```