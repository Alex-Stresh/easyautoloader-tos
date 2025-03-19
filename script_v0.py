import os
import subprocess
import yt_dlp
import whisper

# 👉 Входные данные
input_video_url = "https://www.youtube.com/watch?v=-vyheMu_DYc"  # Основное видео
second_video_url = "https://www.youtube.com/watch?v=g8YF_d_sAyU"  # Видео снизу
output_folder = "output_parts"  # Папка для нарезок
final_video = "final_full.mp4"  # Итоговое видео
subtitles_video = "input_with_subtitles.mp4"  # Видео с субтитрами
final_with_subtitles = "final_with_subtitles.mp4"  # Итоговое видео с субтитрами

# 👉 Функция для скачивания видео с YouTube
def download_youtube_video(url, filename):
    ydl_opts = {
        "format": "bv*[height<=1080]+ba/b[height<=1080]",  # Максимальное качество 720p
        "outtmpl": filename,  # Название файла
        "merge_output_format": "mp4",  # Принудительно сохраняем в MP4
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return filename if os.path.exists(filename) else None

# Скачиваем видео
print("🔻 Скачивание основного видео...")
input_video = download_youtube_video(input_video_url, "downloaded_input.mp4")
print(f"✅ Видео загружено: {input_video}")

print("🔻 Скачивание второго видео...")
second_video = download_youtube_video(second_video_url, "downloaded_second.mp4")
print(f"✅ Видео загружено: {second_video}")

# 👉 Функция для получения длительности видео
def get_video_duration(video_file):
    result = subprocess.run(
        ["ffprobe", "-i", video_file, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())

# Получаем длительность основного видео
input_duration = get_video_duration(input_video)

# 👉 Генерация субтитров перед объединением
print("🔊 Извлечение аудио из видео...")
subprocess.run(["ffmpeg", "-i", input_video, "-vn", "-acodec", "copy", "audio.aac"])

# Загружаем модель Whisper
model = whisper.load_model("base")

print("📝 Распознавание речи...")
result = model.transcribe("audio.aac", fp16=False)

# Создаем SRT-файл с минимальным текстом на экране
subtitles_srt = "subtitles.srt"
with open(subtitles_srt, "w", encoding="utf-8") as f:
    index = 1
    for segment in result["segments"]:
        words = segment["text"].split()
        start_time = segment["start"]
        end_time = segment["end"]
        duration = end_time - start_time
        
        # Разбиваем текст на части по 2-3 слова
        chunk_size = 3  # Максимум 3 слова на экран
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            
            # Рассчитываем время показа (равномерное деление отрезка)
            chunk_start = start_time + (i / len(words)) * duration
            chunk_end = chunk_start + (duration / (len(words) / chunk_size))

            # Формат времени для SRT
            start_str = f"{int(chunk_start // 3600):02}:{int((chunk_start % 3600) // 60):02}:{int(chunk_start % 60):02},{int((chunk_start % 1) * 1000):03}"
            end_str = f"{int(chunk_end // 3600):02}:{int((chunk_end % 3600) // 60):02}:{int(chunk_end % 60):02},{int((chunk_end % 1) * 1000):03}"

            # Записываем в файл
            f.write(f"{index}\n")
            f.write(f"{start_str} --> {end_str}\n")
            f.write(f"{chunk}\n\n")
            index += 1

# 👉 Добавляем субтитры к первому видео
print("🎬 Накладываем субтитры...")
subprocess.run([
    "ffmpeg", "-i", input_video, "-vf",
    f"subtitles={subtitles_srt}:force_style='Fontsize=24,PrimaryColour=&HFFFFFF&,Alignment=2'",
    "-c:a", "copy", "-y", subtitles_video
])

# 👉 Теперь соединяем видео
print("🛠️ Объединяем видео...")
subprocess.run([
    "ffmpeg", "-i", subtitles_video, "-i", second_video, "-filter_complex",
    "[0:v]scale=1080:-1[v0]; [1:v]scale=1080:-1[v1]; [v0][v1]vstack=inputs=2[v]",
    "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "28", "-preset", "fast",
    "-y", final_with_subtitles
])

# 👉 Создаём папку для нарезанных видео
os.makedirs(output_folder, exist_ok=True)

# 👉 Нарезаем объединённое видео на части по 2 минуты
print("✂️ Нарезка видео на части...")
subprocess.run([
    "ffmpeg", "-i", final_with_subtitles, "-c", "copy", "-map", "0",
    "-segment_time", "120", "-f", "segment", "-reset_timestamps", "1",
    os.path.join(output_folder, "part_%03d.mp4")
])

print(f"✅ Готово! Нарезки сохранены в папке: {output_folder}")
print(f"✅ Итоговое видео с субтитрами: {final_with_subtitles}")
