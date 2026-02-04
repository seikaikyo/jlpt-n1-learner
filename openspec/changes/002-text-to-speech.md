---
title: 日文語音朗讀功能
type: feature
status: in-progress
created: 2026-02-04
---

# 日文語音朗讀功能

## 變更內容

使用 Web Speech API 為 AI 回覆加入日文語音朗讀功能，讓用戶可以聽到日文發音。

## 功能規格

- 每則 AI 回覆旁邊顯示播放按鈕
- 點擊按鈕朗讀該則訊息的日文內容
- 播放中顯示停止按鈕，可中斷朗讀
- 使用日文語音 (ja-JP)

## 影響範圍

- `frontend/src/components/ChatInterface.vue` - 加入播放按鈕
- `frontend/src/composables/useSpeech.ts` - 新增語音 composable

## 技術方案

使用瀏覽器內建 Web Speech API (SpeechSynthesis)：
- 免費、零後端成本
- macOS/iOS 日文語音品質可接受
- 不需額外安裝套件

## 測試計畫

1. 點擊播放按鈕，確認日文正確朗讀
2. 播放中點擊停止，確認可中斷
3. 連續點擊不同訊息，確認切換正常

## Checklist

- [x] 建立 useSpeech composable
- [x] ChatInterface 加入播放按鈕
- [ ] 測試各瀏覽器相容性
