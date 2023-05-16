from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .cosine_sim import cosine_sim
from .models import Movie
import json
import pprint
# Create your views here
movie_object = cosine_sim()
@csrf_exempt
def movies(request):
    if request.method == 'POST':
        print("DATA RECEIEVED!")
        data = json.loads(request.body.decode('utf-8'))
        movie_data = data['title']
        movie_list = []
        print(movie_data)

        movie_title = movie_object.cosine_sim_cal(movie_data)
        for movie in movie_title:
            movie_list.append(movie)	
        movie_data = {
                'title' : movie_list
                }
        pprint.pprint(movie_data)

        return JsonResponse(movie_data, content_type='application/json; charset=utf-8')

    else:
        movies = Movie.objects.all()
        print(movies)
        movie_list = []
        for movie in movies:
            movie_list.append(movie)
        response_data ={
                'title' : movie_list
                }
        return JsonResponse(movie_data, content_type='application/json; charset=utf-8')
