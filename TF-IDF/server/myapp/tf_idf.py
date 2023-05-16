from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

import csv

class TFIDF:
    def __init__(self):
        f = open('./myapp/navermovie2-2.csv','r')
        movies_token = csv.reader(f)
	# list 형식으로 csv를 연다.
        movieList = []
        movieName = []
        for movie in movies_token:
            movieName.append(movie.pop(0))
            # 영화 제목 
            movieList.append(' '.join(movie))
            # 문자열로 합쳐서 반환

        self.movieName = movieName
        self.movieList = movieList

    def TFIDF_use_module(self):

        tfIdfVector= TfidfVectorizer().fit(self.movieList) # movieList에 있는 모든 단어를 TFIDF 벡터로 변환
        result = tfIdfVector.transform(self.movieList).toarray() # movieList를 TFIDF 벡터로 변환

        return self.movieName, result
    
if __name__ == '__main__' :
    test = TFIDF().TFIDF_use_module()#
    print(test)
