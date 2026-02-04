from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import re

from ..services.claude_service import chat_with_claude, get_weak_grammar_points
from ..services.learning_service import (
    get_grammar_mastery_data,
    save_learning_record,
    get_weak_areas
)
from ..services.tts_service import parse_for_tts

router = APIRouter(prefix='/api/chat', tags=['chat'])


class ChatRequest(BaseModel):
    mode: str  # grammar, reading, conversation
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


@router.post('', response_model=ChatResponse)
async def chat(request: ChatRequest):
    """主要對話端點"""
    if request.mode not in ['grammar', 'reading', 'conversation']:
        raise HTTPException(status_code=400, detail='無效的練習模式')

    # 取得用戶掌握度數據
    mastery_data = get_grammar_mastery_data()
    weak_points = get_weak_grammar_points(mastery_data)

    # 準備對話歷史
    messages = request.conversation_history.copy()
    messages.append({'role': 'user', 'content': request.message})

    # 呼叫 Claude
    response_text = await chat_with_claude(
        messages=messages,
        mode=request.mode,
        mastery_data=mastery_data,
        weak_points=weak_points
    )

    # 解析回覆
    parsed = parse_json_response(response_text)

    # 解析 TTS 格式
    tts_segments = parse_for_tts(response_text, request.mode)

    return ChatResponse(
        response=response_text,
        parsed_response=parsed,
        mode=request.mode,
        tts_segments=tts_segments
    )


class RecordAnswerRequest(BaseModel):
    mode: str
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
