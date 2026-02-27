---
title: N2 題庫 JSON 檔案生成
type: feature
status: completed
created: 2026-02-27
---

# N2 題庫 JSON 檔案生成

## 變更內容
新增 JLPT N2 級別題庫，包含 30 個文法點的練習題、讀解題及會話題。

## 影響範圍
- `backend/data/question_bank/n2/grammar/n2_grammar.json` (新增 90 題)
- `backend/data/question_bank/n2/reading/short.json` (新增 5 篇短文)
- `backend/data/question_bank/n2/reading/medium.json` (新增 3 篇中文)
- `backend/data/question_bank/n2/reading/long.json` (新增 2 篇長文)
- `backend/data/question_bank/n2/conversation/daily.json` (新增 5 段對話)

## 文法點清單 (30 個)
〜に伴い、〜に応じて、〜に基づいて、〜を踏まえて、〜にかけて、〜にわたって、〜を通じて、〜に沿って、〜に限り、〜に限らず、〜をはじめ、〜を問わず、〜もかまわず、〜にもかかわらず、〜反面、〜一方で、〜のみならず、〜どころか、〜からといって、〜からには、〜上で、〜上は、〜次第、〜以上は、〜てたまらない、〜てならない、〜てしかたがない、〜おそれがある、〜つつある、〜ものの

## 測試計畫
1. JSON 格式正確性驗證 (python -m json.tool)
2. 題目 ID 不重複
3. correct_answer 與 options 對應正確
4. 日文用語符合 N2 程度

## Checklist
- [x] grammar 90 題
- [x] reading short 5 篇
- [x] reading medium 3 篇
- [x] reading long 2 篇
- [x] conversation 5 段
- [x] JSON 格式驗證通過
