# 作業：設計 Skill + 打造 AI 聊天機器人

> **繳交方式**：將你的 GitHub repo 網址貼到作業繳交區
> **作業性質**：個人作業

---

## 作業目標

使用 Antigravity Skill 引導 AI，完成一個具備前後端的 AI 聊天機器人。
重點不只是「讓程式跑起來」，而是透過設計 Skill，學會用結構化的方式與 AI 協作開發。

---

## 繳交項目

你的 GitHub repo 需要包含以下內容：

### 1. Skill 設計（`.agents/skills/`）

為以下五個開發階段＋提交方式各設計一個 SKILL.md：

| 資料夾名稱        | 對應指令          | 說明                                                                           |
| ----------------- | ----------------- | ------------------------------------------------------------------------------ |
| `prd/`          | `/prd`          | 產出 `docs/PRD.md`                                                           |
| `architecture/` | `/architecture` | 產出 `docs/ARCHITECTURE.md`                                                  |
| `models/`       | `/models`       | 產出 `docs/MODELS.md`                                                        |
| `implement/`    | `/implement`    | 產出程式碼（**需指定**：HTML 前端 + FastAPI + SQLite 後端）              |
| `test/`         | `/test`         | 產出手動測試清單                                                               |
| `commit/`       | `/commit`       | 自動 commit + push（**需指定**：使用者與 email 使用 Antigravity 預設值） |

### 2. 開發文件（`docs/`）

用你設計的 Skill 產出的文件，需包含：

- `docs/PRD.md`
- `docs/ARCHITECTURE.md`
- `docs/MODELS.md`

### 3. 程式碼

一個可執行的 AI 聊天機器人，需支援以下功能：

| 功能           | 說明                                       | 是否完成 |
| -------------- | ------------------------------------------ | -------- |
| 對話狀態管理   | 支援多聊天室（session），維持上下文        | O        |
| 訊息系統       | 訊息結構包含 role、content、timestamp      | O        |
| 對話歷史管理   | 可顯示並切換過去的對話紀錄                 | O        |
| 上傳圖片或文件 | 支援使用者上傳檔案作為對話內容             | O        |
| 回答控制       | 提供重新生成（regenerate）或中止回應的功能 | X        |
| 記憶機制       | 儲存使用者偏好，實現跨對話持續性           | O        |
| 工具整合       | 串接外部 API，使聊天機器人具備實際操作能力 | X        |

### 4. 系統截圖（`screenshots/`）

在 `screenshots/` 資料夾放入以下截圖：

- `chat.png`：聊天機器人主畫面，**需包含至少一輪完整的對話**
- `history.png`：對話歷史或多 session 切換的畫面

### 5. 心得報告（本 README.md 下方）

在本 README 的**心得報告**區填寫。

---

## 專案結構範例

```
your-repo/
├── .agents/
│   └── skills/
│       ├── prd/SKILL.md
│       ├── architecture/SKILL.md
│       ├── models/SKILL.md
│       ├── implement/SKILL.md
│       ├── test/SKILL.md
│       └── commit/SKILL.md
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   └── MODELS.md
├── templates/
│   └── index.html
├── screenshots/
│   ├── chat.png
│   ├── history.png
│   └── skill.png
├── app.py
├── requirements.txt
├── .env.example
└── README.md          ← 本檔案（含心得報告）
```

---

## 啟動方式

```bash
# 1. 建立虛擬環境
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. 安裝套件
pip install -r requirements.txt

# 3. 設定環境變數
cp .env.example .env
# 編輯 .env，填入 GEMINI_API_KEY

# 4. 啟動伺服器
uvicorn app:app --reload
# 開啟瀏覽器：http://localhost:8000
```

---

## 心得報告

**姓名**：Jeff
**學號**：

### 問題與反思

**Q1. 你設計的哪一個 Skill 效果最好？為什麼？哪一個效果最差？你認為原因是什麼？**

> **效果最好的是 `implement/SKILL` (實作)**。因為在前面的 PRD、Architecture 與 Models 階段，我們已經把邊界條件、技術選型（HTML + FastAPI + SQLite）與資料表結構定義得非常清楚，這讓 AI 產生程式碼時幾乎沒有幻覺，能一次性產出高品質且架構分明的全端程式碼。
> 
> **效果最差的可能是 `test/SKILL` (測試)**。因為缺乏自動化測試環境，AI 只能條列出手動測試的清單，而無法驗證實際的畫面點擊與互動效果，最終還是需要依賴人類肉眼去確認畫面的 RWD 與 CSS 渲染是否正確。

---

**Q2. 在用 AI 產生程式碼的過程中，你遇到什麼問題是 AI 沒辦法自己解決、需要你介入處理的？**

> 1. **環境與執行路徑問題**：一開始執行 `uvicorn main:app --reload` 時發生了 `500 Internal Server Error` 和 `ModuleNotFoundError`，因為 AI 無法自動偵測終端機當下的工作目錄。必須由我貼出 Terminal 的 Error Log，AI 才知道要將指令改為 `uvicorn backend.main:app --reload`。
> 2. **API Quota 限制**：AI 預設幫我接上了 `gemini-2.5-pro` 模型，導致在對話時跳出 `429 RESOURCE_EXHAUSTED` (配額不足)。因為 AI 看不到我的 API Key 帳號狀態，必須由我把 Error 丟回給 AI，它才意識到並改用免費額度較大的 `gemini-2.5-flash` 來解決問題。