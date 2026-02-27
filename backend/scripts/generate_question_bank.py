#!/usr/bin/env python3
"""JLPT N1 題庫生成器

用 Claude API 批次生成題目，存成 JSON。

用法：
  python scripts/generate_question_bank.py                  # 生成全部
  python scripts/generate_question_bank.py --mode grammar   # 只生成文法
  python scripts/generate_question_bank.py --mode reading   # 只生成讀解
  python scripts/generate_question_bank.py --mode conversation  # 只生成聽解
  python scripts/generate_question_bank.py --mode grammar --count 5  # 每文法點 5 題
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# 加入 backend 到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from anthropic import Anthropic

# 載入環境變數
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
DATA_DIR = Path(__file__).parent.parent / 'data' / 'question_bank'

# N1 文法點（與 claude_service.py 同步）
N1_GRAMMAR_POINTS = [
    '〜ざるを得ない', '〜ないものでもない', '〜ともなると', '〜ならでは',
    '〜をもって', '〜をおいて', '〜ともなく', '〜てやまない',
    '〜に即して', '〜を禁じ得ない', '〜べく', '〜んがため',
    '〜たりとも', '〜といえども', '〜ものを', '〜ばこそ',
    '〜までもない', '〜にもまして', '〜如何', '〜極まりない',
    '〜が早いか', '〜や否や', '〜なり', '〜そばから',
    '〜ずにはおかない', '〜ないではおかない', '〜を余儀なくされる',
    '〜かたがた', '〜かたわら', '〜ながらも', '〜つつも',
]

READING_TYPES = [
    ('short', 15, '150-250字短文'),
    ('medium', 10, '400-600字中文'),
    ('long', 5, '800字以上長文'),
]

CONVERSATION_SCENES = [
    ('workplace', 15, '職場'),
    ('daily', 15, '日常生活'),
    ('school', 15, '學校'),
]


def generate_grammar_questions(grammar_point: str, count: int = 20) -> list[dict]:
    """為單一文法點生成指定數量的題目"""
    clean_name = grammar_point.lstrip('〜').lstrip('~')
    prompt = f"""你是 JLPT N1 出題專家。請為文法點「{grammar_point}」生成 {count} 題選擇題。

每題必須包含：
1. 一個含有空格的句子
2. 4 個選項（其中 1 個正確）
3. 正確答案的編號 (1-4)
4. 完整的出題文字（模仿 JLPT 考試風格）
5. 答對時的解說文字

請用以下 JSON 格式回覆（不要加 markdown code block）：

[
  {{
    "id": "grammar_{clean_name}_001",
    "grammar_point": "{grammar_point}",
    "correct_answer": 1,
    "options": ["選項1", "選項2", "選項3", "選項4"],
    "full_response": "---\\n**問題 1**\\n\\n＿＿＿に入る最も適切なものを選んでください。\\n\\n（日文句子，含空格）\\n\\n1. 選項1\\n2. 選項2\\n3. 選項3\\n4. 選項4\\n\\n---",
    "answer_response": "正解は **1** です。\\n\\n（解說：2-3 句話解釋正確用法）\\n\\n**{grammar_point}** の用法：（簡短用法說明）\\n\\n繼續下一題？"
  }}
]

注意：
- id 的流水號從 001 開始
- full_response 格式要完全模仿 JLPT N1 出題教師的風格
- answer_response 要用正體中文解說，日文原文保留
- 選項要有干擾性，包含其他 N1 文法點
- 每題的句子場景不同（商業、學術、日常等）
- 一次回覆全部 {count} 題"""

    response = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=4096 * 2,
        system='你是 JLPT N1 出題專家。只輸出 JSON，不要其他文字。',
        messages=[{'role': 'user', 'content': prompt}],
    )

    text = response.content[0].text.strip()
    # 清理可能的 markdown code block
    if text.startswith('```'):
        text = text.split('\n', 1)[1]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()

    try:
        questions = json.loads(text)
        print(f'  {grammar_point}: {len(questions)} 題')
        return questions
    except json.JSONDecodeError as e:
        print(f'  {grammar_point}: JSON 解析失敗 - {e}')
        # 嘗試修復常見問題
        try:
            # 找到 JSON 陣列
            start = text.index('[')
            end = text.rindex(']') + 1
            questions = json.loads(text[start:end])
            print(f'  {grammar_point}: 修復後取得 {len(questions)} 題')
            return questions
        except (ValueError, json.JSONDecodeError):
            print(f'  {grammar_point}: 修復失敗，跳過')
            return []


def generate_reading_questions(reading_type: str, count: int, desc: str) -> list[dict]:
    """生成讀解題"""
    prompt = f"""你是 JLPT N1 出題專家。請生成 {count} 篇 {desc}讀解題。

每篇必須包含：
1. 一篇 N1 程度的日文文章
2. 1-2 題選擇題
3. 正確答案

請用以下 JSON 格式回覆（不要加 markdown code block）：

[
  {{
    "id": "reading_{reading_type}_001",
    "reading_type": "{reading_type}",
    "correct_answer": 1,
    "options": ["選項1", "選項2", "選項3", "選項4"],
    "full_response": "---\\n**次の文章を読んで、後の問いに答えなさい。**\\n\\n（日文文章）\\n\\n---\\n**問1** 問題文\\n\\n1. 選項1\\n2. 選項2\\n3. 選項3\\n4. 選項4\\n\\n---",
    "answer_response": "正解は **1** です。\\n\\n（解說）\\n\\n要換一篇新文章嗎？"
  }}
]

注意：
- 文章主題多樣：社會議題、文化評論、科學知識、商業等
- 選項要有干擾性
- answer_response 用正體中文解說
- id 流水號從 001 開始"""

    response = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=4096 * 3,
        system='你是 JLPT N1 出題專家。只輸出 JSON，不要其他文字。',
        messages=[{'role': 'user', 'content': prompt}],
    )

    text = response.content[0].text.strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[1]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()

    try:
        questions = json.loads(text)
        print(f'  {reading_type}: {len(questions)} 篇')
        return questions
    except json.JSONDecodeError:
        try:
            start = text.index('[')
            end = text.rindex(']') + 1
            questions = json.loads(text[start:end])
            print(f'  {reading_type}: 修復後取得 {len(questions)} 篇')
            return questions
        except (ValueError, json.JSONDecodeError):
            print(f'  {reading_type}: JSON 解析失敗，跳過')
            return []


def generate_conversation_questions(scene: str, count: int, desc: str) -> list[dict]:
    """生成聽解/會話題"""
    prompt = f"""你是 JLPT N1 出題專家。請生成 {count} 段{desc}場景的聽解題。

每題必須包含：
1. 場景描述（中文）
2. 對話內容（用 <dialogue> 標籤包裹）
3. 1 題選擇題
4. 正確答案

對話設計原則：
- 使用語氣詞（えーと、あの、まあ）
- 情緒表現（驚訝、猶豫、開心）
- 省略和口語表達
- 不加動作描述

請用以下 JSON 格式回覆（不要加 markdown code block）：

[
  {{
    "id": "conversation_{scene}_001",
    "scene": "{scene}",
    "correct_answer": 2,
    "options": ["選項1", "選項2", "選項3", "選項4"],
    "full_response": "**場景設定**\\n（場景描述）\\n\\n<dialogue>\\n人物A：對話...\\n人物B：對話...\\n</dialogue>\\n\\n**質問**\\n問題文\\n\\n1. 選項1\\n2. 選項2\\n3. 選項3\\n4. 選項4\\n\\n---",
    "answer_response": "正解は **2** です。\\n\\n（解說：提示在哪裡）\\n\\n**表現ポイント**：（挑一個自然日語表現解說）\\n\\n繼續下一題？"
  }}
]

注意：
- 場景: {desc}（{scene}）相關場景
- answer_response 用正體中文解說
- id 流水號從 001 開始"""

    response = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=4096 * 3,
        system='你是 JLPT N1 出題專家。只輸出 JSON，不要其他文字。',
        messages=[{'role': 'user', 'content': prompt}],
    )

    text = response.content[0].text.strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[1]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()

    try:
        questions = json.loads(text)
        print(f'  {scene}: {len(questions)} 段')
        return questions
    except json.JSONDecodeError:
        try:
            start = text.index('[')
            end = text.rindex(']') + 1
            questions = json.loads(text[start:end])
            print(f'  {scene}: 修復後取得 {len(questions)} 段')
            return questions
        except (ValueError, json.JSONDecodeError):
            print(f'  {scene}: JSON 解析失敗，跳過')
            return []


def run_grammar(count_per_point: int):
    """生成文法題庫"""
    grammar_dir = DATA_DIR / 'grammar'
    grammar_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    for i, gp in enumerate(N1_GRAMMAR_POINTS):
        clean_name = gp.lstrip('〜').lstrip('~')
        out_file = grammar_dir / f'{clean_name}.json'

        # 跳過已存在的檔案
        if out_file.exists():
            existing = json.loads(out_file.read_text(encoding='utf-8'))
            count = len(existing) if isinstance(existing, list) else 0
            print(f'  [{i+1}/{len(N1_GRAMMAR_POINTS)}] {gp}: 已存在 ({count} 題)，跳過')
            total += count
            continue

        print(f'  [{i+1}/{len(N1_GRAMMAR_POINTS)}] 生成 {gp}...')
        questions = generate_grammar_questions(gp, count_per_point)
        if questions:
            out_file.write_text(
                json.dumps(questions, ensure_ascii=False, indent=2),
                encoding='utf-8',
            )
            total += len(questions)

        # 避免 rate limit
        time.sleep(1)

    print(f'文法題庫完成: {total} 題')
    return total


def run_reading():
    """生成讀解題庫"""
    reading_dir = DATA_DIR / 'reading'
    reading_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    for reading_type, count, desc in READING_TYPES:
        out_file = reading_dir / f'{reading_type}.json'

        if out_file.exists():
            existing = json.loads(out_file.read_text(encoding='utf-8'))
            c = len(existing) if isinstance(existing, list) else 0
            print(f'  {reading_type}: 已存在 ({c} 篇)，跳過')
            total += c
            continue

        print(f'  生成 {desc} ({reading_type})...')
        questions = generate_reading_questions(reading_type, count, desc)
        if questions:
            out_file.write_text(
                json.dumps(questions, ensure_ascii=False, indent=2),
                encoding='utf-8',
            )
            total += len(questions)

        time.sleep(1)

    print(f'讀解題庫完成: {total} 篇')
    return total


def run_conversation():
    """生成聽解題庫"""
    conv_dir = DATA_DIR / 'conversation'
    conv_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    for scene, count, desc in CONVERSATION_SCENES:
        out_file = conv_dir / f'{scene}.json'

        if out_file.exists():
            existing = json.loads(out_file.read_text(encoding='utf-8'))
            c = len(existing) if isinstance(existing, list) else 0
            print(f'  {scene}: 已存在 ({c} 段)，跳過')
            total += c
            continue

        print(f'  生成 {desc} ({scene})...')
        questions = generate_conversation_questions(scene, count, desc)
        if questions:
            out_file.write_text(
                json.dumps(questions, ensure_ascii=False, indent=2),
                encoding='utf-8',
            )
            total += len(questions)

        time.sleep(1)

    print(f'聽解題庫完成: {total} 段')
    return total


def save_metadata(stats: dict):
    """儲存統計資訊"""
    from datetime import datetime
    metadata = {
        'generated_at': datetime.now().isoformat(),
        'model': 'claude-sonnet-4-20250514',
        'stats': stats,
    }
    meta_file = DATA_DIR / 'metadata.json'
    meta_file.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print(f'metadata 已寫入: {meta_file}')


def main():
    parser = argparse.ArgumentParser(description='JLPT N1 題庫生成器')
    parser.add_argument(
        '--mode',
        choices=['grammar', 'reading', 'conversation', 'all'],
        default='all',
        help='生成模式 (預設: all)',
    )
    parser.add_argument(
        '--count',
        type=int,
        default=20,
        help='每文法點題數 (預設: 20，僅 grammar 模式)',
    )
    args = parser.parse_args()

    if not os.environ.get('ANTHROPIC_API_KEY'):
        print('錯誤: 未設定 ANTHROPIC_API_KEY')
        sys.exit(1)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    stats = {}

    print('=== JLPT N1 題庫生成器 ===\n')

    if args.mode in ('grammar', 'all'):
        print(f'[文法] 生成 {len(N1_GRAMMAR_POINTS)} 文法點 x {args.count} 題...')
        stats['grammar'] = run_grammar(args.count)
        print()

    if args.mode in ('reading', 'all'):
        print('[讀解] 生成讀解題...')
        stats['reading'] = run_reading()
        print()

    if args.mode in ('conversation', 'all'):
        print('[聽解] 生成聽解題...')
        stats['conversation'] = run_conversation()
        print()

    save_metadata(stats)
    print('\n完成!')


if __name__ == '__main__':
    main()
