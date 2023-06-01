from pytube import YouTube
import os
import subprocess

def download_video(url, output_path):
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=True).first()
    output_file = stream.download(output_path=output_path, filename = 'song.mp3')
    return output_file

def convert_to_mp3(input_file, output_file):
    subprocess.run(['ffmpeg', '-i', input_file, output_file])

youtube_url = "https://www.youtube.com/watch?v=P8jvfi-S6IA"
output_path = "/home/baeseeun/Desktop/music"
output_file = "song.mp3"

# 영상 다운로드
video_file = download_video(youtube_url, output_path)

# mp4를 mp3로 변환
# convert_to_mp3(video_file, output_file)

# 다운로드한 mp4 파일 삭제
# os.remove(video_file)
