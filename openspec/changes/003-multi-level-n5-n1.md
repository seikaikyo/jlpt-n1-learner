---
title: JLPT 多級別支援 (N5-N1)
type: feature
status: completed
created: 2026-02-27
---

# JLPT 多級別支援 (N5-N1)

## 變更內容

將現有 N1 專用系統擴充為 N5-N1 全級別。用戶可選擇級別，題庫、system prompt、難度自動對應。

## 設計決策

### 級別 vs 模式

```
目前: mode = grammar | reading | conversation（固定 N1）
改後: level = N5 | N4 | N3 | N2 | N1
      mode  = grammar | reading | conversation（不變）
```

### 各級別差異

| 級別 | 文法點數量 | 讀解長度 | 會話複雜度 | 詞彙範圍 |
|------|-----------|---------|-----------|---------|
| N5 | 15 | 50-100字 | 簡短日常 | 基礎 800 字 |
| N4 | 20 | 100-200字 | 日常對話 | 約 1,500 字 |
| N3 | 25 | 200-400字 | 一般話題 | 約 3,000 字 |
| N2 | 30 | 400-800字 | 社會話題 | 約 6,000 字 |
| N1 | 31 (現有) | 150-800+字 | 職場/學術 | 約 10,000 字 |

## 影響範圍

### 前端 (4 檔案修改)

| 檔案 | 修改內容 |
|------|---------|
| `frontend/src/App.vue` | 標題動態化、新增 level Select |
| `frontend/src/components/ModeSelector.vue` | 描述文字依級別變化 |
| `frontend/src/components/ChatInterface.vue` | badge 動態化、startPrompt 依級別 |
| `frontend/src/composables/useChat.ts` | API 請求加 level 參數 |

### 後端 (5 檔案修改 + 1 新增)

| 檔案 | 修改內容 |
|------|---------|
| `backend/app/services/claude_service.py` | GRAMMAR_POINTS 改為 dict[level]、system prompt 參數化 |
| `backend/app/routers/chat.py` | ChatRequest 加 level 欄位 |
| `backend/app/models/database.py` | LearningRecord 加 level 欄位 |
| `backend/app/services/learning_service.py` | 按級別過濾統計 |
| `backend/app/services/question_bank_service.py` | 按級別子目錄載入 |
| 新增 `backend/app/config/grammar_points.py` | 各級文法點集中管理 |

### 題庫結構

```
backend/data/question_bank/
├── n5/
│   ├── grammar/
│   ├── reading/
│   └── conversation/
├── n4/
│   ├── grammar/
│   ├── reading/
│   └── conversation/
├── n3/ ...
├── n2/ ...
└── n1/           ← 現有內容搬入
    ├── grammar/
    ├── reading/
    └── conversation/
```

## 實作順序

1. 建立 `grammar_points.py` 集中管理各級文法點
2. 重構 question_bank_service 支援多級別目錄
3. 修改後端 API 接受 level 參數
4. 修改前端加入級別選擇
5. 搬移現有 N1 題庫到 n1/ 子目錄
6. 生成 N5-N4-N3-N2 題庫內容
7. 資料庫 migration（加 level 欄位）

## 測試計畫

1. 選 N5 → 確認出題難度符合 N5
2. 選 N1 → 確認現有行為不變
3. 切換級別 → 確認進度分開追蹤
4. 無 API → 確認各級別 fallback 正常
5. /api/status → 確認各級別題庫數量

## Checklist

- [x] grammar_points.py 各級文法點
- [x] question_bank_service 多級別
- [x] 後端 API level 參數
- [x] 前端級別選擇器
- [x] 搬移 N1 題庫
- [x] 生成 N5-N2 題庫
- [x] 資料庫 migration
- [x] 測試全級別
