import requests
from bs4 import BeautifulSoup
import time

def get_search_results(search_query):
    nownum = 2000
    search_url = "https://ko.wikipedia.org/w/index.php?search=" + search_query + "&title=특수:검색&profile=default&fulltext=1&ns0=1&offset=0&limit=2000"
    # limit이 몇 개씩 단어 보여주는지 알려주는거 offset이 시작번호 0으로 하면 처음부터 
    # 순서 1: 먼저 방문, 한 100개정도 먼저 보여줘 그리고 몇갠지 찾아 그리고 그 숫자 끝날때까지 한 2000개? 씩 한 페이지에 보여주고 단어 크롤링하기
    
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, "html.parser")

    res_num = soup.find('div', class_ = "results-info")
    totalnum = int(res_num['data-mw-num-results-total'])
    
    results = soup.find_all('div', class_='mw-search-result-heading')

    search_results = []

    for div in results:
        title_tag = div.find('a', attrs={'title': True})
        if title_tag:
            title = title_tag['title']
            search_results.append(title)

    while(nownum < totalnum) :
        nownum = str(nownum) #str
        search_url = "https://ko.wikipedia.org/w/index.php?search=" + search_query + "&title=특수:검색&profile=default&fulltext=1&ns0=1&offset=" + nownum + "&limit=4000"
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, "html.parser")

        results = soup.find_all('div', class_='mw-search-result-heading')

        for div in results:
            title_tag = div.find('a', attrs={'title': True})
            if title_tag:
                title = title_tag['title']
                search_results.append(title)

        nownum = int(nownum) #int
        nownum += 4000

    return search_results

search_query = "인사"
start = time.time()
search_results = get_search_results(search_query)
finish = time.time()


print(search_results)
print("단어 개수 : " ,len(search_results))
print("걸린 시간 : ",finish - start)

#한 번에 많은 단어 할 수록 시간 단축, limit 최대 5000
#검색 한 번에 알 수 있는 최대 관련 검색어 10000개
