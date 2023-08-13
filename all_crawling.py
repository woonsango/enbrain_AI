import requests
from bs4 import BeautifulSoup
from gensim import models
from kiwipiepy import Kiwi
import time
def get_search_results(search_query):
    nownum = 2000
    search_url = "https://ko.wikipedia.org/w/index.php?search=" + search_query + "&title=특수:검색&profile=default&fulltext=1&ns0=1&offset=0&limit=2000"
    # limit이 몇 개씩 단어 보여주는지 알려주는거 offset이 시작번호 0으로 하면 처음부터 
    # 먼저 2000개 정도 찾고 총 개수 알아낸 다음 그 때까지 과정 반복
    
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # 먼저 단어 총 개수 알아내기
    res_num = soup.find('div', class_ = "results-info")
    totalnum = int(res_num['data-mw-num-results-total'])
    print(totalnum)
    results = soup.find_all('div', class_='mw-search-result-heading')

    search_results = []

    for div in results:
        title_tag = div.find('a', attrs={'title': True})
        if title_tag:
            title = title_tag['title']
            search_results.append(title)
    
    # 2번째 검색부터 반복 
    while(nownum < totalnum) :
        nownum = str(nownum) #str
        search_url = "https://ko.wikipedia.org/w/index.php?search=" + search_query + "&title=특수:검색&profile=default&fulltext=1&ns0=1&offset=" + nownum + "&limit=2000"
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
def getWikiData(search_results):
    wiki_url = "https://ko.wikipedia.org/wiki/" + search_results
    headers = {'Content-Type': 'application/json'}
    response = requests.get(wiki_url)
    if response.status_code == 200:
        url = "https://ko.wikipedia.org/w/api.php?action=parse&parse&page=" + search_results + "&prop=wikitext&formatversion=2&format=json"
        response = requests.get(url, headers=headers)
    return response.json(), wiki_url

# Tokenization of the synopsis
def tokenizing(text):
    text_data, url = getWikiData(text)
    kiwi = Kiwi()
    kiwi.prepare()
    index = text_data['parse']['wikitext'].find("== 각주 ==")
    if(index != -1):
          text_data['parse']['wikitext'] = text_data['parse']['wikitext'][:index]
    text_wikitext = text_data['parse']['wikitext']
    result = kiwi.tokenize(text_wikitext) 
    # return result, url, text_data, text_wikitext
    return result, url

# Extracting words and their cosine similarity values
def make_word(result):
    cosine_list = []
    made_words = []
    temp_word = ""
    bef_tag = ""
    bef_loc = 0
    form_num = 0
    cosine_sum = 0
    cosine = {}

    for form, tag, start, length in result:
        # Nouns
        if tag in ['NNP', 'NNG']:
            # 명사 여러 개가 띄어쓰기 없이 나왔을 때 한 단어로 취급, 후에 바꿔도 됨(모든 명사 구분하는 걸로)
            if bef_tag == 'NN' and bef_loc == start:
                temp_word += form
            # 띄어쓰기 후에 들어오는 명사
            elif bef_tag == 'NN' and bef_loc != start:
                made_words.append(temp_word)
                temp_word = form
                form_num = 0
                
            # 관형격 조사 다음에 들어오는 명사
            elif bef_tag == 'JKG' or bef_tag == 'XSN':
                cosine_list.append(form)
                temp_word += form
                
            elif temp_word == "":
                temp_word = form

            bef_loc = start + length
            form_num += 1
            bef_tag = 'NN'

        # 관형격 조사일 때 ex)신의성실의 원칙
        elif tag == 'JKG' and bef_tag == "NN":
            cosine_list.append(form)
            temp_word += form + " "
            bef_tag = 'JKG'
            form_num += 1

        # ~적 (e.g., 안정적, 감각적)
        elif tag == 'XSN' and bef_tag == "NN":
            temp_word += form + " "
            bef_tag = 'XSN'
            form_num += 1
        
        else:
            if bef_tag == 'NN' and len(temp_word) > 1:
                made_words.append(temp_word)
                # for token in cosine_list:
                #     if token in ko_model.wv.key_to_index:
                #         cosine_sim = cosine_similarity([ko_model.wv[text_data['parse']['title']]], [ko_model.wv[token]])
                #         if cosine_sum < cosine_sim:
                #             cosine_sum = cosine_sim
                #             cosine[temp_word] = cosine_sum

            cosine_list = []
            cosine_sum = 0
            temp_word = ""
            bef_tag = ""
            bef_loc = 0
            form_num = 0

    return cosine, made_words

# 키워드와 관련된 유사도 높은 결과 단어 추출
def getWord(text):
    search_results = get_search_results(text)
    page_result = {}
    result =[]
    for search in search_results:
        similar_word = []
        content, url = tokenizing(search)
        cosine, made_words = make_word(content)
        made_words_set = set(made_words)
        final_words_list = list(made_words_set)
        for token in final_words_list:
            # count = 0
            # if token in ko_model.wv.key_to_index:
                # cosine_sim = cosine_similarity([ko_model.wv[text_data['parse']['title']]], [ko_model.wv[token]])
                # if cosine_sim > 0.16 and len(token) >1:
                    # print(f'{token}: {cosine_sim}')
                    similar_word.append([token,url])
        for token in cosine:
            # if cosine[token] > 0.12 and len(token) > 1:
                # count = text_wikitext.count(token[0])
                # print(f'{token}: {cosine[token]}')
                similar_word.append([token, url])
        page_result[search] = similar_word
        print(page_result)

    result.append([text, page_result])
    return result

if __name__ == '__main__' :
    result = getWord("민법")
    print(result)
    # print(len(result))
# search_query = "민법"
# start = time.time()
# search_results = get_search_results(search_query)
# finish = time.time()


# print(search_results)
# print("단어 개수 : " ,len(search_results))
# print("걸린 시간 : ",finish - start)

#한 번에 많은 단어 할 수록 시간 단축, limit 최대 5000
#검색 한 번에 알 수 있는 최대 관련 검색어 10000개
