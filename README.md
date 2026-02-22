# JLPT N1 學習系統

Claude AI 驅動的 JLPT N1 自適應學習平台，追蹤弱點文法並個人化出題。

## 功能

- **文法練習**: 25+ 個 N1 文法點，AI 自動針對弱項出題
- **讀解練習**: 短文 (150-250 字) 到長文 (800+ 字)，主旨/細節/作者意圖題
- **聽解練習**: 模擬 N1 聽力，對話自動男女聲切換
- **語音朗讀**: Web Speech API，支援語速 0.5x-1.5x 調整
- **自適應學習**: 追蹤每個文法點的精熟度，正確率 < 60% 自動加強
- **學習進度**: 總練習數、正確率、各模式統計、弱項識別

## 技術棧

| 層級 | 技術 |
|------|------|
| 前端 | Vue 3 + TypeScript + PrimeVue (Aura) |
| 後端 | FastAPI + SQLModel + SQLite |
| AI | Claude API (自適應出題 + 即時解說) |
| 語音 | Web Speech API (日文男女聲 + 中文) |
| 部署 | Vercel (前端) |

## API

| 端點 | 功能 |
|------|------|
| `POST /api/chat` | 傳送訊息，回傳 AI 回應 + TTS 語音片段 |
| `POST /api/chat/record` | 記錄答題正確性 |
| `GET /api/progress` | 學習進度 + 弱項分析 |
| `GET /api/progress/summary` | 快速摘要 |

## 開發

```bash
# 前端 (port 5172)
cd frontend && npm install && npm run dev

# 後端 (port 8002)
cd backend && source venv/bin/activate && uvicorn app.main:app --port 8002
```

## N1 文法涵蓋

ざるを得ない、ないものでもない、ともなると、ならでは、をもって、をおいて、ともなく、てやまない、に即して、を禁じ得ない、べく、んがため、たりとも、といえども 等 25+ 項
