import requests
from gensim import models
from kiwipiepy import Kiwi
from sklearn.metrics.pairwise import cosine_similarity

ko_model = models.fasttext.load_facebook_model('cc.ko.300.bin')

# Wikipedia content crawling
def getWikiData(search):
    url = "https://ko.wikipedia.org/w/api.php?action=parse&parse&page=" + search + "&prop=wikitext&formatversion=2&format=json"
    headers = {'Content-Type': 'application/json'}

    response = requests.get(url, headers=headers)
    return response.json(), url

# Tokenization of the synopsis
def tokenizing(text):
    text_data, url = getWikiData(text)
    kiwi = Kiwi()
    kiwi.prepare()
    
    text_wikitext = text_data['parse']['wikitext']
    result = kiwi.tokenize(text_wikitext)
    return result, url, text_data, text_wikitext

# Extracting words and their cosine similarity values
def make_word(result, text_data):
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
                for token in cosine_list:
                    if token in ko_model.wv.key_to_index:
                        cosine_sim = cosine_similarity([ko_model.wv[text_data['parse']['title']]], [ko_model.wv[token]])
                        if cosine_sum < cosine_sim:
                            cosine_sum = cosine_sim
                            cosine[temp_word] = cosine_sum

            cosine_list = []
            cosine_sum = 0
            temp_word = ""
            bef_tag = ""
            bef_loc = 0
            form_num = 0

    return cosine, made_words

# 키워드와 관련된 유사도 높은 결과 단어 추출
def getWord(text):
    content, url, text_data, text_wikitext = tokenizing(text)
    cosine, made_words = make_word(content, text_data)
    made_words_set = set(made_words)
    final_words_list = list(made_words_set)
    similar_word = []
    result = {}

    for token in final_words_list:
        count = 0
        if token in ko_model.wv.key_to_index:
            cosine_sim = cosine_similarity([ko_model.wv[text_data['parse']['title']]], [ko_model.wv[token]])
            if cosine_sim > 0.2 and len(token) >1:
                similar_word.append([token,url])
    cnt = 0
    for token in cosine:
        if cosine[token] > 0.1 and len(token) > 1:
            # count = text_wikitext.count(token[0])
            similar_word.append([token, url])
    result[text] = similar_word
    return result
result = getWord("민법")