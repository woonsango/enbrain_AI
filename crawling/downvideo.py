import pickle
import os
from pytube import YouTube
from pydub import AudioSegment
import subprocess
import whisper
import torch

# 모델 로드하기
model = whisper.load_model("medium")

# 피클 파일 경로
music_data_pickle = "music_data.pickle"

# music_data.pickle 파일 로드
with open(music_data_pickle, 'rb') as file:
    music_data = pickle.load(file)

# 가사 추출 함수
def whisperlyrics(audio_file_path):
    audio_file = open(audio_file_path, "rb")
    result = model.transcribe("audio.mp3", language = 'ko')
    lyrics = result["text"]
    return lyrics

# 전체 노래 수 초기화
total_songs = len(music_data)
skipped_songs = 0

# 음악 데이터 처리
for idx, song_data in enumerate(music_data[:5], 1):
    song_name = song_data['노래']
    song_url = song_data['URL']
    
    print(f"처리 중인 노래 {idx}: {song_name}")
    
    try:
        # MP4 파일 다운로드
        yt = YouTube(song_url)
        output_video = yt.streams.get_lowest_resolution().download(filename='video.mp4')
        output_audio = "audio.mp3"

        # ffmpeg 명령어 실행
        command = f'ffmpeg -i "{output_video}" -vn -acodec libmp3lame "{output_audio}"'
        subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # MP3 파일을 이용하여 가사 추출
        lyrics = whisperlyrics(output_audio)

        # 노래, URL, 가사 묶기
        song_info = {'title': song_name,'URL': song_url,'lyrics': lyrics}
        print(song_info)

        # 묶인 노래 정보를 데이터베이스에 보내는 코드

        # MP3 파일 삭제
        os.remove(output_video)
        os.remove(output_audio)

    except Exception as e:
        print(f"Skipping Song {idx}: {song_name} ({str(e)})")
        skipped_songs += 1
        continue
    
    # 남은 노래 수와 스킵된 노래 수 출력
    print(f"남은 노래 수: {total_songs - idx}")
    print(f"스킵된 노래 수: {skipped_songs}")