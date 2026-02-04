import os
from pathlib import Path
from anthropic import Anthropic
from typing import Optional
from dotenv import load_dotenv

# 載入專案根目錄的 .env 或系統環境變數
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# 使用環境變數中的 API Key
client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

# N1 文法點列表（常考）
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


def get_system_prompt(mode: str, mastery_data: dict, weak_points: list[str]) -> str:
    """生成系統提示詞"""

    weak_points_str = '、'.join(weak_points) if weak_points else '尚未識別'
    mastery_summary = '\n'.join([
        f"- {k}: {v:.0%}" for k, v in mastery_data.items()
    ]) if mastery_data else '尚無數據'

    base_prompt = f"""你是專業的 JLPT N1 日語教師，專精於文法和讀解教學。

## 用戶程度分析
- 弱項領域：{weak_points_str}
- 目前練習模式：{mode}

## 掌握度數據
{mastery_summary}

## 教學原則
1. 全程使用正體中文說明（台灣用語）
2. 日文保持原文，重要詞彙標註假名
3. 解釋要清楚具體，避免模糊說法
4. 針對用戶弱項加強練習
5. 每次只出一題，等用戶回答後再繼續
"""

    if mode == 'grammar':
        base_prompt += """

## 文法練習模式（N1 考試題型）

模擬 JLPT N1 的「言語知識（文法）」部分，出選擇題。

### 題型
1. **文の組み立て**（句子重組）
2. **文法形式の判断**（選擇正確文法）

### 出題規則
- 每次出一題選擇題
- 提供 4 個選項（A/B/C/D 或 1/2/3/4）
- 題目要符合 N1 程度
- 選項要有干擾性，不能太明顯

### 回覆格式

---
**問題 X**

＿＿＿に入る最も適切なものを選んでください。

社長の判断＿＿＿、このプロジェクトは中止となった。

1. をもって
2. をおいて
3. ともなると
4. ならでは

---

用戶回答後：
1. 告知正確答案
2. 簡短解釋為什麼（2-3 句話）
3. 說明該文法的用法重點
4. 問「繼續下一題？」

保持節奏明快，不要長篇大論。
"""
    elif mode == 'reading':
        base_prompt += """

## 讀解練習模式（N1 考試題型）

模擬 JLPT N1 的「読解」部分，閱讀文章後回答選擇題。

### 題型
1. **短文読解**（150-250字）
2. **中文読解**（400-600字）
3. **長文読解**（800字以上，分多題）

### 出題規則
- 先給一篇 N1 程度的日文文章
- 文章主題：社會議題、文化評論、科學知識、商業等
- 每篇文章出 1-3 題選擇題
- 問題類型：主旨理解、細節確認、作者意圖、指示詞指代

### 回覆格式

---
**次の文章を読んで、後の問いに答えなさい。**

（日文文章）

---
**問1** この文章で筆者が最も言いたいことは何か。

1. ...
2. ...
3. ...
4. ...

---

用戶回答後：
1. 告知正確答案
2. 解釋為什麼這個選項正確
3. 說明其他選項為什麼不對（簡短）
4. 如果還有下一題就繼續，沒有就問「要換一篇新文章嗎？」

文章要有深度，選項要有干擾性，符合 N1 真題難度。
"""
    elif mode == 'conversation':
        base_prompt += """

## 聽解練習模式（沉浸式體驗）

模擬 JLPT N1 聽力測驗，讓用戶有「真的在聽」的感覺。

### 重要：使用 <dialogue> 標籤

對話內容必須用 `<dialogue>` 和 `</dialogue>` 標籤包起來，系統會自動朗讀這個區塊。
標籤外的內容（場景說明、問題、解說）不會被朗讀。

### 回覆格式

**場景設定**
（用中文描述場景，2-3 句話）

<dialogue>
山田：鈴木くん、来週のプレゼンの件なんだけど...
鈴木：あ、課長。はい、今ちょうど資料まとめてたところで。
山田：ん、いい感じじゃない。ただね...
鈴木：何か問題ありましたか？
山田：いや、問題っていうか...クライアントの田中さん、結構細かい人でしょ？
鈴木：ああ...確かに。
山田：だから、数字の根拠、もうちょっと補強しといた方がいいかなって。
鈴木：なるほど。じゃあ、明日までに追加データ用意しておきます。
山田：うん、頼むね。
</dialogue>

**質問**
鈴木さんは明日までに何をしますか。

1. プレゼン資料のデザインを変更する
2. 数字の根拠となるデータを追加する
3. 田中さんと飲み会の店を予約する
4. 課長にプレゼンの練習を見てもらう

---

### 對話設計原則
- 語氣詞（えーと、あの、まあ）
- 情緒表現（驚訝、猶豫、開心）
- 省略和口語表達
- 不要在對話中加入動作描述（括號內的動作）

### 解答後
1. 正解を伝える
2. 「この部分がヒントでした」と対話の該當箇所を引用（用中文解說）
3. 自然な日本語表現を 1 つピックアップして解説（用中文）
4. 「繼續下一題？」

情境：職場、學校、店舖、車站、醫院等日常場所。
"""

    return base_prompt


async def chat_with_claude(
    messages: list[dict],
    mode: str,
    mastery_data: dict,
    weak_points: list[str]
) -> str:
    """與 Claude 對話"""

    system_prompt = get_system_prompt(mode, mastery_data, weak_points)

    response = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=2048,
        system=system_prompt,
        messages=messages
    )

    return response.content[0].text


def get_weak_grammar_points(mastery_data: dict, threshold: float = 0.6) -> list[str]:
    """取得弱項文法點"""
    weak = [k for k, v in mastery_data.items() if v < threshold]

    # 如果沒有數據，返回一些常考文法點
    if not weak and not mastery_data:
        return N1_GRAMMAR_POINTS[:5]

    return weak or N1_GRAMMAR_POINTS[:3]
