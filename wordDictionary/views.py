from django.shortcuts import render
from .models import Post
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def post_list(request):
    post_list = Post.objects.all()
    page = request.GET.get('page')   # 현재 페이지

    paginator = Paginator(post_list, 1000)   # 한 페이지당 1000개의 행

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:   # url에 페이지 번호가 들어오지 않을 경우 1페이지로 인식하도록
        page = 1
        page_obj = paginator.page(page)
    except EmptyPage:   # url에 페이지 번호를 너무 크게 입력할 경우
        page = paginator.num_pages
        page_obj = paginator.page(page)

    # 페이지 번호 주변에 보여줄 페이지 번호들
    leftIndex = (int(page) - 2)
    if leftIndex < 1:
        leftIndex = 1
    
    rightIndex = (int(page) + 2)
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages
    
    custom_range = range(leftIndex, rightIndex + 1)

    
    return render(request, 'main/check.html', {'post_list': post_list, 'page_obj': page_obj, 'paginator': paginator, 'custom_range': custom_range})