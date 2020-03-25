from django.shortcuts import render,HttpResponse
from  django.http import JsonResponse
from django.shortcuts import  redirect
from search.models import TechnologyType,AnswerType
import json
from elasticsearch import Elasticsearch
from datetime import datetime
import redis
import pymysql
from user import  models

current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
db = pymysql.connect("localhost","root","1422127065","bishe" ,charset="utf8" )
cursor = db.cursor()
client=Elasticsearch(hosts=["127.0.0.1"])
redis_cli=redis.StrictRedis()

def  IndexView(request):
    topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
    new_topn_search = []
    for x in topn_search:
        new_topn_search.append(x.decode(encoding='utf-8'))
    return render(request,'index.html',{"new_topn_search":new_topn_search})

#跳转搜索结果页面时 如果登录了 就以登录者搜索的最新一条为搜索返回内容，否则以热搜的最新一条返回搜索结果
def Result(requests):
    #mysql  用户操作组
    if requests.session.get('is_login', None):
        user_id = requests.session.get('user_id')
        res=models.Search.objects.filter(user_id=user_id).values("searchtitle","searchtime").order_by("-searchtime")
        if  res:
            key_words=res[0]['searchtitle']
        else:
            res = models.Hot_search.objects.values("Hot_searchtitle", "Hot_searchtime").order_by("-Hot_searchtime")
            if res:
                key_words = res[0]['Hot_searchtitle']
    else:
        res=models.Hot_search.objects.values("Hot_searchtitle","Hot_searchtime").order_by("-Hot_searchtime")
        if res:
            key_words=res[0]['Hot_searchtitle']
    models.Hot_search.objects.create(Hot_searchtitle=key_words)
    redis_cli.zincrby("search_keywords_set", 1, key_words)
    topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)

    # 热门搜索  redis数据库组
    new_topn_search = []
    for x in topn_search:
        new_topn_search.append(x.decode(encoding='utf-8'))

    es_category = requests.GET.get('s_type', '')
    page = requests.GET.get("p", "2")
    try:
        page = int(page)
    except:
        page = 1
    start_time = datetime.now()
    response = client.search(
        index="{0}".format(es_category),
        body={
            "query": {
                "multi_match": {
                    "query": key_words,
                    "fields": ["title^3", "tags", "content"]
                }
            },
            "from": (page - 1) * 10,  # 从多少条开始获取
            "size": 10,  # 获取多少条数据
            "highlight": {  # 查询关键词高亮处理
                # 样式控制
                "pre_tags": ['<span class="keyWord">'],  # 高亮开始标签
                "post_tags": ['</span>'],  # 高亮结束标签
                "fields": {  # 高亮设置
                    "title": {},  # 高亮字段
                    "content": {}  # 高亮字段
                }
            }
        }
    )
    end_time = datetime.now()
    last_seconds = (end_time - start_time).total_seconds()
    total_nums = response["hits"]["total"]  # 返回总的条数
    if total_nums > 10:
        page_nums = int(total_nums / 10) + 1
    else:
        page_nums = int(total_nums / 10)
    all_list = []
    # 10条
    for hit in response["hits"]["hits"]:
        hit_dict = {}
        if "highlight" in hit:
            if "title" in hit["highlight"]:
                hit_dict["title"] = "".join(hit["highlight"]["title"])
            else:
                hit_dict["title"] = ''.join(hit["_source"]["title"])
            if "content" in hit["highlight"]:
                hit_dict["content"] = "".join(hit["highlight"]["content"][:500])
            else:
                hit_dict["content"] = "".join(hit["_source"]["content"][:500])
            hit_dict["time"] = hit['_source']["time"]
            hit_dict["url"] = hit['_source']["link_url"]
            hit_dict["score"] = hit["_score"]
            hit_dict["source"] = hit['_source']["source"]
            # 将内容加入到list
            all_list.append(hit_dict)
    return render(requests, "result.html", {"all_list": all_list,
                                           "key_words": key_words,
                                           "total_nums": total_nums,  # 数据总条数
                                           "page": page,  # 当前页码
                                           "page_nums": page_nums,  # 页数
                                           "last_seconds": last_seconds,
                                           "topn_search": new_topn_search,
                                           })


 # 搜索自动补全逻辑处理
def SearchSuggest(request):
    es_category=request.GET.get('s_type','')
    if es_category=="question":
        key_words = request.GET.get('s', '')  # 获取到请求词
        re_datas = []
        if key_words:
            s = AnswerType.search()
            s = s.suggest('my_suggest', key_words, completion={
                "field": "suggest", "fuzzy": {
                    "fuzziness": 2
                },
                "size": 10
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source["title"])
    else:
        key_words = request.GET.get('s', '') # 获取到请求词
        re_datas = []
        if key_words:
            s = TechnologyType.search()
            s = s.suggest('my_suggest', key_words, completion={
                "field": "suggest", "fuzzy": {
                    "fuzziness": 2
                },
                "size": 10
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source["title"])
    return HttpResponse(json.dumps(re_datas), content_type="application/json")

def SearchView(request):
        es_category = request.GET.get('s_type', '')
        key_words=request.GET.get('q',"")
        if request.session.get('is_login',None):
            user_id=request.session.get('user_id')
            models.Search.objects.create(searchtitle=key_words,user_id=user_id)
        models.Hot_search.objects.create(Hot_searchtitle=key_words)
        redis_cli.zincrby("search_keywords_set", 1,key_words)
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)

        #热门搜索
        new_topn_search=[]
        for x  in topn_search:
            new_topn_search.append(x.decode(encoding='utf-8'))
        page = request.GET.get("p", "2")
        page=str(int(page)+1)
        try:
            page = int(page)
        except:
            page = 1
        start_time=datetime.now()
        response=client.search(
            index="{0}".format(es_category),
            body={
                "query": {
                  "multi_match": {
                    "query": key_words,
                    "fields": ["title^3","tags","content"] #title设置 是其他符合关键词的字段的三倍
                  }
              },
                "from": (page-1)*10, #从多少条开始获取
                "size":10,#获取多少条数据
                "highlight": {  # 查询关键词高亮处理
                    #样式控制
                    "pre_tags": ['<span class="keyWord">'],  # 高亮开始标签
                    "post_tags": ['</span>'],  # 高亮结束标签
                    "fields": {  # 高亮设置
                        "title": {},  # 高亮字段
                        "content": {}  # 高亮字段
                    }
                }
            }
        )
        end_time=datetime.now()
        last_seconds=(end_time-start_time).total_seconds()
        total_nums = response["hits"]["total"] #返回总的条数
        if total_nums>10:
            page_nums=int(total_nums/10)+1
        else:
                page_nums=int(total_nums/10)
        all_list=[]
        #10条
        for hit  in response["hits"]["hits"]:
              hit_dict = {}
              if "highlight" in hit:
                  if "title" in hit["highlight"]:
                        hit_dict["title"] = "".join(hit["highlight"]["title"])
                  else:
                        hit_dict["title"] = ''.join(hit["_source"]["title"])
                  if "content" in hit["highlight"]:
                      hit_dict["content"] = "".join(hit["highlight"]["content"][:500])
                  else:
                      hit_dict["content"] = "".join(hit["_source"]["content"][:500])
                  article_time= hit['_source']["time"]
                  hit_dict["time"]=article_time.split("T")[0]
                  hit_dict["url"] = hit['_source']["link_url"]
                  hit_dict["score"] = hit["_score"]
                  hit_dict["source"]=hit['_source']["source"]
                  # 将内容加入到list
                  all_list.append(hit_dict)
        return render(request, "result.html", {"all_list":all_list,
                                                 "key_words":key_words,
                                                 "total_nums":total_nums,#数据总条数
                                                 "page":page,#当前页码
                                                 "page_nums":page_nums,#页数
                                                 "last_seconds":last_seconds,
                                                  "topn_search": new_topn_search,
                                                })

def  Search_history(requests):
    user_id = requests.session.get('user_id')
    res=models.Search.objects.filter(user_id=user_id).values("id","searchtitle","searchurl","searchtime")
    dict=[]
    for x in res:
        data={}
        data['id'] = x['id']
        data['title']=x['searchtitle']
        data['time']=x['searchtime'].strftime('%Y-%m-%d %H:%M:%S')
        data['url']=x['searchurl']
        dict.append(data)
    return JsonResponse({"code": 0, "message:": "", "count": len(res),
                         "data":dict})

#删除搜索历史记录
def  delete_search(requests):
     if requests.is_ajax():
         id=requests.POST['id']
         res=models.Search.objects.filter(id=id).delete()
         if res:
             return JsonResponse({"message":"ok"})
         else:
             return JsonResponse({"message":"error"})
def  collect_history(requests):
    user_id = requests.session.get('user_id')
    res = models.Collect.objects.filter(user_id=user_id).values("id", "collecttitle", "collecturl", "collecttime")
    dict = []
    for x in res:
        data = {}
        data['id'] = x['id']
        data['title'] = x['collecttitle']
        data['time'] = x['collecttime'].strftime('%Y-%m-%d %H:%M:%S')
        data['url'] = x['collecturl']
        dict.append(data)

    return JsonResponse({"code": 0, "message:": "", "count": len(res),
                         "data": dict})

def  delete_collect(requests):
    if requests.is_ajax():
        id = requests.POST['id']
        res = models.Collect.objects.filter(id=id).delete()
        if res:
            return JsonResponse({"message": "ok"})
        else:
            return JsonResponse({"message": "error"})

