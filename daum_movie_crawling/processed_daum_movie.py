import re  # 정규표현식을 위한 모듈
import pickle
from konlpy.tag import Okt  # 한국어 자연어 처리 모듈


# 특수문자 제거 위한 함수
def cleanText(readData):
    # 줄거리에 포함되어 있는 특수문자 제거
    text = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》‘’“”]', '',
                  readData)  # re.sub（정규 표현식, 치환 문자, 대상 문자열）
    return text


def stopwords(readData):
    okt = Okt()
    nouns = okt.nouns(readData)  # 명사만 뽑아내기

    # 텍스트 파일 열기
    korean_stopwords_path = "./korean_stopwords.txt"
    with open(korean_stopwords_path, encoding='utf-8') as f:
        stopwords = f.readlines()
    stopwords = [x.strip() for x in stopwords]

    # 불용어 및 한 글자 제거
    remove_char = [x for x in nouns if (x not in stopwords) and (len(x) > 1)]

    # 문자열로 만들기
    text = ' '.join(remove_char)

    return text


def processedData():
    with open('daum_moive.pickle', 'rb') as f:
        data = pickle.load(f)

    processed_data = []
    for d in data:
        # 줄거리 가공
        story_del = stopwords(d['story'])  # 명사 추출 + 불용어 및 한 글자 제거
        story_clean = cleanText(story_del)  # 특수문자 제거

        # story value값 리스트로 만들기
        if len(story_clean) == 0:
            story_final = []
        else:
            story_final = story_clean.split(" ")

        d['story'] = story_final

        # 장르 가공 (genre value값 리스트로 만들기)
        if len(d['genre']) == 0:
            genre_final = []
        else:
            genre_final = d['genre'].split("/")

        d['genre'] = genre_final

        # 줄거리 및 장르 저장
        processed_data.append(d)


    with open("processed_daum_movie.pickle", "wb") as f:
        pickle.dump(processed_data, f)


processedData()