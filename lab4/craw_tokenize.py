from gensim import models

ko_model = models.fasttext.load_facebook_model('cc.ko.300.bin')

print(ko_model.wv["민법"])
print("신의성실의" in ko_model.wv.key_to_index)



import requests

def getWikiData(search):
    
    url = "https://ko.wikipedia.org/w/api.php?action=parse&parse&page="+ search +"&prop=wikitext&formatversion=2&format=json"
    headers = {'Content-Type': 'application/json'}

    response = requests.get(url, headers=headers)

    return response

text = getWikiData("민법").json()

# print(text)

# for key, value in text['parse'].items():
#     print(f'{key}: {value}\n\n')
    
print(text['parse']['wikitext'])

from icu_tokenizer import Tokenizer

tokenizer = Tokenizer(lang='ko')

text_wikitext = text['parse']['wikitext']
text_tokenize = tokenizer.tokenize(text_wikitext)
print(text_tokenize)

from sklearn.metrics.pairwise import cosine_similarity

for token in text_tokenize:
    if token in ko_model.wv.key_to_index:
        cosine_sim = cosine_similarity([ko_model.wv[text['parse']['title']]], [ko_model.wv[token]])
        if cosine_sim > 0.5:
            print(f'{token}: {cosine_sim}')
    # else: 
    #     print(token)

from gensim import models

ko_model = models.fasttext.load_facebook_model('cc.ko.300.bin')

print(ko_model.wv["민법"])
print("신의성실의" in ko_model.wv.key_to_index)



import requests

def getWikiData(search):
    
    url = "https://ko.wikipedia.org/w/api.php?action=parse&parse&page="+ search +"&prop=wikitext&formatversion=2&format=json"
    headers = {'Content-Type': 'application/json'}

    response = requests.get(url, headers=headers)

    return response

text = getWikiData("민법").json()

# print(text)

# for key, value in text['parse'].items():
#     print(f'{key}: {value}\n\n')
    
print(text['parse']['wikitext'])

from icu_tokenizer import Tokenizer

tokenizer = Tokenizer(lang='ko')

text_wikitext = text['parse']['wikitext']
text_tokenize = tokenizer.tokenize(text_wikitext)
print(text_tokenize)

from sklearn.metrics.pairwise import cosine_similarity

for token in text_tokenize:
    if token in ko_model.wv.key_to_index:
        cosine_sim = cosine_similarity([ko_model.wv[text['parse']['title']]], [ko_model.wv[token]])
        if cosine_sim > 0.5:
            print(f'{token}: {cosine_sim}')
    # else: 
    #     print(token)

