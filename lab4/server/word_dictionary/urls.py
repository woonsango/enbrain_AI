from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('check', views.check, name='check'),
    path('keywords', views.keywords, name='keywords'),
    path('keywordCollection', views.keywordCollection, name='keywordCollection'),
    path('history', views.history, name='history'),
    path('delWord', views.delWord, name='delWord'),
    path('delKeyword', views.delKeyword, name='delKeyword')
    ]
