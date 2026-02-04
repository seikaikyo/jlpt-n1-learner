from datetime import datetime
from sqlmodel import Session, select
from ..models.database import LearningRecord, GrammarMastery, ReadingProgress, engine


def get_grammar_mastery_data() -> dict[str, float]:
    """取得所有文法掌握度"""
    with Session(engine) as session:
        stmt = select(GrammarMastery)
        results = session.exec(stmt).all()
        return {r.grammar_point: r.mastery_level for r in results}


def update_grammar_mastery(grammar_point: str, is_correct: bool) -> float:
    """更新文法掌握度"""
    with Session(engine) as session:
        stmt = select(GrammarMastery).where(
            GrammarMastery.grammar_point == grammar_point
        )
        mastery = session.exec(stmt).first()

        if not mastery:
            mastery = GrammarMastery(
                grammar_point=grammar_point,
                correct_count=1 if is_correct else 0,
                total_count=1
            )
            session.add(mastery)
        else:
            mastery.total_count += 1
            if is_correct:
                mastery.correct_count += 1
            mastery.last_practiced = datetime.now()

        # 計算掌握度（加權平均，最近的更重要）
        mastery.mastery_level = mastery.correct_count / mastery.total_count
        session.commit()
        session.refresh(mastery)

        return mastery.mastery_level


def save_learning_record(
    mode: str,
    question: str,
    user_answer: str,
    is_correct: bool,
    grammar_point: str = None,
    explanation: str = None
) -> LearningRecord:
    """儲存學習紀錄"""
    with Session(engine) as session:
        record = LearningRecord(
            mode=mode,
            question=question,
            user_answer=user_answer,
            is_correct=is_correct,
            grammar_point=grammar_point,
            explanation=explanation
        )
        session.add(record)
        session.commit()
        session.refresh(record)

        # 如果有文法點，同時更新掌握度
        if grammar_point:
            update_grammar_mastery(grammar_point, is_correct)

        return record


def get_learning_stats() -> dict:
    """取得學習統計"""
    with Session(engine) as session:
        # 總練習次數
        total_stmt = select(LearningRecord)
        total_records = session.exec(total_stmt).all()

        # 各模式統計
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

        # 文法掌握度
        mastery_stmt = select(GrammarMastery).order_by(
            GrammarMastery.mastery_level
        ).limit(10)
        masteries = session.exec(mastery_stmt).all()
        stats['grammar_mastery'] = {
            m.grammar_point: {
                'level': m.mastery_level,
                'practiced': m.total_count
            } for m in masteries
        }

        # 最近紀錄
        recent_stmt = select(LearningRecord).order_by(
            LearningRecord.created_at.desc()
        ).limit(10)
        recent = session.exec(recent_stmt).all()
        stats['recent_records'] = [
            {
                'mode': r.mode,
                'question': r.question[:50] + '...' if len(r.question) > 50 else r.question,
                'is_correct': r.is_correct,
                'grammar_point': r.grammar_point,
                'created_at': r.created_at.isoformat()
            } for r in recent
        ]

        return stats


def get_weak_areas() -> list[str]:
    """識別弱項領域"""
    stats = get_learning_stats()
    weak = []

    for mode, data in stats['by_mode'].items():
        if data['total'] >= 5 and data['accuracy'] < 0.6:
            weak.append(mode)

    # 加入掌握度低的文法點
    for grammar, data in stats['grammar_mastery'].items():
        if data['level'] < 0.5:
            weak.append(f"文法：{grammar}")

    return weak if weak else ['尚未識別（練習次數不足）']
