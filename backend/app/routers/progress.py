from fastapi import APIRouter
from ..services.learning_service import get_learning_stats, get_weak_areas

router = APIRouter(prefix='/api/progress', tags=['progress'])


@router.get('')
async def get_progress():
    """取得學習進度"""
    stats = get_learning_stats()
    weak_areas = get_weak_areas()

    return {
        'success': True,
        'data': {
            'stats': stats,
            'weak_areas': weak_areas
        }
    }


@router.get('/summary')
async def get_summary():
    """取得簡要統計"""
    stats = get_learning_stats()

    # 計算總正確率
    total_correct = sum(d['correct'] for d in stats['by_mode'].values())
    total_count = sum(d['total'] for d in stats['by_mode'].values())

    return {
        'success': True,
        'data': {
            'total_practices': stats['total_practices'],
            'overall_accuracy': total_correct / total_count if total_count > 0 else 0,
            'by_mode': {
                mode: {
                    'count': data['total'],
                    'accuracy': data['accuracy']
                }
                for mode, data in stats['by_mode'].items()
            },
            'weak_grammar_count': len([
                g for g, d in stats['grammar_mastery'].items()
                if d['level'] < 0.6
            ])
        }
    }
