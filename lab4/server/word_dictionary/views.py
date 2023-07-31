from django.shortcuts import render
from django.db import connection

# Create your views here.
def index(request):
    return render(request,'main/index.html')

def check(request):

    word = request.GET.get('query')

    #db 불러오기
    with connection.cursor() as cursor:
        # query문 실행(keyword table 가져오기)
        cursor.execute(f"""SELECT d.word, d.usable, cast(d.created_date as char), cast(d.modified_date as char)
                        FROM mydb.keyword_dictionary d
                        join mydb.keyword k on d.keyword_id = k.id ;
                        where keyword_id = {8};""")
        # query문 결과 모두를 tuple로 저장
        rows = cursor.fetchall()

    print(rows)


    return render(request, 'main/check.html', {'rows': rows})

def wordDictionary(request):
    return render(request, 'main/wordDictionary.html')

def keywordCollection(request):
    return render(request, 'main/keywordCollection.html')

def keywords(request):

    #db 불러오기
    with connection.cursor() as cursor:
        # query문 실행(keyword table 가져오기)
        cursor.execute("""SELECT keyword 
                        FROM keyword ;""")
        # query문 결과 모두를 tuple로 저장
        rows = cursor.fetchall()
        # print(rows)

    return render(request, 'main/keywords.html', {"rows":rows})