import numpy as np
from numpy.linalg import norm
from django.db import models
from .tf_idf import TFIDF

class cosine_sim:
    
    def __init__(self):

        self.movieName, self.movieTFIDF = TFIDF().TFIDF_use_module()
	
    def cosine_sim_cal(self, name_input):
        if name_input in self.movieName:

            story_input = self.movieTFIDF[self.movieName.index(name_input)]

            result = []

            for movie in range(len(self.movieTFIDF)):
                cos_sim =np.dot(story_input, self.movieTFIDF[movie])/(norm(story_input)*norm(self.movieTFIDF[movie]))
                # 
                if cos_sim > 0.3:
                    result.append([movie,cos_sim])
		# 유사도가 0.3 보다 높은 영화만 출력
            result = sorted(result, key = lambda x : -x[1]) # 정렬
            # 유사도가 높은 순으로 정리
            result.pop(0)
	    # 입력받은 제목은 제외
            movieSimName = []
            for m in result:
                movieSimName.append(self.movieName[m[0]])
                #  
            
            return movieSimName

        
        else:
            return ["그런 영화는 없어요 ㅠㅠ"]
        
if __name__ == '__main__' :
    test = cosine_sim()
    print(test.cosine_sim_cal('고수고수고고수'))
