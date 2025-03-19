#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import traceback

# Добавление отладочной печати для проверки запуска
print("Скрипт запущен!")

# Добавляем текущую директорию в путь поиска модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

print(f"Текущая директория добавлена в путь: {current_dir}")
print(f"Путь поиска модулей: {sys.path}")

try:
    print("Попытка импорта video_handler...")
    from video_handler import VideoProcessor
    print("Импорт video_handler успешен")
except Exception as e:
    print(f"Ошибка при импорте: {e}")
    traceback.print_exc()
    sys.exit(1)

def main():
    print("🚀 Запуск обработки видео...")
    
    try:
        # Укажите URL основного видео
        main_video_url = "https://www.youtube.com/watch?v=-vyheMu_DYc"
        
        # Для фонового видео можно указать либо конкретное видео
        background_video_url = "https://www.youtube.com/watch?v=g8YF_d_sAyU"
        
        # Либо плейлист, из которого будет выбрано случайное видео
        background_playlist_url = None  # "https://www.youtube.com/playlist?list=PLAYLIST_ID"
        
        print("Создание экземпляра VideoProcessor...")
        processor = VideoProcessor(
            main_video_url=main_video_url,
            background_video_url=background_video_url,
            background_playlist_url=background_playlist_url,
            output_folder="output_parts",
            final_with_subtitles="final_with_subtitles.mp4"
        )
        
        print("Запуск процесса обработки...")
        result = processor.process()
        print(f"Результат обработки: {result}")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("Запуск main()...")
    main()
    print("Завершение работы скрипта")