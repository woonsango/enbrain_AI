import wikipediaapi
from kiwipiepy import Kiwi

wiki_search = wikipediaapi.Wikipedia('wikicrawl (1004bse@kookmin.ac.kr)', 'ko')
kiwi = Kiwi()
kiwi.prepare()
page_py = wiki_search.page('민법')
text = page_py.text
result = kiwi.tokenize(text)

made_words = []
temp_word = ""
bef_tag = ""
bef_loc = 0
form_num = 0
cnt = 0

for form, tag, start, len in result:

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
      temp_word += form

    # 처음 들어오는 명사
    elif temp_word == "":
      temp_word = form

    # 단어 위치, 단어 개수 초기화
    bef_loc = start + len
    form_num += 1
    bef_tag = 'NN'
    cnt += 1


  # 관형격 조사일 때 ex)신의성실의 원칙
  elif tag == 'JKG' and bef_tag == "NN":
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
    if bef_tag == 'NN':
      made_words.append(temp_word)
      print(temp_word)
    temp_word = ""
    bef_tag = ""
    bef_loc = 0
    form_num = 0