import os
import subprocess
import whisper

def get_video_duration(video_file):
    result = subprocess.run(
        ["ffprobe", "-i", video_file, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())

def generate_subtitles(video_file, subtitles_file="subtitles.srt"):
    print("🔊 Извлечение аудио из видео...")
    subprocess.run(["ffmpeg", "-i", video_file, "-vn", "-acodec", "copy", "audio.aac"])

    print("📝 Распознавание речи...")
    model = whisper.load_model("base")
    result = model.transcribe("audio.aac", fp16=False)

    with open(subtitles_file, "w", encoding="utf-8") as f:
        index = 1
        for segment in result["segments"]:
            words = segment["text"].split()
            start_time = segment["start"]
            end_time = segment["end"]
            duration = end_time - start_time
            
            chunk_size = 3
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])
                
                chunk_start = start_time + (i / len(words)) * duration
                chunk_end = chunk_start + (duration / (len(words) / chunk_size))

                start_str = f"{int(chunk_start // 3600):02}:{int((chunk_start % 3600) // 60):02}:{int(chunk_start % 60):02},{int((chunk_start % 1) * 1000):03}"
                end_str = f"{int(chunk_end // 3600):02}:{int((chunk_end % 3600) // 60):02}:{int(chunk_end % 60):02},{int((chunk_end % 1) * 1000):03}"

                f.write(f"{index}\n")
                f.write(f"{start_str} --> {end_str}\n")
                f.write(f"{chunk}\n\n")
                index += 1
    
    return subtitles_file

def add_subtitles_to_video(video_file, subtitles_file, output_file):
    print("🎬 Накладываем субтитры...")
    subprocess.run([
        "ffmpeg", "-i", video_file, "-vf",
        f"subtitles={subtitles_file}:force_style='Fontsize=24,PrimaryColour=&HFFFFFF&,Alignment=2'",
        "-c:a", "copy", "-y", output_file
    ])
    return output_file

def combine_videos(main_video, background_video, output_file):
    print("🛠️ Объединяем видео...")
    subprocess.run([
        "ffmpeg", "-i", main_video, "-i", background_video, "-filter_complex",
        "[0:v]scale=1080:-1[v0]; [1:v]scale=1080:-1[v1]; [v0][v1]vstack=inputs=2[v]",
        "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "28", "-preset", "fast",
        "-y", output_file
    ])
    return output_file

def split_video(video_file, output_folder, segment_time=120):
    os.makedirs(output_folder, exist_ok=True)
    print("✂️ Нарезка видео на части...")
    subprocess.run([
        "ffmpeg", "-i", video_file, "-c", "copy", "-map", "0",
        "-segment_time", str(segment_time), "-f", "segment", "-reset_timestamps", "1",
        os.path.join(output_folder, "part_%03d.mp4")
    ])
    return output_folder