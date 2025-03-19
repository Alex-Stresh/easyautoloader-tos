#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from video_downloader import download_youtube_video, get_random_video_from_playlist
from video_processor import (
    generate_subtitles, 
    add_subtitles_to_video, 
    combine_videos, 
    split_video
)

class VideoProcessor:
    def __init__(
        self, 
        main_video_url=None, 
        background_playlist_url=None,
        background_video_url=None,
        output_folder="output_parts",
        final_video="final_full.mp4",
        subtitles_video="main_with_subtitles.mp4",
        final_with_subtitles="final_with_subtitles.mp4"
    ):
        self.main_video_url = main_video_url
        self.background_playlist_url = background_playlist_url
        self.background_video_url = background_video_url
        self.output_folder = output_folder
        self.final_video = final_video
        self.subtitles_video = subtitles_video
        self.final_with_subtitles = final_with_subtitles
        
        self.main_video_file = "downloaded_main.mp4"
        self.background_video_file = "downloaded_background.mp4"
        self.subtitles_file = "subtitles.srt"
        self.audio_file = "audio.aac"
        
    def process(self):
        try:
            # Шаг 1: Скачивание видео
            print("🔻 Скачивание основного видео...")
            self.main_video_file = download_youtube_video(self.main_video_url, self.main_video_file)
            print(f"✅ Основное видео загружено: {self.main_video_file}")
            
            # Выбор фонового видео из плейлиста, если предоставлен URL плейлиста
            if self.background_playlist_url and not self.background_video_url:
                self.background_video_url = get_random_video_from_playlist(self.background_playlist_url)
                if not self.background_video_url:
                    print("❌ Не удалось получить видео из плейлиста")
                    return False
            
            print("🔻 Скачивание фонового видео...")
            self.background_video_file = download_youtube_video(self.background_video_url, self.background_video_file)
            print(f"✅ Фоновое видео загружено: {self.background_video_file}")
            
            # Шаг 2: Генерация субтитров
            self.subtitles_file = generate_subtitles(self.main_video_file, self.subtitles_file)
            
            # Шаг 3: Добавление субтитров к основному видео
            self.subtitles_video = add_subtitles_to_video(
                self.main_video_file, 
                self.subtitles_file, 
                self.subtitles_video
            )
            
            # Шаг 4: Объединение видео
            self.final_with_subtitles = combine_videos(
                self.subtitles_video,
                self.background_video_file,
                self.final_with_subtitles
            )
            
            # Шаг 5: Разбиение на части
            output_folder = split_video(self.final_with_subtitles, self.output_folder)
            
            print(f"✅ Готово! Нарезки сохранены в папке: {output_folder}")
            print(f"✅ Итоговое видео с субтитрами: {self.final_with_subtitles}")
            
            # Шаг 6: Очистка временных файлов
            self.cleanup()
            
            return True
            
        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")
            return False
    
    def cleanup(self):
        """Удаляет временные файлы после обработки, оставляя только нарезанные видео"""
        print("🧹 Очистка временных файлов...")
        
        # Список файлов для удаления
        files_to_remove = [
            self.main_video_file,
            self.background_video_file,
            self.subtitles_file,
            self.audio_file,
            self.subtitles_video,
            self.final_with_subtitles
        ]
        
        for file in files_to_remove:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"  ✓ Удален файл: {file}")
                except Exception as e:
                    print(f"  ✗ Не удалось удалить файл {file}: {e}")
        
        print("✅ Очистка завершена. Оставлены только нарезанные видео в папке.")