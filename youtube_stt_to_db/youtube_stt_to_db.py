import pickle  # 피클파일 로드시 사용
import os  # 파일 삭제시 사용
from pytube import YouTube  # 영상 다운시 사용
import subprocess  # mp3 파일 다운시 사용
import whisper  # 가사 추출시 사용
import torch  # gpu사용
import mysql.connector

# 모델 로드하기
model = whisper.load_model("medium")

# 피클 파일 경로
music_data_pickle = "music_data.pickle"

# music_data.pickle 파일 로드
with open(music_data_pickle, 'rb') as file:
    music_data = pickle.load(file)

# 가사 추출 함수
def whisperlyrics(output_audio):
    audio_file = open(output_audio, "rb")
    result = model.transcribe("audio.mp3", language='ko')  # 한국어로 MP3파일에서 가사 추출
    lyrics = result["text"]  # 여러가지 결과 중 전체 문장에 해당하는 값만 가져옴
    return lyrics

# 전체 노래 수
total_songs = len(music_data)
skipped_songs = 0

# 데이터베이스 연결 설정
host = '3.130.235.128'
port = 3306
user = 'eun'
password = '0112'
database = 'db_bert'
auth_plugin = 'mysql_native_password'

connection = mysql.connector.connect(host=host, port=port, user=user, password=password, database=database, auth_plugin=auth_plugin)
cursor = connection.cursor()

# 음악 데이터 처리
for idx, song_data in enumerate(music_data[:5], 1):  # 일단 노래 5개만 시도해본다
    song_name = song_data['노래']  # '노래'키에서 제목 가져오기
    song_url = song_data['URL']  # 'URL'키에서 URL 가져오기

    print(f"처리 중인 노래 {idx}: {song_name}")

    try:
        # YouTube 객체 생성
        yt = YouTube(song_url)

        # 영상 길이 확인
        if yt.length > 7 * 60:  # 7분보다 길이가 길면 영상 삭제하기
            skipped_songs += 1
            print(f"영상 길이가 7분 이상인 노래 스킵: {song_name}")
            continue

        # 7분보다 길이가 짧은 영상만 다운받기
        output_video = yt.streams.get_lowest_resolution().download(filename='video.mp4')  # 이름이 video.mp4이고 가장 낮은 화질의 영상 다운
        output_audio = "audio.mp3"  # 먼저 MP3 이름 생성

        # ffmpeg로 MP3파일 다운로드
        command = f'ffmpeg -i "{output_video}" -vn -acodec libmp3lame "{output_audio}"'  # 다운받은 MP4를 MP3로 변환하는 과정
        subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # 변환 과정에서 출력 및 오류를 화면에 표시하지 않고 실행 결과만 확인

        # MP3 파일을 이용하여 whisper 모델을 이용해 가사 추출
        lyrics = whisperlyrics(output_audio)

        # 노래, URL, 가사 묶기
        song_info = {'title': song_name, 'URL': song_url, 'lyrics': lyrics}  # 노래 당 'title'키에 제목, 'URL'키에 URL, 'lyrics'키에 가사들이 딕셔너리 형태로 묶여짐
        print(song_info)  # 완료된 결과 출력

        # 데이터베이스에 값 보내기
        query = "INSERT INTO tb_bert (titles, urls, lyrics) VALUES (%s, %s, %s)"
        data = (song_info['title'], song_info['URL'], song_info['lyrics'])
        cursor.execute(query, data)
        connection.commit()

        # 가사 추출한 MP4, MP3 파일 삭제
        os.remove(output_video)
        os.remove(output_audio)

    # MP4 다운 오류 났을시 건너뛰는 코드
    except Exception as e:
        print(f"다운 오류 발생 {idx}: {song_name} ({str(e)})")
        skipped_songs += 1
        continue

    # 남은 노래 수와 스킵된 노래 수 출력
    print(f"남은 노래 수: {total_songs - idx}")
    print(f"스킵된 노래 수: {skipped_songs}")

# 서버 연결 종료
cursor.close()
connection.close()