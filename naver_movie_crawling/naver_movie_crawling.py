import re   # 정규표현식을 위한 모듈
import requests   # HTTP 요청을 보내는 모듈
import openpyxl   # 엑셀 관련 모듈
from bs4 import BeautifulSoup as bs   # 파싱 및 파싱한 문서에서 필요한 정보를 추출하는 모듈
from konlpy.tag import Okt   # 한국어 자연어 처리 모듈


# 특수문자 제거 위한 함수
def cleanText(readData):
    # 줄거리에 포함되어 있는 특수문자 제거
    text = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》‘’“”]', '', readData)  # re.sub（정규 표현식, 치환 문자, 대상 문자열）
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


def crawling(start_code, finish_code):
    try:
        global is_ok
        is_ok = False
        wb = openpyxl.Workbook()   # Workbook(): 빈 엑셀 파일을 생성
        sheet = wb.active   # active: 현재 활성화된 시트 선택

        # HTML 파싱
        j = 0
        # 네이버 영화의 영화 코드 범위 지정
        for i in range(start_code, finish_code):

            movie_code = str(i)
            raw = requests.get("https://movie.naver.com/movie/bi/mi/basic.nhn?code=" + movie_code)
            html = bs(raw.text, 'html.parser')

            # 전체 컨테이너
            movie = html.select("div.article")

            # 전체 컨테이너가 가지고 있는 영화 관련 정보
            for a, m in enumerate(movie):

                # 영화 제목 수집
                title = m.select_one("h3.h_movie a")
                # m: BeautifulSoup으로 파싱된 HTML 문서 객체
                # select_one: HTML 문서에서 하나의 요소만 선택하는 메서드
                # "h3.h_movie a": h3 태그의 class 속성 값이 h_movie인 요소의 하위 태그 중 a 태그를 선택

                # 영화 줄거리 수집
                story = m.select("div.story_area p.con_tx")
                # select: HTML 문서에서 여러 요소를 선택하는 메서드
                # "div.story_area p.con_tx": div 태그의 class 속성 값이 story_area인 요소의 하위 태그 중 p 태그의 class 속성 값이 con_tx인 모든 요소를 선택

                # 줄거리가 없으면 넘어가기
                if len(story) == 0:
                    continue

                # 출력용 (지워도 무방)
                print("=" * 50)
                print("제목:", title.text)
                print("줄거리: ")
                for s in story:
                    print(s.text)
                print("-" * 50)

                # 영화 관련 정보 엑셀(xlsx) 형식 저장
                # 데이터 만들기 1: HTML로 가져온 정보에서 TEXT 정보만 뽑아서 리스트 형태로 만들기
                story_list = [s.text for s in story]

                # 데이터 만들기 2: 여러 개로 이루어진 리스트 형태를 하나의 문자열 형태로 만들고, 정보 가공
                story_str = ''.join(story_list).replace('\xa0', ' ')
                story_del = stopwords(story_str)   # 명사 추출 + 불용어 및 한 글자 제거
                story_clean = cleanText(story_del)  # 특수문자 제거

                # 데이터 만들기 3: 엑셀에 넣기 위해 리스트 형태로 만들기
                story_split = story_clean.split(' ')
                story_split.insert(0, title.text)  # 엑셀 한 행에 넣기 위해 타이틀을 줄거리(단어형식) 리스트 맨 앞에 넣기

                # 영화 관련 정보 엑셀 행 추가: line by line으로 추가
                sheet.append(story_split)

                is_ok = True

            # 출력용 (지워도 무방)
            if is_ok == True:
                j = j + 1
            print(finish_code - start_code, "개 중에", finish_code - i, "개 남음")
            print((i - start_code)+1, "번째 영화 체크 중", j, "개의 영화 정보 저장 완료")

    # 엑셀 저장
    except:
        print("에러 발생")
        wb.save("navermovie1.csv")

    finally:
        print("완료")
        wb.save("navermovie2.csv")

crawling(165932, 215932)