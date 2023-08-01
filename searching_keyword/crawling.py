import requests

def getWikiData(search):
    url = "https://ko.wikipedia.org/w/api.php?action=parse&parse&page="+ search +"&prop=wikitext&formatversion=2&format=json"
    headers = {'Content-Type': 'application/json'}

    response = requests.get(url, headers=headers)

    return response.json(), url

def contents(text):
    text, url = getWikiData(text)
    from kiwipiepy import Kiwi

    kiwi = Kiwi()
    kiwi.prepare()


    text_wikitext = text['parse']['wikitext']
    result = kiwi.tokenize(text_wikitext)
    return result, url, text
def word_cosine_similarity(result,text):
    
    cosine_list = []
    made_words = []
    temp_word = ""
    bef_tag = ""
    bef_loc = 0
    form_num = 0
    cnt = 0
    cosine = []
    cosine_sum = 0
    from sklearn.metrics.pairwise import cosine_similarity
    for form, tag, start, length in result:

      # 먼저 명사일 때
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

        # 처음 들어오는 명사
        elif temp_word == "":
          temp_word = form

        # 단어 위치, 단어 개수 초기화
        bef_loc = start + length
        form_num += 1
        bef_tag = 'NN'
        cnt += 1

      # 관형격 조사일 때 ex)신의성실의 원칙
      elif tag == 'JKG' and bef_tag == "NN":
        cosine_list.append(form)
        temp_word += form + " "
        bef_tag = 'JKG'
        form_num += 1

      # ~적
      elif tag == 'XSN' and bef_tag == "NN":
        temp_word += form + " "
        bef_tag = 'XSN'
        form_num += 1


      # 다른 태그 들어왔을때 단어 리스트에 넣기 및 초기화
      # 더 고려할 것 : 몇 개의 형태소로 이루어진 것만 넣을까, 1글자거나 긴 단어는 뺄까, 1 <= form_num <= 4 and ~의 경우 빼기
      else:
        # if temp_word not in made_words:
        del length
        if bef_tag == 'NN' and len(temp_word) > 1:
          made_words.append(temp_word)
          for token in cosine_list:
            if token in ko_model.wv.key_to_index:
                cosine_sim = cosine_similarity([ko_model.wv[text['parse']['title']]], [ko_model.wv[token]])
                if cosine_sum < cosine_sim:
                    cosine_sum = cosine_sim
                    cosine.append([temp_word, cosine_sum])
          # print(temp_word)
        cosine_list = []
        cosine_sum = 0
        temp_word = ""
        bef_tag = ""
        bef_loc = 0
        form_num = 0
    return cosine, made_words
def getWord(text):
    content, url, text = contents(text)
    cosine, made_words = word_cosine_similarity(content, text)
    made_words_set = set(made_words)
    final_words_list = list(made_words_set)
    result = {}

    for token in final_words_list:
        count = 0
        if token in ko_model.wv.key_to_index:
            cosine_sim = cosine_similarity([ko_model.wv[text['parse']['title']]], [ko_model.wv[token]])
            if cosine_sim > 0.2:
                # for form, tag, start, len in result:
                #     if token==form:
                #         count+=1
                # print(f'{token}: {cosine_sim}')
                result[token] = [cosine_sim, url]

    for token in cosine:
        if token[1] > 0.1:
            count = text_wikitext.count(token[0])
            # print(f'{token[0]} : {token[1]}')
            result[token[0]] = [token[1], url]

    return result
result = getWord("민법")
result