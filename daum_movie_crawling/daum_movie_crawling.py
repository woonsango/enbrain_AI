import requests  # HTTP 요청을 보내는 모듈
from bs4 import BeautifulSoup as bs  # 파싱 및 파싱한 문서에서 필요한 정보를 추출하는 모듈
from selenium import webdriver  # 웹 브라우저를 조작하는 모듈
from selenium.webdriver.common.by import By  # 웹 페이지에서 요소를 찾는 방법에 대한 모듈
from selenium.webdriver.support.ui import WebDriverWait  # 특정 조건이 충족될 때까지 대기하는 모듈
from selenium.webdriver.support import expected_conditions as EC  # 특정 조건이 충족될 때까지 대기하는 모듈에서 사용하는, 예상 조건에 대한 모듈
from selenium.webdriver.chrome.options import Options  # Chrome 브라우저 설정에 대한 모듈
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities  # 웹 드라이버 설정에 대한 모듈
import pickle  # 데이터를 파일로 저장하고 불러오는 모듈


def crawling(start_code, finish_code):
    try:
        global is_ok
        is_ok = False
        cnt = 0
        j = 0
        data = []  # 수집한 데이터를 저장할 리스트

        # 영화 코드 범위 지정
        for i in range(finish_code, start_code, -1):
            movie_code = str(i)
            raw = requests.get("https://movie.daum.net/moviedb/main?movieId=" + movie_code)
            html = bs(raw.text, 'html.parser')

            # 페이지가 완전히 로드되는 걸 기다리지 않게끔 웹 드라이버 설정
            caps = DesiredCapabilities().CHROME
            caps["pageLoadStrategy"] = "none"  # default: caps["pageLoadStrategy"] = "normal"

            options = Options()
            options.add_argument("--headless")  # 창을 띄우지 않게끔
            driver = webdriver.Chrome('chromedriver', options=options)
            driver.get("https://movie.daum.net/moviedb/main?movieId=" + movie_code)

            # 영화 제목 수집
            title = html.find("head").find("title").text.replace(" | 다음영화", "")
            # 존재하지 않는 영화일 때 넘어가기
            if title == "다음영화":
                continue

            # 영화 줄거리 수집
            try:
                raw_story = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    '#mainContent > div > div.box_detailinfo > div.contents > div.detail_basicinfo > div > div > div'))
                ).text
                # 해당 요소가 로딩될 때까지 최대 5초까지 대기
                # presence_of_element_located: 로딩된 페이지에 조건 요소가 있는지 확인
                story = raw_story.replace("\n", " ")
            except:  # 줄거리 정보가 없을 때
                story = ""

            # 영화 장르 수집
            try:
                genre = driver.find_element(By.XPATH,
                                            '//*[@id="mainContent"]//dt[contains(text(), "장르")]').find_element(By.XPATH,
                                                                                                               'following-sibling::dd').text
            except:  # 장르 정보가 없을 때
                genre = ""

            # 데이터를 리스트에 추가
            data.append({'title': title, 'story': story, 'genre': genre})

            # 저장
            with open('daum_moive.pickle', 'wb') as f:
                pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

            # 창 닫기
            driver.quit()

            # 줄거리가 없는 영화 제외했을 때의 영화 정보의 개수 정하기
            if len(data[-1]['story']) != 0:
                cnt += 1
                if cnt == 20000:
                    return

            # 출력용 (지워도 무방)
            is_ok = True
            print("=" * 50)
            print("제목:", title)
            print("줄거리: ", story)
            print("장르: ", genre)
            print("-" * 50)
            if is_ok == True:
                j = j + 1
            print((finish_code - i) + 1, "번째 영화 체크 중", j, "개의 영화 정보 저장 완료 (줄거리가 존재하는 영화 정보는", cnt, "개)")
            print(finish_code - start_code, "개 중에", (i - start_code) - 1, "개 남음")

    except:
        print((finish_code - i) + 1, "번째 영화 체크 중 error")


crawling(24157, 129157)   # 총 105,000만 개