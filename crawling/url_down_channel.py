import pickle
from googleapiclient.discovery import build

# YouTube API 키
api_key = "AIzaSyBUgWGFMPhWkUf7zawPk7NvlnyJx02V4hc"

# YouTube API 클라이언트 생성
youtube = build('youtube', 'v3', developerKey=api_key)

# 검색할 동영상의 요청 파라미터 설정
search_params = {
    'part': 'snippet',
    'channelId': 'UChECO7Cr9QpD1XE1YUiAjAA',
    'publishedAfter': '2017-01-01T00:00:00Z',
    # 'publishedBefore': '2017-12-31T00:00:00Z',
    'videoDuration': 'short' or 'medium',
    'type': 'video',
    'maxResults': 50
}

# 검색 결과를 저장할 리스트
search_results = []

# 페이지네이션을 위한 nextPageToken 초기화
next_page_token = None

# 페이지네이션 수행
while True:
    # nextPageToken 값을 요청 파라미터에 추가
    if next_page_token:
        search_params['pageToken'] = next_page_token
    
    # 동영상 검색 요청
    search_response = youtube.search().list(**search_params).execute()
    
    # 검색 결과 저장
    search_results.extend(search_response['items'])
    
    # 다음 페이지의 토큰 가져오기
    next_page_token = search_response.get('nextPageToken')
    
    # 다음 페이지가 없으면 반복 종료
    if not next_page_token:
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
    if video_url in existing_urls:
        continue

    music_data.append({'노래': video_title, 'URL': video_url})

# 기존 데이터에 새로운 데이터 추가
existing_data.extend(music_data)

# 피클 파일에 데이터 저장
with open(file_path, 'wb') as file:
    pickle.dump(existing_data, file)

# 노래 개수 확인
total_songs = len(music_data)
print(f"피클 파일에 저장된 노래 개수: {total_songs}")


