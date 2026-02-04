from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session
from pathlib import Path

# 資料庫路徑
DB_PATH = Path(__file__).parent.parent.parent.parent / 'data' / 'learning.db'
DATABASE_URL = f'sqlite:///{DB_PATH}'

engine = create_engine(DATABASE_URL, echo=False)


class LearningRecord(SQLModel, table=True):
    """學習紀錄"""
    __tablename__ = 'learning_records'

    id: Optional[int] = Field(default=None, primary_key=True)
    mode: str = Field(index=True)  # grammar, reading, vocabulary, conversation
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
    grammar_point: str = Field(unique=True, index=True)
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


def init_db():
    """初始化資料庫"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)


def get_session():
    """取得資料庫 session"""
    with Session(engine) as session:
        yield session
