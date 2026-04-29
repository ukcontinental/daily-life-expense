# Gmail MCP Server 安裝指南（GongRzhe 版）

> 用途：讓 Claude 能直接讀 Gmail 信件附件（PDF/Word/Excel/圖片等），解決目前 Cowork 內建 Gmail connector 讀不到附件的問題。
> 官方來源：https://github.com/GongRzhe/Gmail-MCP-Server
> npm 套件名：`@gongrzhe/server-gmail-autoauth-mcp`
> 建立日期：2026-04-22（請 Willie 需要時告訴 Claude「調出 Gmail MCP 安裝指南」）

---

## 〇、開始前準備（5 分鐘）

**你需要有的東西：**
- [ ] macOS 電腦（你目前使用中）
- [ ] 已安裝 Node.js（如果沒有，到 https://nodejs.org/ 下載 LTS 版本安裝）
- [ ] Google 帳號（`uk.continental@gmail.com`）
- [ ] Claude Desktop 應用程式（你目前使用中）
- [ ] 瀏覽器（Chrome / Safari 都可以，做 Google 授權用）

**時間估計：**
- 熟手：10 分鐘
- 第一次做：20–30 分鐘（主要卡在 Google Cloud 那邊的設定）

---

## 一、到 Google Cloud Console 申請 OAuth 憑證（10–15 分鐘）

這步驟是讓你自己的 Gmail MCP 服務取得 Google 官方認證，沒這步就不能存取你的 Gmail。

### 1.1 建立 Google Cloud 專案

1. 瀏覽器打開 https://console.cloud.google.com/
2. 用 `uk.continental@gmail.com` 登入
3. 左上角的專案選單點一下 → 「新增專案 (New Project)」
4. 專案名稱隨便取，例如 `gmail-mcp-willie` → 點「建立」
5. 等幾秒，建好後確認左上角已經切到這個新專案

### 1.2 啟用 Gmail API

1. 左側選單（或搜尋框）找到 **「API 和服務 / APIs & Services」** → **「程式庫 / Library」**
2. 搜尋框打 `Gmail API` → 點進去 → 按 **「啟用 / Enable」**
3. 等它啟用完（約 10 秒）

### 1.3 設定 OAuth 同意畫面 (OAuth consent screen)

1. 左側 **「API 和服務」** → **「OAuth 同意畫面 / OAuth consent screen」**
2. User Type 選 **「外部 / External」** → 點「建立」
3. 填入：
   - App name：`Gmail MCP for Willie`（隨便取）
   - User support email：`uk.continental@gmail.com`
   - Developer contact information：`uk.continental@gmail.com`
   - 其他留空，按「儲存並繼續」
4. Scopes 頁面直接「儲存並繼續」（不用手動加）
5. Test users 頁面 → 點「Add Users」→ 填入 `uk.continental@gmail.com` → 儲存
   ⚠️ **這步很重要**，如果沒把自己加成 test user，授權會被拒絕
6. 最後「回到控制台」

### 1.4 建立 OAuth 用戶端 ID

1. 左側 **「API 和服務」** → **「憑證 / Credentials」**
2. 上方 **「+ 建立憑證 / Create Credentials」** → 選 **「OAuth 用戶端 ID / OAuth client ID」**
3. 應用程式類型選：**「電腦版應用程式 / Desktop app」**（最省事，不用設 redirect URI）
4. 名稱隨便取，例如 `Claude Gmail MCP` → 點「建立」
5. 彈出視窗會顯示 Client ID 和 Client secret → 點右邊 **「下載 JSON」**
6. 把下載的檔案（檔名會像 `client_secret_xxxx.json`）改名成 **`gcp-oauth.keys.json`**

> 💡 如果你想選「Web application」也可以，但要在 Authorized redirect URIs 多加一行 `http://localhost:3000/oauth2callback`。Desktop app 比較簡單。

---

## 二、把憑證檔放到正確位置 + 跑一次授權（3 分鐘）

打開 macOS 的 **「終端機 Terminal」**（Spotlight 搜尋 Terminal 就有），逐行複製貼上：

```bash
# 1. 建立 MCP 專用資料夾
mkdir -p ~/.gmail-mcp

# 2. 把剛剛下載並改名的憑證檔移進去（假設放在 Downloads）
mv ~/Downloads/gcp-oauth.keys.json ~/.gmail-mcp/

# 3. 跑一次授權（會自動開瀏覽器）
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

執行第 3 步時會發生什麼：
- 終端機會開始下載 MCP 套件（首次需要 30 秒到 1 分鐘）
- 瀏覽器會自動打開 Google 登入頁
- 選 `uk.continental@gmail.com` 登入
- 會出現「這個 App 未經 Google 驗證」的警告 → 點 **「進階 / Advanced」** → **「前往 Gmail MCP for Willie（不安全）」**
  （因為這個 App 只有你自己在用，不需要送 Google 審查）
- 勾選 **所有** 要求的 Gmail 權限 → 按「繼續」
- 看到「Authentication successful!」就成功了
- 終端機會顯示憑證已存到 `~/.gmail-mcp/credentials.json`

✅ 到這裡，Gmail MCP 就準備好了。

---

## 三、告訴 Claude Desktop 要用這個 MCP（2 分鐘）

### 3.1 找到 Claude Desktop 設定檔

在終端機執行：

```bash
open ~/Library/Application\ Support/Claude/
```

Finder 會打開 `Claude` 資料夾，找 `claude_desktop_config.json` 檔案。
- 如果有這個檔案 → 直接用「文字編輯」或 VS Code 打開編輯
- 如果沒有 → 新增一個空檔，檔名就叫 `claude_desktop_config.json`

### 3.2 貼入以下 JSON 內容

**情況 A：你原本沒有 `claude_desktop_config.json`**（整個檔案貼入）

```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": [
        "@gongrzhe/server-gmail-autoauth-mcp"
      ]
    }
  }
}
```

**情況 B：你已經有 `claude_desktop_config.json` 而且裡面有其他 MCP**
只在 `mcpServers` 物件裡加一個 `"gmail": {...}` 鍵，範例：

```json
{
  "mcpServers": {
    "existing-server": { "...原本的東西..." },
    "gmail": {
      "command": "npx",
      "args": [
        "@gongrzhe/server-gmail-autoauth-mcp"
      ]
    }
  }
}
```

⚠️ JSON 很挑剔，記得 **逗號不能多不能少**、**雙引號不能用中文引號**。

### 3.3 重啟 Claude Desktop

完全關閉 Claude Desktop（`Cmd + Q`），再重新打開。
打開後開啟一個新對話，問 Claude「你有 gmail 工具嗎？」，如果他回答列出 `search_emails`、`read_email`、`download_attachment` 等工具，就成功了。

---

## 四、可用工具清單（裝好後可以叫 Claude 做這些事）

| 工具名 | 做什麼 |
|---|---|
| `search_emails` | 搜尋信件（支援 Gmail 搜尋語法，例如 `from:annie@bubbletea123.com has:attachment newer_than:7d`） |
| `read_email` | 讀單封信內容 + 顯示附件清單（含檔名、大小、attachmentId） |
| **`download_attachment`** | ⭐ **關鍵功能**：下載附件到你電腦本地（再搭配 PDF skill 就能分析 PDF 內容） |
| `send_email` | 寄信（支援 HTML、附件） |
| `draft_email` | 存成草稿（支援附件） |
| `modify_email` | 加/移除標籤（歸檔、標記已讀等） |
| `delete_email` | 刪除信件 |
| `list_email_labels` | 列出所有 Gmail 標籤 |
| `create_label` / `update_label` / `delete_label` / `get_or_create_label` | 管理標籤 |
| `batch_modify_emails` / `batch_delete_emails` | 批次處理多封信 |

**PDF 處理流程（自動化後）：**
```
你 → Claude：「把 Annie 今天的 T&T PO 附件整理成一張表」
Claude 會：
  1. search_emails (from:annie@bubbletea123.com newer_than:1d has:attachment)
  2. read_email → 拿到每封信的 attachmentId
  3. download_attachment → 存到你的資料夾
  4. 用 pdf skill 解析每份 PDF → 抽出品項/數量/金額/到貨日
  5. 彙總成 Excel 或表格給你
```

---

## 五、疑難排解

| 狀況 | 解法 |
|---|---|
| `OAuth Keys Not Found` | 確認 `gcp-oauth.keys.json` 在 `~/.gmail-mcp/` 裡，且檔名完全正確（不是 `gcp-oauth.keys.json.json`） |
| `Invalid Credentials Format` | 檢查 JSON 檔裡是 `"installed"` 還是 `"web"`，Desktop app 類型應該是 `"installed"` |
| `Port 3000 already in use` | 授權時 port 3000 被佔用，關掉其他占用該 port 的程式，或重開機重試 |
| Claude Desktop 看不到 gmail 工具 | 1. 檢查 JSON 語法 2. 完全 `Cmd+Q` 關閉再重開 3. 看 Claude Desktop 的 MCP log：`~/Library/Logs/Claude/mcp*.log` |
| 授權時 Google 顯示「Access blocked」 | 1.3 步驟忘了把自己加成 Test user |
| 附件下載失敗 | 確認目標資料夾有寫入權限；Gmail 單檔附件上限 25MB |
| 重新授權 | 刪除 `~/.gmail-mcp/credentials.json`，再跑一次 `npx @gongrzhe/server-gmail-autoauth-mcp auth` |

---

## 六、安全性須知

- 你的 Gmail 授權 token 存在 **你自己的電腦本機** `~/.gmail-mcp/credentials.json`，不會上傳到 GongRzhe 或任何雲端。
- `gcp-oauth.keys.json` 也只留在本機。
- 如果以後要撤銷權限：到 https://myaccount.google.com/permissions 找「Gmail MCP for Willie」移除。
- **不要把 `~/.gmail-mcp/` 整個資料夾分享給別人 / 上傳 GitHub / 傳 Slack**，裡面的檔案等同 Gmail 的鑰匙。

---

## 七、Docker 替代方案（選用，進階）

如果你不想裝 Node.js，可以改用 Docker。授權步驟：

```bash
docker run -i --rm \
  --mount type=bind,source=/Users/willie/.gmail-mcp/gcp-oauth.keys.json,target=/gcp-oauth.keys.json \
  -v mcp-gmail:/gmail-server \
  -e GMAIL_OAUTH_PATH=/gcp-oauth.keys.json \
  -e "GMAIL_CREDENTIALS_PATH=/gmail-server/credentials.json" \
  -p 3000:3000 \
  mcp/gmail auth
```

`claude_desktop_config.json` 改成：

```json
{
  "mcpServers": {
    "gmail": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "mcp-gmail:/gmail-server",
        "-e", "GMAIL_CREDENTIALS_PATH=/gmail-server/credentials.json",
        "mcp/gmail"
      ]
    }
  }
}
```

---

## 八、Willie 的快速檢查清單（印出來照著做）

- [ ] Step 1：Google Cloud Console 建新專案 `gmail-mcp-willie`
- [ ] Step 2：啟用 Gmail API
- [ ] Step 3：OAuth 同意畫面選 External、加 `uk.continental@gmail.com` 為 test user
- [ ] Step 4：建 Desktop app OAuth client ID、下載 JSON、改名為 `gcp-oauth.keys.json`
- [ ] Step 5：`mkdir -p ~/.gmail-mcp && mv ~/Downloads/gcp-oauth.keys.json ~/.gmail-mcp/`
- [ ] Step 6：`npx @gongrzhe/server-gmail-autoauth-mcp auth`（瀏覽器授權）
- [ ] Step 7：編輯 `~/Library/Application Support/Claude/claude_desktop_config.json` 加 gmail server
- [ ] Step 8：`Cmd + Q` 關閉 Claude Desktop → 重開
- [ ] Step 9：問 Claude「列出你的 Gmail 工具」確認成功

---

*需要時叫 Claude「調出 Gmail MCP 安裝指南」，就會把這份再給你看。*
