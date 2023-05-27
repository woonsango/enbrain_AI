import pickle
from googleapiclient.discovery import build

# YouTube API 키
api_key = "AIzaSyAKOESDI-pZNQ4fV2zI-U9ViGbjLXFCm2Y"

# YouTube API 클라이언트 생성
youtube = build('youtube', 'v3', developerKey=api_key)

# 검색할 동영상의 요청 파라미터 설정
search_params = {
    'part': 'snippet',  # Include snippet data in the API response
    'q': 'Music Video',
    'type': 'video',
    'regionCode': 'US',
    'safeSearch': 'strict',
    'videoDimension': '2d',
    'videoDuration': 'short' and 'medium',
    'videoSyndicated': 'true',
    'publishedAfter': '2022-01-01T00:00:00Z',
    'publishedBefore': '2022-06-30T00:00:00Z',
    'maxResults': 50  # 페이지네이션 당 최대 50개의 검색 결과
}

# 검색 결과를 저장할 리스트
search_results = []

# 동영상 검색 요청
search_response = youtube.search().list(**search_params).execute()

# 첫 번째 페이지의 검색 결과 저장
search_results.extend(search_response['items'])

# nextPageToken을 사용하여 페이지네이션 수행
while 'nextPageToken' in search_response:
    # nextPageToken 값을 요청 파라미터에 추가
    search_params['pageToken'] = search_response['nextPageToken']
    
    # 다음 페이지의 검색 결과 요청
    search_response = youtube.search().list(**search_params).execute()
    
    # 검색 결과 저장
    search_results.extend(search_response['items'])

    # 누적된 검색 결과가 10000개에 도달하면 반복 종료
    if len(search_results) >= 20000:
        break

# 기존 데이터의 URL을 저장할 Set 자료구조 생성
existing_urls = set()

# 기존 데이터 로드 및 URL 저장
file_path = 'music_data.pickle'

try:
    with open(file_path, 'rb') as file:
        existing_data = pickle.load(file)
        existing_urls.update(data['URL'] for data in existing_data)
except FileNotFoundError:
    existing_data = []

# 검색된 음악의 노래와 URL을 저장할 리스트
music_data = []

# 검색 결과를 순회하면서 데이터 저장
for item in search_results:
    video_title = item['snippet']['title']
    video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"

    # 중복 URL인 경우 스킵
    if any(existing_data['URL'] == video_url for existing_data in existing_data):
        continue

    music_data.append({'노래': video_title, 'URL': video_url})

# 기존 데이터에 새로운 데이터 추가
existing_data.extend(music_data)

# 피클 파일에 데이터 저장
with open(file_path, 'wb') as file:
    pickle.dump(existing_data, file)
