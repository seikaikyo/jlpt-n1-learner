import logging
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session, text
from pathlib import Path

logger = logging.getLogger(__name__)

# 資料庫路徑
DB_PATH = Path(__file__).parent.parent.parent.parent / 'data' / 'learning.db'
DATABASE_URL = f'sqlite:///{DB_PATH}'

engine = create_engine(DATABASE_URL, echo=False)


class LearningRecord(SQLModel, table=True):
    """學習紀錄"""
    __tablename__ = 'learning_records'

    id: Optional[int] = Field(default=None, primary_key=True)
    mode: str = Field(index=True)  # grammar, reading, vocabulary, conversation
    level: str = Field(default='n1', index=True)  # n5, n4, n3, n2, n1
    question: str
    user_answer: str
    is_correct: bool
    grammar_point: Optional[str] = Field(default=None, index=True)
    explanation: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class GrammarMastery(SQLModel, table=True):
    """文法掌握度"""
    __tablename__ = 'grammar_mastery'

    id: Optional[int] = Field(default=None, primary_key=True)
    grammar_point: str = Field(index=True)
    level: str = Field(default='n1', index=True)  # n5, n4, n3, n2, n1
    correct_count: int = Field(default=0)
    total_count: int = Field(default=0)
    mastery_level: float = Field(default=0.0)  # 0.0 ~ 1.0
    last_practiced: datetime = Field(default_factory=datetime.now)


class ReadingProgress(SQLModel, table=True):
    """讀解進度"""
    __tablename__ = 'reading_progress'

    id: Optional[int] = Field(default=None, primary_key=True)
    total_passages: int = Field(default=0)
    correct_answers: int = Field(default=0)
    total_questions: int = Field(default=0)
    accuracy_rate: float = Field(default=0.0)
    last_practiced: datetime = Field(default_factory=datetime.now)


def _migrate_add_level_column():
    """為舊資料庫加入 level 欄位（冪等）"""
    with Session(engine) as session:
        for table in ('learning_records', 'grammar_mastery'):
            try:
                session.exec(text(f"SELECT level FROM {table} LIMIT 1"))
            except Exception:
                logger.info('Migration: 為 %s 加入 level 欄位', table)
                session.exec(text(
                    f"ALTER TABLE {table} ADD COLUMN level TEXT NOT NULL DEFAULT 'n1'"
                ))
                session.commit()


def init_db():
    """初始化資料庫"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)
    _migrate_add_level_column()


def get_session():
    """取得資料庫 session"""
    with Session(engine) as session:
        yield session
