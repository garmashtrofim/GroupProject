import pandas as pd
from typing import List, Dict, Optional


def load_and_validate_data(csv_path: str) -> pd.DataFrame:
    """
    Загружает и валидирует данные из CSV-файла
    """
    required_cols = [
        'student_id', 'name', 'group', 'discipline',
        'grade', 'attendance', 'activity_score', 'project_participation'
    ]

    df = pd.read_csv(csv_path)

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Отсутствуют обязательные колонки: {missing_cols}")

    df['grade'] = pd.to_numeric(df['grade'], errors='coerce')
    df['attendance'] = pd.to_numeric(df['attendance'], errors='coerce')
    df['activity_score'] = pd.to_numeric(df['activity_score'], errors='coerce')
    df['project_participation'] = df['project_participation'].astype(bool)

    df = df.dropna(subset=['student_id', 'grade'])

    df = df[(df['grade'] >= 0) & (df['grade'] <= 100)]
    df = df[(df['attendance'] >= 0) & (df['attendance'] <= 100)]
    df = df[(df['activity_score'] >= 0) & (df['activity_score'] <= 100)]

    print(f"✅ Загружено {len(df)} записей")
    return df


def calculate_student_rating(df: pd.DataFrame, weights: Optional[Dict[str, float]] = None) -> pd.DataFrame:
    """
    Рассчитывает рейтинг каждого студента
    """
    if weights is None:
        weights = {
            'grade': 0.4,
            'attendance': 0.25,
            'activity': 0.2,
            'project': 0.15
        }

    avg_grade = df.groupby('student_id')['grade'].mean().rename('avg_grade')
    avg_attendance = df.groupby('student_id')['attendance'].mean().rename('avg_attendance')
    avg_activity = df.groupby('student_id')['activity_score'].mean().rename('avg_activity')
    project_rate = df.groupby('student_id')['project_participation'].mean().rename('project_rate') * 100

    metrics = pd.concat([avg_grade, avg_attendance, avg_activity, project_rate], axis=1).reset_index()

    for col in ['avg_grade', 'avg_attendance', 'avg_activity', 'project_rate']:
        min_val = metrics[col].min()
        max_val = metrics[col].max()
        if max_val - min_val > 0:
            metrics[col] = (metrics[col] - min_val) / (max_val - min_val) * 100
        else:
            metrics[col] = 0.0

    metrics['rating'] = (
            weights['grade'] * metrics['avg_grade'] +
            weights['attendance'] * metrics['avg_attendance'] +
            weights['activity'] * metrics['avg_activity'] +
            weights['project'] * metrics['project_rate']
    )

    student_info = df[['student_id', 'name', 'group']].drop_duplicates('student_id')
    result = metrics.merge(student_info, on='student_id', how='left')

    print(f"✅ Рассчитан рейтинг для {len(result)} студентов")
    return result


def analyze_by_discipline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Анализирует успеваемость по дисциплинам
    """
    result = df.groupby('discipline')['grade'].agg(['mean', 'median', 'std', 'count']).round(2)
    result.columns = ['Средняя', 'Медиана', 'Стд.отклонение', 'Количество']
    print(f"✅ Проанализировано {len(result)} дисциплин")
    return result


def identify_at_risk_students(rating_df: pd.DataFrame, threshold: float = 30) -> pd.DataFrame:
    """
    Находит студентов в группе риска (рейтинг < threshold)
    """
    at_risk = rating_df[rating_df['rating'] < threshold].copy()
    at_risk = at_risk.sort_values('rating', ascending=True)

    print(f"⚠️ Найдено {len(at_risk)} студентов в группе риска (порог: {threshold} баллов)")
    return at_risk