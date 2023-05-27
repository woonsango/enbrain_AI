import os
import time
import pickle
from pytube import YouTube

# 피클 파일 경로
file_path = 'music_data.pickle'

# 다운로드 위치
download_path = '/home/seeun/Desktop/music_video'

# 피클 파일 로드
with open(file_path, 'rb') as f:
    music_data = pickle.load(f)

# 다운로드 완료된 영상 개수 및 총 소요 시간 초기화
completed_downloads = 0
total_time = 0
start_time = time.time()

# 모든 영상 다운로드
for data in music_data:
    video_url = data['URL']

    try:
        # YouTube 동영상 객체 생성
        youtube = YouTube(video_url)

        # 'age restricted'인 경우 건너뛰기
        if youtube.age_restricted:
            print(f"다운로드 실패: {video_url} - Age restricted, skipping")
            continue

        # 동영상 다운로드
        youtube.streams.get_lowest_resolution().download(output_path=download_path)
        print(f"다운로드 완료: {video_url}")

        # 오디오 스트림 필터링 (mp3 포맷)
        audio_stream = youtube.streams.filter(only_audio=True).first()

        # mp3 다운로드
        mp3_filename = audio_stream.download(output_path=download_path)

        # 다운로드한 파일 이름을 .mp3로 변경
        new_filename = os.path.splitext(mp3_filename)[0] + '.mp3'
        os.rename(mp3_filename, new_filename)

        # 다운로드 및 변환 완료 및 소요 시간 정보 출력
        print(f"다운로드 및 변환 완료: {video_url}")

        # 다운로드 완료된 영상 개수 증가
        completed_downloads += 1

        # 50개 다운로드 완료 시 반복 종료
        if completed_downloads >= 50:
            break

    except Exception as e:
        print(f"다운로드 실패: {video_url} - {str(e)}")

end_time = time.time()
# 다운로드 완료된 영상 개수 및 총 소요 시간 출력
print(f"다운로드 완료된 영상 개수: {completed_downloads}")
print(f"총 소요 시간: {end_time - start_time}초")
