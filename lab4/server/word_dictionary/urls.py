from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('check', views.check, name='check'),
    path('keywords', views.keywords, name='keywords'),
    path('keywordCollection', views.keywordCollection, name='keywordCollection'),
    path('wordDictionary', views.wordDictionary, name='wordDictionary'),
]