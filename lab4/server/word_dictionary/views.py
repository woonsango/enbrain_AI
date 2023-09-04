from django.shortcuts import render
from django.db import connection
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .crawling_all import getWord

# Create your views here.
def index(request):
    if request.method == 'POST':
        print(request.POST['hungry'])
    return render(request,'main/index.html')

def check(request):

    if request.method == 'POST':
        if request.POST['mode'] == 'filter':
            print(request.POST)
            print(request.POST['query'])
            print(request.POST['addDateStart'])
            print(request.POST['addDateEnd'])
            print(request.POST['modifyDateStart'])
            print(request.POST['modifyDateEnd'])
            print(request.POST['frequencyStart'])
            print(request.POST['frequencyEnd'])
            print(request.POST['selectedUsage'])

            with connection.cursor() as cursor:
                cursor.execute(f"""with url_info as 
                            (
                                select d.id , c.url, frequency
                                from (select *, row_number() over (partition by keyword_dictionary_id order by frequency desc, id) as fre_num
                                        from dictionary_crawling_info) c
                                join keyword_dictionary d on c.keyword_dictionary_id = d.id
                                where d.keyword_id = (select id
                                            from keyword
                                            where keyword = '{request.POST['query']}') and fre_num <= 3
                                order by d.id, frequency desc
                            ), 
                            freq_info as
                            (
                                select keyword_dictionary_id, sum(frequency) as frequency
                                from dictionary_crawling_info
                                group by keyword_dictionary_id
                            )
                            -- where keyword_dictionary_id = 42 ;
                            SELECT d.id, d.word, d.usable, cast(date_format(d.created_date, '%Y-%m-%d %H:%i') as char), cast(date_format(d.modified_date, '%Y-%m-%d %H:%i') as char), freq_info.frequency, TRIM(TRAILING ', ' FROM group_concat(url_info.url, ', ')) as url
                            FROM mydb.keyword_dictionary d
                            join mydb.keyword k on d.keyword_id = k.id
                            join freq_info on d.id = freq_info.keyword_dictionary_id
                            join url_info on d.id = url_info.id
                            where d.remove = 1 and
                                    k.keyword = '{request.POST['query']}' and 
                                    ((d.created_date >= case '{request.POST['addDateStart']}' when '' then '2003-04-01' else '{request.POST['addDateStart']}' end) and 
                                    (d.created_date <= case '{request.POST['addDateEnd']}' when '' then now() else '{request.POST['addDateEnd']}' end)) and 
                                    ((d.modified_date >= case '{request.POST['modifyDateStart']}' when '' then '2003-04-01' else '{request.POST['modifyDateStart']}' end) and 
                                    (d.modified_date <= case '{request.POST['modifyDateEnd']}' when '' then now() else '{request.POST['modifyDateEnd']}' end)) and 
                                    (freq_info.frequency >= case '{request.POST['frequencyStart']}' when '' then 0 else cast('{request.POST['frequencyStart']}' as unsigned) end and freq_info.frequency <= case '{request.POST['frequencyEnd']}' when '' then 999999999 else cast('{request.POST['frequencyEnd']}' as unsigned) end) and
                                    d.usable = case '{request.POST['selectedUsage']}' when 'one' then 1
															when 'zero' then 0
                                                            when 'entire' then  0 or d.usable = 1 end
                            group by d.id
                            order by 6 desc ;""")
                # query문 결과 모두를 tuple로 저장
                rows = cursor.fetchall()
                rows = [ (i[0], i[1], i[2], i[3], i[4], i[5], i[6].split(',')) for i in rows]
                # print(rows)
            return render(request, 'main/check.html', {"rows":rows, 'keyword':request.POST['query']})
        elif request.POST['mode'] == 'add':
            print(request.POST)
            with connection.cursor() as cursor:
                cursor.execute(f"""select word
                                    from keyword_dictionary
                                    where keyword_id = (select id
                                                        from keyword
                                                        where keyword = '{request.POST['query']}') ;""")
                ## 이미 있는거면 알려주기
                if request.POST["finalWord"] not in [i[0]for i in cursor.fetchall()]:
                    print(request.POST["finalWord"])
                    cursor.execute(f"""insert into keyword_dictionary (keyword_id, word, created_date, modified_date)
                                        values ((select id
                                                from keyword
                                                where keyword = '{request.POST['query']}'),
                                                '{request.POST['finalWord']}', now(), now()) ;""")
                    # 여기 부분 키워드에만 나오도록 수정하자
                    cursor.execute(f"""select id
                            from keyword_dictionary
                            where word = '{request.POST['finalWord']}' and keyword_id = (select id
                                                     										from keyword
                                                     										where keyword = '{request.POST['query']}');""")
                    keyword_dictionary_id = (cursor.fetchone())[0]
                    cursor.execute(f"""insert into dictionary_crawling_info (keyword_dictionary_id, frequency, url, created_date, modified_date)
                                    values ({keyword_dictionary_id}, 1, '{request.POST['finalUrl']}', NOW(), NOW()) ;""")
                    cursor.execute(f"""insert into dictionary_history (keyword_dictionary_id, word, created_date, modified_date)
                                    values ({keyword_dictionary_id}, 
                                            '{request.POST['finalWord']}', now(), now())""")
        elif request.POST['mode'] == 'update':
            print(request.POST)
            with connection.cursor() as cursor:
                cursor.execute(f"""select word
                                    from keyword_dictionary
                                    where keyword_id = (select id
                                                        from keyword
                                                        where keyword = '민법') ;""")
                result = [i[0] for i in cursor.fetchall()]
                if request.POST['finalWord'] in result and request.POST['finalWord'] != request.POST['beforeWord']:
                    print('이미 존재하는 단어입니다')
                else: 
                    cursor.execute(f"""update keyword_dictionary
                                    set word = '{request.POST['finalWord']}', usable = {request.POST['finalUsage']}, modified_date = now()
                                    where id = (select tmp.id
                                                from (select id 
                                                        from keyword_dictionary
                                                        where word = '{request.POST['beforeWord']}' and keyword_id = (select id
                                                                                            from keyword
                                                                                            where keyword = '{request.POST['query']}')) tmp);""")
                    print('update success')
                    cursor.execute(f"""insert into dictionary_history (keyword_dictionary_id, word, created_date, modified_date)
                                    values ((select id
                                            from keyword_dictionary
                                            where word = '{request.POST['finalWord']}'and keyword_id = (select id
                                                                                        from keyword
                                                                                        where keyword = '{request.POST['query']}')), 
                                            '{request.POST['finalWord']}', now(), now()) ;""")
        elif request.POST['mode'] == 'delete' :
            print(request.POST)
            with connection.cursor() as cursor:
                keyword = request.POST['query']
                for word in request.POST['delete_word'].split(','):
                    print(word)
                    cursor.execute(f"""update keyword_dictionary
                                        set remove = 0, modified_date = now()
                                        where id = (select tmp.id
                                                    from (select id
                                                            from keyword_dictionary
                                                            where word = '{word}' and keyword_id = (select id
                                                                                                from keyword
                                                                                                where keyword = '{keyword}')) as tmp);""")
                    cursor.execute(f"""insert into dictionary_history (keyword_dictionary_id, word, created_date, modified_date)
                                        values ((select id
                                                from keyword_dictionary
                                                where word = '{word}'and keyword_id = (select id
                                                                                            from keyword
                                                                                            where keyword = '{keyword}')), 
                                                '삭제됨', now(), now()) ;""")
                    

        
        word = request.POST['query']
        page = 1
    else:
        word = request.GET.get('query')
        page = request.GET.get('page')

    #db 불러오기
    with connection.cursor() as cursor:
        # query문 실행(keyword table 가져오기)
        cursor.execute(f"""with url_info as 
                            (
                                select d.id , c.url, frequency
                                from (select *, row_number() over (partition by keyword_dictionary_id order by frequency desc, id) as fre_num
                                        from dictionary_crawling_info) c
                                join keyword_dictionary d on c.keyword_dictionary_id = d.id
                                where d.keyword_id = (select id
                                            from keyword
                                            where keyword = '{word}') and fre_num <= 3
                                order by d.id, frequency desc
                            ), 
                            freq_info as
                            (
                                select keyword_dictionary_id, sum(frequency) as frequency
                                from dictionary_crawling_info
                                group by keyword_dictionary_id
                            )
                            -- where keyword_dictionary_id = 42 ;
                            SELECT d.id, d.word, d.usable, cast(date_format(d.created_date, '%Y-%m-%d %H:%i') as char), cast(date_format(d.modified_date, '%Y-%m-%d %H:%i') as char), freq_info.frequency, TRIM(TRAILING ', ' FROM group_concat(url_info.url, ', ')) as url
                            FROM mydb.keyword_dictionary d
                            join mydb.keyword k on d.keyword_id = k.id
                            join freq_info on d.id = freq_info.keyword_dictionary_id
                            join url_info on d.id = url_info.id
                            where d.remove = 1 and k.keyword = '{word}'
                            group by d.id
                            order by 6 desc ;""")
        
        # query문 결과 모두를 tuple로 저장
        rows = cursor.fetchall()
        rows = [ (i[0], i[1], i[2], i[3], i[4], i[5], i[6].split(',')) for i in rows]

        paginator = Paginator(rows, 2000)

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page = 1
            page_obj = paginator.page(page)
        except EmptyPage:
            page = paginator.num_pages # 가장 마지막 페이지
            page_obj = paginator.page(page)

    # print(rows)

    # return render(request, 'main/check.html', {'rows': rows, 'keyword':word})
    return render(request, 'main/check.html', {'rows': page_obj, 'keyword':word, 'paginator': paginator})

def history(request):

    keyword = request.GET.get('keyword')
    word = request.GET.get('word')
    print(keyword)
    print(word)
    with connection.cursor() as cursor:
        cursor.execute(f"""select word, usable, cast(date_format(created_date, '%Y-%m-%d %H:%i') as char), cast(date_format(modified_date, '%Y-%m-%d %H:%i') as char)
                            from dictionary_history
                            where keyword_dictionary_id = (select id 
                                                            from keyword_dictionary
                                                            where word = '{word}' and keyword_id = (select id
                                                                                                    from keyword
                                                                                                    where keyword = '{keyword}'))
                            order by created_date desc;""")
        rows = cursor.fetchall()
        print(rows)
            

    return render(request, 'main/history.html', {'rows': rows, 'keyword': keyword, 'word':word})

def keywordCollection(request):
    print(request.GET.get('query'))
    keyword = ''
    # get 요청이 있을 때 실행
    if request.GET.get('query'):
        # get 요청 확인(keyword가 qeury string으로 들어옴)
        keyword = request.GET.get('query')
        print(keyword)
        # db 접근
        with connection.cursor() as cursor:
            # 존재하는 키워드 출력 query
            cursor.execute(f"""select keyword
                            from keyword ;""")
            exit_keyword = [i[0]for i in cursor.fetchall()]
            print(exit_keyword)
            # 이미 존재하는 키워드일 때 실행
            if keyword in exit_keyword:
                return render(request, 'main/keywordCollection.html', {"keyword": keyword, "exit_keyword": exit_keyword})
        # 크롤링하기
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
            for word in crawling_data:
                cursor.execute(f"""insert into keyword_dictionary (keyword_id, word, created_date, modified_date)
                                        values ({keyword_id}, '{word[0]}', NOW(), NOW()) ; """)
                # keyword에 대한 단어 가져오도록 변경
                cursor.execute(f"""select id
                            from keyword_dictionary
                            where word = '{word[0]}' and keyword_id = {keyword_id};""")
                keyword_dictionary_id = (cursor.fetchone())[0]
                # print(word)
                for url_frequency in range(len(word[1])):
                    # print(word[1][url_frequency])
                    # print(word[2][url_frequency])
                    cursor.execute(f"""insert into dictionary_crawling_info (keyword_dictionary_id, frequency, url, created_date, modified_date)
                                    values ({keyword_dictionary_id}, {word[1][url_frequency]}, '{word[2][url_frequency]}', NOW(), NOW()) ;""")
                cursor.execute(f"""insert into dictionary_history (keyword_dictionary_id, word, created_date, modified_date)
                                values ({keyword_dictionary_id}, 
                                        '{word[0]}', now(), now())""")
       
    return render(request, 'main/keywordCollection.html', {"keyword": keyword})

def keywords(request):

    if request.method == 'POST':
        print(request.POST['mode'])
        if request.POST['mode'] == 'filter':
            print(request.POST)
            print(request.POST['addDateStart'])
            print(request.POST['addDateEnd'])
            print(request.POST['modifyDateStart'])
            print(request.POST['modifyDateEnd'])
            with connection.cursor() as cursor:
                cursor.execute(f"""select keyword, cast(date_format(created_date, '%Y-%m-%d %H:%i') as char), cast(date_format(modified_date, '%Y-%m-%d %H:%i') as char)
                                    from keyword
                                    where remove = 1 and 
                                        ((created_date >= case '{request.POST['addDateStart']}' when '' then '2003-04-01' else '{request.POST['addDateStart']}' end) and 
                                        (created_date <= case '{request.POST['addDateEnd']}' when '' then now() else '{request.POST['addDateEnd']}' end)) and 
                                        ((modified_date >= case '{request.POST['modifyDateStart']}' when '' then '2003-04-01' else '{request.POST['modifyDateStart']}' end) and 
                                        (modified_date <= case '{request.POST['modifyDateEnd']}' when '' then now() else '{request.POST['modifyDateEnd']}' end));""")
                rows = cursor.fetchall()
                print(rows)
                return render(request, 'main/keywords.html', {"words":rows})
        elif request.POST['mode'] == 'add':
            print(request.POST)
            print(request.POST['finalWord'])
            with connection.cursor() as cursor:
                # 존재하는 키워드 출력 query
                cursor.execute(f"""select keyword
                                from keyword ;""")
                exit_keyword = [i[0]for i in cursor.fetchall()]
                print(exit_keyword)
                # 이미 존재하는 키워드일 때 실행
                if request.POST['finalWord'] not in exit_keyword:
                    cursor.execute(f"""INSERT INTO keyword (keyword, created_date, modified_date)
                                VALUES ("{request.POST['finalWord']}", NOW(), NOW()) ;""")
        elif request.POST['mode'] == 'delete':
            print(request.POST)
            with connection.cursor() as cursor:
                for keyword in request.POST['delete_word'].split(','):
                    print(keyword)
                    cursor.execute(f"""update keyword
                                        set remove = 0, modified_date = now()
                                        where keyword = '{keyword}' ;""")
                        

    #db 불러오기
    with connection.cursor() as cursor:
        # query문 실행(keyword table 가져오기)
        cursor.execute(f"""SELECT keyword, cast(date_format(created_date, '%Y-%m-%d %H:%i') as char), cast(date_format(modified_date, '%Y-%m-%d %H:%i') as char)
                            FROM keyword
                            where remove = 1 ;""")
        # query문 결과 모두를 tuple로 저장
        rows = cursor.fetchall()
        # print(rows)

    return render(request, 'main/keywords.html', {"words":rows})


def delWord(request):

    if request.method == 'POST':
        keyword = request.POST['keyword']
        re_word = request.POST['re_word']
        print(keyword)
        print(re_word)
        with connection.cursor() as cursor:
            cursor.execute(f"""update keyword_dictionary
                                set remove = 1, modified_date = now()
                                where id = (select tmp.id
                                            from (select id
                                                    from keyword_dictionary
                                                    where word = '{re_word}' and keyword_id = (select id
                                                                                        from keyword
                                                                                        where keyword = '{keyword}')) as tmp);""")
            cursor.execute(f"""insert into dictionary_history (keyword_dictionary_id, word, created_date, modified_date)
                                            values ((select id
                                                    from keyword_dictionary
                                                    where word = '{re_word}'and keyword_id = (select id
                                                                                                from keyword
                                                                                                where keyword = '{keyword}')), 
                                                    '복구됨', now(), now()) ;""")
    else:
        keyword = request.GET.get('keyword')
    with connection.cursor() as cursor:
        cursor.execute(f"""with url_info as 
                            (
                                select d.id , c.url, frequency
                                from (select *, row_number() over (partition by keyword_dictionary_id order by frequency desc, id) as fre_num
                                        from dictionary_crawling_info) c
                                join keyword_dictionary d on c.keyword_dictionary_id = d.id
                                where d.keyword_id = (select id
                                            from keyword
                                            where keyword = '{keyword}') and fre_num <= 3
                                order by d.id, frequency desc
                            ), 
                            freq_info as
                            (
                                select keyword_dictionary_id, sum(frequency) as frequency
                                from dictionary_crawling_info
                                group by keyword_dictionary_id
                            )
                            -- where keyword_dictionary_id = 42 ;
                            SELECT d.id, d.word, d.usable, cast(date_format(d.modified_date, '%Y-%m-%d %H:%i') as char), freq_info.frequency, TRIM(TRAILING ', ' FROM group_concat(url_info.url, ', ')) as url
                            FROM mydb.keyword_dictionary d
                            join mydb.keyword k on d.keyword_id = k.id
                            join freq_info on d.id = freq_info.keyword_dictionary_id
                            join url_info on d.id = url_info.id
                            where d.remove = 0 and k.keyword = '{keyword}'
                            group by d.id
                            order by 5 desc ;""")
        # query문 결과 모두를 tuple로 저장
        rows = cursor.fetchall()
        rows = [ (i[0], i[1], i[2], i[3], i[4], i[5].split(',')) for i in rows]

        
    return render(request, 'main/delWord.html', {'rows': rows, 'keyword':keyword})

def delKeyword(request):

    if request.method == 'POST':
        re_keyword = request.POST['re_keyword']
        with connection.cursor() as cursor:
            cursor.execute(f"""update keyword
                                set remove = 1, modified_date = now()
                                where keyword = '{re_keyword}' ;""")

    with connection.cursor() as cursor:
        cursor.execute(f"""SELECT keyword, cast(date_format(modified_date, '%Y-%m-%d %H:%i') as char)
                            FROM keyword
                            where remove = 0 ;""")
        rows = cursor.fetchall()
    return render(request, 'main/delKeyword.html', {'rows':rows})
