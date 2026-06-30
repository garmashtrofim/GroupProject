import json
import pandas as pd
from functions import (
    load_and_validate_data,
    calculate_student_rating,
    analyze_by_discipline,
    identify_at_risk_students
)
import os
import webbrowser
import threading
import time


def main():
    """
    Главная функция для запуска анализа
    """
    print("=" * 50)
    print("🚀 СИСТЕМА АНАЛИЗА УСПЕВАЕМОСТИ СТУДЕНТОВ")
    print("=" * 50)

    try:
        # 1. Загрузка конфигурации
        print("\n📂 Загрузка конфигурации...")
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ Конфигурация загружена")

        # 2. Загрузка и валидация данных
        print("\n📊 Загрузка данных...")
        df = load_and_validate_data('students.csv')

        # 3. Расчет рейтинга
        print("\n📈 Расчет рейтинга студентов...")
        rating_df = calculate_student_rating(df, weights=config['weights'])

        # 4. Анализ по дисциплинам
        print("\n📚 Анализ по дисциплинам...")
        discipline_stats = analyze_by_discipline(df)

        # 5. Поиск группы риска
        print("\n⚠️ Поиск студентов в группе риска...")
        at_risk = identify_at_risk_students(
            rating_df,
            threshold=config['risk_threshold']
        )

        # 6. Сохранение результатов в CSV
        print("\n💾 Сохранение результатов...")

        # Создаём папки, если их нет
        os.makedirs('data', exist_ok=True)

        rating_df.to_csv(config['output_files']['rating_file'], index=False, encoding='utf-8')
        discipline_stats.to_csv(config['output_files']['discipline_stats_file'], encoding='utf-8')
        at_risk.to_csv(config['output_files']['at_risk_file'], index=False, encoding='utf-8')

        # 7. Подготовка данных для HTML
        print("\n🌐 Подготовка данных для веб-страницы...")

        # Преобразуем данные в JSON для передачи в HTML
        results = {
            'students': rating_df.to_dict('records'),
            'discipline_stats': discipline_stats.reset_index().to_dict('records'),
            'at_risk': at_risk.to_dict('records'),
            'total_students': len(rating_df),
            'total_disciplines': len(discipline_stats),
            'at_risk_count': len(at_risk),
            'at_risk_percent': round(len(at_risk) / len(rating_df) * 100, 1) if len(rating_df) > 0 else 0,
            'top_students': rating_df.nlargest(3, 'rating')[['name', 'group', 'rating']].to_dict('records'),
            'weights': config['weights']
        }

        # Сохраняем JSON для HTML
        with open('data/results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print("✅ Данные сохранены в data/results.json")

        # 8. Вывод итоговой статистики
        print("\n" + "=" * 50)
        print("📊 ИТОГОВАЯ СТАТИСТИКА")
        print("=" * 50)
        print(f"✅ Всего студентов: {len(rating_df)}")
        print(f"⚠️ В группе риска: {len(at_risk)} ({len(at_risk) / len(rating_df) * 100:.1f}%)")
        print(f"📚 Дисциплин: {len(discipline_stats)}")
        print(f"\n📁 Результаты сохранены в файлы:")
        print(f"   - {config['output_files']['rating_file']}")
        print(f"   - {config['output_files']['discipline_stats_file']}")
        print(f"   - {config['output_files']['at_risk_file']}")
        print(f"   - data/results.json (для веб-страницы)")
        print("=" * 50)
        print("✅ Анализ успешно завершён!")

        # ====== АВТОМАТИЧЕСКОЕ ОТКРЫТИЕ БРАУЗЕРА ======
        print("\n🌐 Открытие веб-страницы...")

        # Функция для открытия браузера с задержкой
        def open_browser():
            time.sleep(1.5)
            webbrowser.open('http://localhost:8000/index.html')
            print("✅ Браузер открыт!")

        # Запускаем открытие браузера в отдельном потоке
        threading.Thread(target=open_browser, daemon=True).start()

        # Запускаем сервер
        print("🚀 Запуск веб-сервера на http://localhost:8000")
        print("   Нажмите Ctrl+C для остановки сервера")
        print("-" * 50)
        os.system('python -m http.server 8000')

    except FileNotFoundError as e:
        print(f"\n❌ ОШИБКА: Файл не найден - {e}")
        print("   Убедитесь, что файлы config.json и students.csv существуют")
    except KeyboardInterrupt:
        print("\n\n👋 Сервер остановлен")
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()