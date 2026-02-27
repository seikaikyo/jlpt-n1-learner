import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# 載入環境變數
load_dotenv()

from .models.database import init_db
from .routers import chat, progress
from .services.api_health import api_health
from .services.question_bank_service import question_bank

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時初始化資料庫
    init_db()

    # 載入題庫
    question_bank.load()
    logger.info('題庫狀態: %s', question_bank.get_status())

    # 設定 API key 狀態
    api_health.set_has_api_key(bool(os.environ.get('ANTHROPIC_API_KEY')))

    yield


app = FastAPI(
    title='JLPT 學習系統',
    description='AI 驅動的 JLPT N5-N1 適應性學習系統',
    version='2.0.0',
    lifespan=lifespan
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5172', 'http://127.0.0.1:5172'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# 註冊路由
app.include_router(chat.router)
app.include_router(progress.router)


@app.get('/')
async def root():
    return {
        'name': 'JLPT 學習系統',
        'version': '2.0.0',
        'endpoints': [
            '/api/chat',
            '/api/progress'
        ]
    }


@app.get('/health')
async def health():
    return {'status': 'ok'}


@app.get('/api/status')
async def status():
    """系統狀態（API + 題庫）"""
    return {
        'api': api_health.get_status(),
        'question_bank': question_bank.get_status(),
    }
