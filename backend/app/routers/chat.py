from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import json
import re

from ..services.claude_service import (
    chat_with_claude,
    get_weak_grammar_points,
    ClaudeAPIError,
)
from ..services.learning_service import (
    get_grammar_mastery_data,
    save_learning_record,
    get_weak_areas
)
from ..services.tts_service import parse_for_tts
from ..services.api_health import api_health
from ..services.question_bank_service import question_bank

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/chat', tags=['chat'])


class ChatRequest(BaseModel):
    mode: str  # grammar, reading, conversation
    level: str = 'n1'  # n5, n4, n3, n2, n1
    message: str
    conversation_history: list[dict] = []


class TTSSegmentModel(BaseModel):
    text: str
    speaker: Optional[str] = None
    lang: str = 'ja'
    pause_after: str = 'none'
    pause_before: Optional[str] = None
    voice: str = 'female'  # female 或 male


class ChatResponse(BaseModel):
    response: str
    parsed_response: Optional[dict] = None
    mode: str
    level: str = 'n1'
    tts_segments: list[TTSSegmentModel] = []


def parse_json_response(text: str) -> Optional[dict]:
    """嘗試從回覆中解析 JSON"""
    # 尋找 JSON 區塊
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # 嘗試直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    return None


def _is_requesting_new_question(message: str) -> bool:
    """判斷用戶是要新題還是在回答題目"""
    new_question_keywords = [
        '開始', '下一題', '繼續', '出題', '新題', '再來',
        '練習', '文法', '讀解', '聽解', '會話',
        'start', 'next', 'continue', 'new',
    ]
    msg = message.strip().lower()
    # 如果訊息很短且是數字（1-4），視為回答
    if msg in ('1', '2', '3', '4', 'a', 'b', 'c', 'd'):
        return False
    return any(kw in msg for kw in new_question_keywords) or len(msg) <= 5


def _get_fallback_response(request_mode: str, request_level: str, message: str, mastery_data: dict, weak_points: list[str]) -> str:
    """從題庫取得 fallback 回應"""
    if not question_bank.has_questions(request_mode, request_level):
        return '目前題庫尚未建立，且 AI 服務暫時無法使用。請稍後再試。'

    if _is_requesting_new_question(message):
        question = question_bank.get_question(
            mode=request_mode,
            level=request_level,
            mastery_data=mastery_data,
            weak_points=weak_points,
        )
        if question:
            return question.get('full_response', '題庫讀取錯誤')
        return '題庫已用完，請稍後再試。'
    else:
        return (
            '目前為離線題庫模式，無法即時批改你的回答。\n\n'
            '請對照上方題目的選項自行核對答案，或輸入「下一題」繼續練習。'
        )


@router.post('', response_model=ChatResponse)
async def chat(request: ChatRequest, raw_request: Request):
    """主要對話端點（含 fallback 機制）"""
    if request.mode not in ['grammar', 'reading', 'conversation']:
        raise HTTPException(status_code=400, detail='無效的練習模式')

    if request.level not in ['n5', 'n4', 'n3', 'n2', 'n1']:
        raise HTTPException(status_code=400, detail='無效的級別')

    # 取得用戶掌握度數據
    mastery_data = get_grammar_mastery_data(level=request.level)
    weak_points = get_weak_grammar_points(mastery_data, level=request.level)

    # 準備對話歷史
    messages = request.conversation_history.copy()
    messages.append({'role': 'user', 'content': request.message})

    response_text = None

    # 從 header 取得用戶自訂 API key
    request_api_key = raw_request.headers.get('X-Api-Key')
    has_key = bool(request_api_key) or api_health.should_try_api

    # 嘗試 Claude API
    if has_key:
        try:
            response_text = await chat_with_claude(
                messages=messages,
                mode=request.mode,
                level=request.level,
                mastery_data=mastery_data,
                weak_points=weak_points,
                api_key=request_api_key,
            )
            if not request_api_key:
                api_health.mark_success()
        except ClaudeAPIError as e:
            logger.warning('Claude API 失敗，切換到題庫模式: %s', e)
            if not request_api_key:
                api_health.mark_failure()

    # Fallback 到題庫
    if response_text is None:
        response_text = _get_fallback_response(
            request.mode, request.level, request.message, mastery_data, weak_points
        )

    # 解析回覆
    parsed = parse_json_response(response_text)

    # 解析 TTS 格式
    tts_segments = parse_for_tts(response_text, request.mode)

    return ChatResponse(
        response=response_text,
        parsed_response=parsed,
        mode=request.mode,
        level=request.level,
        tts_segments=tts_segments
    )


class RecordAnswerRequest(BaseModel):
    mode: str
    level: str = 'n1'
    question: str
    user_answer: str
    is_correct: bool
    grammar_point: Optional[str] = None
    explanation: Optional[str] = None


@router.post('/record')
async def record_answer(request: RecordAnswerRequest):
    """記錄用戶答案"""
    record = save_learning_record(
        mode=request.mode,
        level=request.level,
        question=request.question,
        user_answer=request.user_answer,
        is_correct=request.is_correct,
        grammar_point=request.grammar_point,
        explanation=request.explanation
    )

    return {
        'success': True,
        'record_id': record.id
    }
