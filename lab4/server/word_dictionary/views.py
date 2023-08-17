from django.shortcuts import render
from django.db import connection
from .crawling_all import getWord

# Create your views here.
def index(request):
    return render(request,'main/index.html')

def check(request):

    word = request.GET.get('query')

    #db 불러오기
    with connection.cursor() as cursor:
        # query문 실행(keyword table 가져오기)
        cursor.execute(f"""with tmp as
                        (
                        select keyword_dictionary_id, sum(frequency) as frequency
                        from dictionary_crawling_info
                        group by keyword_dictionary_id
                        )
                        -- where keyword_dictionary_id = 42 ;
                        SELECT d.id, d.word, d.usable, cast(cast(d.created_date as date) as char), cast(cast(d.modified_date as date) as char), tmp.frequency
                        FROM mydb.keyword_dictionary d
                        join mydb.keyword k on d.keyword_id = k.id
                        join tmp on d.id = tmp.keyword_dictionary_id
                        where k.keyword = '{word}' ;""")
        # query문 결과 모두를 tuple로 저장
        rows = cursor.fetchall()

    print(word)
    print(rows)

    print(rows)


    return render(request, 'main/check.html', {'rows': rows})

def history(request):

    return render(request, 'main/history.html')

def keywordCollection(request):
    print(request.GET.get('query'))
    keyword = ''
    if request.GET.get('query'):
        keyword = request.GET.get('query')
        print(keyword)
        with connection.cursor() as cursor:
            cursor.execute(f"""select keyword
                            from keyword ;""")
            exit_keyword = [i[0]for i in cursor.fetchall()]
            print(exit_keyword)
            if keyword in exit_keyword:
                return render(request, 'main/keywordCollection.html', {"keyword": keyword, "exit_keyword": exit_keyword})
        crawling_data = getWord(keyword)
        with connection.cursor() as cursor:
            cursor.execute(f"""INSERT INTO keyword (keyword, created_date, modified_date)
                    VALUES ("{keyword}", NOW(), NOW()) ;""")
            cursor.execute(f"""select id
                            from keyword
                            where keyword='{keyword}' ;
                            """)
            keyword_id = (cursor.fetchone())[0]
            print(keyword_id)
            for key in crawling_data:
                for data in crawling_data[key]:
                    # print(f'data: {crawling_data[key][data]}')
                    for word in crawling_data[key][data]:
                        print(word)
                    # print(f'data[0]: {data[0]}')
                        cursor.execute(f"""insert into keyword_dictionary (keyword_id, word, created_date, modified_date)
                                        values ({keyword_id}, '{word[0]}', NOW(), NOW()) ; """)
                        cursor.execute(f"""select id
                                    from keyword_dictionary
                                    where word = '{word[0]}' ;""")
                        keyword_dictionary_id = (cursor.fetchone())[0]
                    # print(f'data[1]: {data[1]}')
                        cursor.execute(f"""insert into dictionary_crawling_info (keyword_dictionary_id, frequency, url, created_date, modified_date)
                                    values ({keyword_dictionary_id}, {word[1]}, '{word[2]}', NOW(), NOW()) ;""")

    return render(request, 'main/keywordCollection.html', {"keyword": keyword})

def keywords(request):

    #db 불러오기
    with connection.cursor() as cursor:
        # query문 실행(keyword table 가져오기)
        cursor.execute("""SELECT keyword, cast(cast(created_date as date) as char), cast(cast(modified_date as date) as char)
                        FROM keyword ;""")
        # query문 결과 모두를 tuple로 저장
        rows = cursor.fetchall()
        # print(rows)

    return render(request, 'main/keywords.html', {"words":rows})