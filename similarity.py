# !git clone https://github.com/SKTBrain/KoBERT.git
# !pip install sentencepiece
# import sys
# sys.path.append('KoBERT')
from sklearn.metrics.pairwise import cosine_similarity
from kobert.pytorch_kobert import get_pytorch_kobert_model
import mysql.connector

# 데이터베이스 연결 설정
host = '3.130.235.128'
port = 3306
user = 'eun'
password = '0112'
database = 'db_bert'
auth_plugin = 'mysql_native_password'

connection = mysql.connector.connect(host=host, port=port, user=user, password=password, database=database, auth_plugin=auth_plugin)
cursor = connection.cursor()

# 쿼리 실행
query = "SELECT titles, urls, lyrics, vector FROM tb_bert"
cursor.execute(query)

# 결과 가져오기
results = cursor.fetchall()
results = [song for song in results if len(song[2]) > 10]
# KoBERT 모델 및 토크나이저 불러오기
bertmodel, vocab = get_pytorch_kobert_model()

import sentencepiece as spm
import numpy as np

sp = spm.SentencePieceProcessor()

# 이 밑에 3줄을 이용해 코드 경로를 찾은 후 sp.lod("?") 물음표 대신 넣어주면 됨.
# from kobert.utils import get_tokenizer

# tokenizer = get_tokenizer()
# print(tokenizer)
sp.load('/home/20223176/.cache/kobert_news_wiki_ko_cased-1087f8699e.spiece')

def encode_text(text):
    # 텍스트를 토큰화하고, 각 토큰을 정수 ID로 변환
    tokens = sp.encode_as_pieces(text)

    # Make sure the tokens does not exceed 512
    if len(tokens) > 512:
        tokens = tokens[:512]

    if len(tokens) == 0:  # 추가된 코드
        print("Warning: the input text has resulted in 0 tokens.")
        return None

    input_ids = [vocab[token] for token in tokens]
    # 입력 텐서 생성
    input_ids = torch.tensor([input_ids], dtype=torch.long)
    # KoBERT 모델을 사용하여 벡터 인코딩
    with torch.no_grad():
        model_output = bertmodel(input_ids)
    # 'last_hidden_state'만 가져오기
    last_hidden_state = model_output[0]
    # 평균 벡터를 계산 (토큰 차원을 따라서)
    mean_vector = last_hidden_state.mean(dim=1).numpy()
    return mean_vector.flatten()
def calculate_similarity(vector1, vector2):
    # 두 벡터 사이의 코사인 유사도 계산
    return cosine_similarity(vector1.reshape(1, -1), vector2.reshape(1, -1))
# 키워드 점수 계산
def keyword_score(keyword, lyrics):
    return lyrics.count(keyword)

# 유사도 점수 계산
def similarity_score(vector1, vector2):
    return cosine_similarity(vector1.reshape(1, -1), vector2.reshape(1, -1))

# 최종 점수 계산
def total_score(keyword, lyrics, user_vector, song_vector, alpha=1e-4):
    return keyword_score(keyword, lyrics) * similarity_score(user_vector, song_vector)
def recommend_songs(keyword):

    # 키워드를 벡터로 변환
    keyword_vector = encode_text(keyword)

    # 모든 노래에 대해 유사도를 계산
    scores = []
    for song in results:
        song_vector = song[3]
        song_vector = np.fromstring(song_vector, sep=',')  # Convert string to numpy array
        if song_vector is not None:  # 추가된 코드
            score = total_score(keyword, song[2], keyword_vector, song_vector)
            scores.append((score, song))
            continue

    # 가장 유사한 노래를 찾아서 반환
    most_similar_songs = sorted(scores, key=lambda x: x[0], reverse=True)[:10]

    song_title = []
    song_url = []
    # Return the top 10 similar songs' title and URL
    for idx, song_info in enumerate(most_similar_songs, start=1):

        song_title.append(song_info[1][0])
        song_url.append(song_info[1][1])
    song_dict = {'title' : song_title, 'url' : song_url}
    return song_dict