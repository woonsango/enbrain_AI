import pickle
import os
from pytube import YouTube
from pydub import AudioSegment
import whisper
import torch

# 피클파일 해결하기

# 모델 로드하기
model = whisper.load_model("medium")

# 피클 파일 경로
music_data_pickle = "music_data.pickle"
music_res_pickle = "music_res.pickle"

# music_data.pickle 파일 로드
with open(music_data_pickle, 'rb') as file:
    music_data = pickle.load(file)

# 기존 결과 로드 또는 파일 생성
try:
    with open(music_res_pickle, 'rb') as file:
        music_res = pickle.load(file)
except FileNotFoundError:
    music_res = {}

# 가사 추출 함수
def whisperlyrics(audio_file_path):
    audio_file = open(audio_file_path, "rb")
    result = model.transcribe("song.mp3")
    lyrics = result["text"]
    return lyrics

# 음악 데이터 처리
for idx, song_data in enumerate(music_data[:5], 1):
    song_name = song_data['노래']
    song_url = song_data['URL']
    
    print(f"Processing Song {idx}: {song_name}")

    try:
        # MP3 파일 다운로드
        yt = YouTube(song_url)
        stream = yt.streams.filter(only_audio=True).first()
        output_file = stream.download(filename='song.mp3')
        
        # 6분 이상인 노래는 제외
        audio_duration = AudioSegment.from_file(output_file).duration_seconds
        if audio_duration > 6 * 60:
            print(f"Song {idx} exceeds 6-minute limit. Skipping.")
            os.remove(output_file)  # MP3 파일 삭제
            continue

        # MP3 파일을 이용하여 가사 추출
        lyrics = whisperlyrics(output_file)
        print(lyrics)

        # 결과 저장
        song_data['가사'] = lyrics
        # music_res[song_name] = song_data  # Store song data in the music_res dictionary

        # MP3 파일 삭제
        os.remove(output_file)

    except Exception as e:
        print(f"Skipping Song {idx}: {song_name} ({str(e)})")
        continue

# music_res.pickle 파일에 결과 저장
with open(music_res_pickle, 'wb') as file:
    pickle.dump(music_res, file)
