---
title: JLPT N1 適應性學習系統
type: feature
status: in-progress
created: 2026-02-03
---

# JLPT N1 適應性學習系統

## 背景

用戶 JLPT N1 成績：
- 總分：84/180（差 16 分及格）
- 言語知識：25/60（文法 C 級）
- 讀解：23/60（最弱）
- 聽解：36/60（強項）

需要一個能根據用戶程度即時調整的互動式學習系統。

## 變更內容

建立本地端 AI 驅動的 N1 學習系統：

### 核心功能
1. **文法診斷對話** - Claude API 出題，即時解釋，記錄弱點
2. **讀解陪練** - 短文分析，逐句拆解句子結構
3. **語彙練習** - 漢字讀音、意思、用法
4. **弱點複習** - 錯題自動排入複習佇列
5. **進度追蹤** - 各文法點掌握度視覺化

### 技術架構
```
前端：Vite + Vue 3 + PrimeVue + TypeScript
後端：FastAPI + Claude API (Anthropic SDK)
資料庫：SQLite（本地檔案）
```

### 學習模式
| 模式 | 說明 |
|------|------|
| 文法練習 | AI 出題 → 用戶作答 → AI 解釋 → 記錄掌握度 |
| 讀解練習 | AI 給短文 → 逐句分析 → 問答理解 |
| 自由對話 | 用日文對話 → AI 糾正文法錯誤 |
| 弱點複習 | 根據錯題紀錄針對性出題 |

## 影響範圍

新專案，建立以下檔案：

```
jlpt-n1-learner/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.vue    # 對話介面
│   │   │   ├── ProgressDashboard.vue # 進度儀表板
│   │   │   └── PracticeMode.vue     # 練習模式選擇
│   │   ├── composables/
│   │   │   └── useChat.ts           # 對話邏輯
│   │   ├── stores/
│   │   │   └── learning.ts          # 學習狀態管理
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI 入口
│   │   ├── routers/
│   │   │   ├── chat.py              # 對話 API
│   │   │   └── progress.py          # 進度 API
│   │   ├── services/
│   │   │   ├── claude_service.py    # Claude API 封裝
│   │   │   └── learning_service.py  # 學習邏輯
│   │   └── models/
│   │       └── database.py          # SQLite 模型
│   └── requirements.txt
├── openspec/
│   └── changes/
└── README.md
```

## UI/UX 規格

### 主介面佈局
- 左側：練習模式選擇 + 進度概覽
- 右側：對話區域（主要互動區）
- 底部：輸入框 + 送出按鈕

### 色彩
- 使用 PrimeVue Aura 主題預設色彩
- 正確回答：綠色 (success)
- 錯誤回答：橘色 (warning)
- AI 訊息：灰色背景
- 用戶訊息：主題色背景

### 響應式
- 本地開發，優先桌面版
- 最小寬度 1024px

## 測試計畫

1. 後端 API 測試
   - [ ] `/api/chat` 能正確呼叫 Claude API
   - [ ] `/api/progress` 能正確讀寫 SQLite

2. 前端功能測試
   - [ ] 對話介面能發送/接收訊息
   - [ ] 進度儀表板正確顯示數據
   - [ ] 各練習模式可正常切換

3. 整合測試
   - [ ] 完整學習流程：選模式 → 練習 → 看進度
   - [ ] 錯題能正確記錄並出現在複習中

## Checklist

- [ ] 建立前端專案 (Vite + Vue + PrimeVue)
- [ ] 建立後端專案 (FastAPI)
- [ ] 實作 Claude API 服務
- [ ] 實作 SQLite 資料模型
- [ ] 實作對話介面
- [ ] 實作進度追蹤
- [ ] 實作文法練習模式
- [ ] 實作讀解練習模式
- [ ] 測試完整流程
