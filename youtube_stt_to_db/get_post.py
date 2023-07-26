from django.http import JsonResponse
from myapp.similarity import recommend_songs


def get_send_urls(request):
    if request.method == 'GET':
        title_list = []
        url_list = []
        data = request.GET.get(‘movie’)
        songs = recommend_songs(data)

        for i in range(len(songs["title"])):
            title = songs["title"][i]
            title_list.append(title)

            orignal_url = songs["url"][i]
            replace_sentence = "https://www.youtube.com/watch?v="
            url = orignal_url.replace(replace_sentence, "")
            url_list.append(url)

        response = {"title": title_list, "url": url_list}
        return JsonResponse(response, content_type='application/json; charset=utf-8')
    # 결과값: url1=https://www.youtube.com/watch?v=video1&url2=https://www.youtube.com/watch?v=video2&url3=https://www.youtube.com/watch?v=video3

    else:
        return JsonResponse("잘못된 요청 방법입니다.", status=400)


def post_send_urls(request):
    if request.method == 'POST':
        url1 = "https://www.youtube.com/watch?v=video1"
        url2 = "https://www.youtube.com/watch?v=video2"
        url3 = "https://www.youtube.com/watch?v=video3"

        urls = [url1, url2, url3]

        response = "\n".join(urls)
        return JsonResponse(response, content_type='application/json; charset=utf-8')
		# 결과값: https://www.youtube.com/watch?v=video1
            # https://www.youtube.com/watch?v=video2
            # https://www.youtube.com/watch?v=video3
    
	else:
        return JsonResponse("잘못된 요청 방법입니다.", status=400)