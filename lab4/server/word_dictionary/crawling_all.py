import requests
from bs4 import BeautifulSoup
from kiwipiepy import Kiwi
from urllib.parse import quote
import time
import re
import requests.exceptions

# ref 태그 사이 내용 삭제
def remove_ref_tags(text):
    pattern = r'<ref>.*?</ref>'
    cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL)
    return cleaned_text

# 검색결과 나오는 소제목들 크롤링
def get_search_results(search_query):
    nownum = 2000
    search_url = "https://ko.wikipedia.org/w/index.php?search=" + search_query + "&title=특수:검색&profile=default&fulltext=1&ns0=1&offset=0&limit=2000"
    # limit : 한 페이지 당 몇 개의 단어를 가져올 것인지
    # offset : 몇 번째 단어부터 보여줄 것인지
    # 먼저 2000개 찾고 총 개수 알아낸 다음 모든 단어 찾을 때까지 과정 반복 
    
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # 먼저 단어 총 개수 알아내기
    res_num = soup.find('div', class_ = "results-info")
    totalnum = int(res_num['data-mw-num-results-total'])
    results = soup.find_all('div', class_='mw-search-result-heading')

    search_results = []

    # 첫번째 페이지 ~2000개 연관검색어 title 리스트에 저장
    for div in results:
        title_tag = div.find('a', attrs={'title': True})
        if title_tag:
            title = title_tag['title']
            title = title.replace(' ', '_')
            search_results.append(title)
    
    # 연관 검색어가 2000개가 넘어가면 while문 반복 (2000번째 단어부터)
    while(nownum < totalnum):
        nownum = str(nownum) #str
        search_url = "https://ko.wikipedia.org/w/index.php?search=" + search_query + "&title=특수:검색&profile=default&fulltext=1&ns0=1&offset=" + nownum + "&limit=4000"
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, "html.parser")

        results = soup.find_all('div', class_='mw-search-result-heading')

        # 두번째 ~ 마지막 페이지 (2000 ~ 10000번째 단어) 연관검색어 title 페이지에 저장
        for div in results:
            title_tag = div.find('a', attrs={'title': True})
            if title_tag:
                title = title_tag['title']
                title = title.replace(' ', '_')
                search_results.append(title)

        nownum = int(nownum) #int
        nownum += 4000

    return search_results

# 각 페이지 내용 api로 가져오기
def getWikiData(search_results):
    wiki_url = "https://ko.wikipedia.org/wiki/" + search_results
    encode_url = quote(search_results)
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.get(wiki_url)
        if response.status_code == 200:
            url = "https://ko.wikipedia.org/w/api.php?action=parse&parse&page=" + encode_url + "&prop=wikitext&formatversion=2&format=json"
            response = requests.get(url, headers=headers)
            return response.json(), wiki_url
    except requests.exceptions.ConnectionError:
        time.sleep(1)
        return getWikiData(search_results)

# 페이지 내용 전처리 및 토크나이징
def tokenizing(text):
    text_data, url = getWikiData(text)
    kiwi = Kiwi()
    kiwi.prepare()
    text_data['parse']['wikitext'] = remove_ref_tags(text_data['parse']['wikitext'])
    index = text_data['parse']['wikitext'].find("== 각주 ==")
    if(index != -1):
          text_data['parse']['wikitext'] = text_data['parse']['wikitext'][:index]
    text_wikitext = text_data['parse']['wikitext']
    result = kiwi.tokenize(text_wikitext) 
    # return result, url, text_data, text_wikitext
    return result, url

# 단어 추출 및 빈도수 체크
def make_word(result):
    cosine_list = []
    made_words = []
    temp_word = ""
    bef_tag = ""
    bef_loc = 0
    form_num = 0
    cnt_dict = {}
    cosine = {}
    for form, tag, start, length in result:
        
        # Nouns (일반명사, 고유명사)
        if tag in ['NNP', 'NNG']:

            # 명사 여러 개가 띄어쓰기 없이 나왔을 때 한 단어로 취급
            if bef_tag == 'NN' and bef_loc == start:
                temp_word += form

            # 띄어쓰기 후에 들어오는 명사
            elif bef_tag == 'NN' and bef_loc != start:
                if temp_word in cnt_dict:
                    cnt_dict[temp_word] += 1
                else:
                    cnt_dict[temp_word] = 1
                made_words.append(temp_word)
                temp_word = form
                form_num = 0 # 밑에서 1 더해서 일단 초기화
                
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
            cosine_list.append(temp_word)
            temp_word += form + " "
            bef_tag = 'JKG'
            form_num += 1

        # ~적 ex)안정적 공급
        elif tag == 'XSN' and bef_tag == "NN":
            cosine_list.append(temp_word)
            temp_word += form + " "
            bef_tag = 'XSN'
            form_num += 1
        
        # 그 외의 태그 등장시 만들어진 단어 append
        else:
            if bef_tag == 'NN' and len(temp_word) > 1:
                if temp_word in cnt_dict:
                    cnt_dict[temp_word] += 1
                else:
                    cnt_dict[temp_word] = 1
                made_words.append(temp_word)
                # for token in cosine_list:
                #     if token in ko_model.wv.key_to_index:
                #         cosine_sim = cosine_similarity([ko_model.wv[text_data['parse']['title']]], [ko_model.wv[token]])
                #         if cosine_sum < cosine_sim:
                #             cosine_sum = cosine_sim
                #             cosine[temp_word] = cosine_sum

            cosine_list = []
            temp_word = ""
            bef_tag = ""
            bef_loc = 0
            form_num = 0

    return cosine, made_words, cnt_dict

# 키워드와 관련된 유사도 높은 결과 단어 추출
def getWord(text):
    search_results = get_search_results(text)
    similar_word= []
    grouped_result = []
    word_group = {}
    cnt = 0
    for search in search_results:
        content, url = tokenizing(search)
        cosine, made_words,cnt_dict = make_word(content)
        # 중복 단어 처리 및 전처리
        made_words_set = set(made_words) 
        final_words_list = list(made_words_set) 
        final_words_list = [token for token in final_words_list if "'" not in token] 
        for token in final_words_list:
            # count = 0
            # if token in ko_model.wv.key_to_index:
                # cosine_sim = cosine_similarity([ko_model.wv[text_data['parse']['title']]], [ko_model.wv[token]])
                if len(token) > 1 and token in cnt_dict:
                    # print(f'{token}: {cosine_sim}')
                    similar_word.append([token, cnt_dict[token], url]) 
        # for token in cosine:
        #     if len(token) > 1:
        #         # count = text_wikitext.count(token[0])
        #         # print(f'{token}: {cosine[token]}')
        #         similar_word.append([token, cnt_dict[token], url])
        
        # 요청 나눠서 하기
        # cnt += 1
        # if cnt%16 == 0:
        #     time.sleep(1)
    
    # 단어마다 페이지별 출현 횟수 및 url list에 넣기
    for word_info in similar_word:
            word, count, url = word_info
            if word not in word_group:
                word_group[word] = [count], [url]
            else:
                word_group[word][0].append(count)
                word_group[word][1].append(url)

    for word, (counts, urls) in word_group.items():
        grouped_result.append([word, counts, urls])
    return grouped_result

if __name__ == '__main__' :
    result = getWord("수학")
    print(result)
    # import pickle
    # import gzip 
    # with gzip.open('first_crawling', 'wb') as f:
    #     pickle.dump(result, f)