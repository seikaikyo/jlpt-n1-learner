from datetime import datetime
from sqlmodel import Session, select, and_
from ..models.database import LearningRecord, GrammarMastery, ReadingProgress, engine


def get_grammar_mastery_data(level: str = 'n1') -> dict[str, float]:
    """取得指定級別的文法掌握度"""
    with Session(engine) as session:
        stmt = select(GrammarMastery).where(GrammarMastery.level == level)
        results = session.exec(stmt).all()
        return {r.grammar_point: r.mastery_level for r in results}


def update_grammar_mastery(grammar_point: str, is_correct: bool, level: str = 'n1') -> float:
    """更新文法掌握度"""
    with Session(engine) as session:
        stmt = select(GrammarMastery).where(
            and_(
                GrammarMastery.grammar_point == grammar_point,
                GrammarMastery.level == level,
            )
        )
        mastery = session.exec(stmt).first()

        if not mastery:
            mastery = GrammarMastery(
                grammar_point=grammar_point,
                level=level,
                correct_count=1 if is_correct else 0,
                total_count=1
            )
            session.add(mastery)
        else:
            mastery.total_count += 1
            if is_correct:
                mastery.correct_count += 1
            mastery.last_practiced = datetime.now()

        mastery.mastery_level = mastery.correct_count / mastery.total_count
        session.commit()
        session.refresh(mastery)

        return mastery.mastery_level


def save_learning_record(
    mode: str,
    question: str,
    user_answer: str,
    is_correct: bool,
    level: str = 'n1',
    grammar_point: str = None,
    explanation: str = None
) -> LearningRecord:
    """儲存學習紀錄"""
    with Session(engine) as session:
        record = LearningRecord(
            mode=mode,
            level=level,
            question=question,
            user_answer=user_answer,
            is_correct=is_correct,
            grammar_point=grammar_point,
            explanation=explanation
        )
        session.add(record)
        session.commit()
        session.refresh(record)

        if grammar_point:
            update_grammar_mastery(grammar_point, is_correct, level=level)

        return record


def get_learning_stats(level: str | None = None) -> dict:
    """取得學習統計（可按級別過濾）"""
    with Session(engine) as session:
        stmt = select(LearningRecord)
        if level:
            stmt = stmt.where(LearningRecord.level == level)
        total_records = session.exec(stmt).all()

        stats = {
            'total_practices': len(total_records),
            'by_mode': {},
            'grammar_mastery': {},
            'recent_records': []
        }

        for mode in ['grammar', 'reading', 'vocabulary', 'conversation']:
            mode_records = [r for r in total_records if r.mode == mode]
            correct = sum(1 for r in mode_records if r.is_correct)
            stats['by_mode'][mode] = {
                'total': len(mode_records),
                'correct': correct,
                'accuracy': correct / len(mode_records) if mode_records else 0
            }

        mastery_stmt = select(GrammarMastery).order_by(
            GrammarMastery.mastery_level
        ).limit(10)
        if level:
            mastery_stmt = mastery_stmt.where(GrammarMastery.level == level)
        masteries = session.exec(mastery_stmt).all()
        stats['grammar_mastery'] = {
            m.grammar_point: {
                'level': m.mastery_level,
                'practiced': m.total_count
            } for m in masteries
        }

        recent_stmt = select(LearningRecord).order_by(
            LearningRecord.created_at.desc()
        ).limit(10)
        if level:
            recent_stmt = recent_stmt.where(LearningRecord.level == level)
        recent = session.exec(recent_stmt).all()
        stats['recent_records'] = [
            {
                'mode': r.mode,
                'level': r.level,
                'question': r.question[:50] + '...' if len(r.question) > 50 else r.question,
                'is_correct': r.is_correct,
                'grammar_point': r.grammar_point,
                'created_at': r.created_at.isoformat()
            } for r in recent
        ]

        return stats


def get_weak_areas(level: str | None = None) -> list[str]:
    """識別弱項領域"""
    stats = get_learning_stats(level=level)
    weak = []

    for mode, data in stats['by_mode'].items():
        if data['total'] >= 5 and data['accuracy'] < 0.6:
            weak.append(mode)

    for grammar, data in stats['grammar_mastery'].items():
        if data['level'] < 0.5:
            weak.append(f"文法：{grammar}")

    return weak if weak else ['尚未識別（練習次數不足）']
