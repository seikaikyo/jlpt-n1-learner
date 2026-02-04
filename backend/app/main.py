import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# 載入環境變數
load_dotenv()

from .models.database import init_db
from .routers import chat, progress


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時初始化資料庫
    init_db()
    yield


app = FastAPI(
    title='JLPT N1 學習系統',
    description='AI 驅動的 JLPT N1 適應性學習系統',
    version='1.0.0',
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
        'name': 'JLPT N1 學習系統',
        'version': '1.0.0',
        'endpoints': [
            '/api/chat',
            '/api/progress'
        ]
    }


@app.get('/health')
async def health():
    return {'status': 'ok'}
