from django.shortcuts import render,HttpResponse
from django.views.generic.base import View
from search.models import ArticType
import json
from elasticsearch import Elasticsearch
from datetime import datetime
import redis

client=Elasticsearch(hosts=["127.0.0.1"])

redis_cli=redis.StrictRedis()

def  IndexView(request):
    return render(request,'index.html')

def SearchSuggest(request):                                      # 搜索自动补全逻辑处理
    key_words = request.GET.get('s', '')                        # 获取到请求词
    re_datas = []
    if key_words:
        s = ArticType.search()
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
        key_words=request.GET.get('q',"")
        print(key_words)
        page = request.GET.get("p", "1")
        print("当前页码是：")
        print(page)
        try:
            page = int(page)
        except:
            page = 1

        jobbole_count=redis_cli.get("jobbole_count")#搜索记录次数
        jobbole_count=int(jobbole_count)

        start_time=datetime.now()
        response=client.search(
            index="jobbole",
            body={
                "query": {
                  "multi_match": {
                    "query": key_words,
                    "fields": ["title","tags","content"]
                  }
              },
                "from": (page-1)*10,
                "size":10,
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
        total_nums = response["hits"]["total"]
        print()
        if total_nums>10:
            page_nums=int(total_nums/10)+1
        else:
            page_nums=int(total_nums/10)
        hit_list=[]
        for hit  in response["hits"]["hits"]:
              hit_dict = {}
              if "highlight" in hit:
                  if "title" in hit["highlight"]:
                        hit_dict["title"] = hit["highlight"]["title"][0]
                  else:
                        hit_dict["title"] = hit["_source"]["title"][0]

                  if "content" in hit["highlight"]:
                      hit_dict["content"] = "".join(hit["highlight"]["content"][:500])
                  else:
                      hit_dict["content"] = "".join(hit["_source"]["content"][:500])

                  hit_dict["create_date"] = hit['_source']["create_date"]
                  hit_dict["url"] = hit['_source']["link_url"]
                  hit_dict["score"] = hit["_score"]
                  # 将内容加入到list
                  hit_list.append(hit_dict)
        return render(request, "result.html", {"all_list":hit_list,
                                                 "key_words":key_words,
                                                 "total_nums":total_nums,
                                                 "page":page,
                                                 "page_nums":page_nums,
                                                 "last_seconds":last_seconds,
                                                  "jobbole_count":jobbole_count,
                                                    # "top_search":top_search,
                                                })
# import json
# from django.shortcuts import render
# from django.views.generic.base import View
# from search.models import ArticType
# from django.http import HttpResponse
# from elasticsearch import Elasticsearch
# from datetime import datetime
# import redis
#
# client = Elasticsearch(hosts=["127.0.0.1"])
# redis_cli = redis.StrictRedis()
#
#
# def IndexView(request):
#     #首页
#         topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
#         return render(request, "index.html", {"topn_search":topn_search})
#
# # Create your views here.
# def SearchSuggest(request):
#         key_words = request.GET.get('s','')
#         re_datas = []
#         if key_words:
#             s = ArticType.search()
#             s = s.suggest('my_suggest', key_words, completion={
#                 "field":"suggest", "fuzzy":{
#                     "fuzziness":2
#                 },
#                 "size": 10
#             })
#             suggestions = s.execute_suggest()
#             for match in suggestions.my_suggest[0].options:
#                 source = match._source
#                 re_datas.append(source["title"])
#         return HttpResponse(json.dumps(re_datas), content_type="application/json")
#
#
# def SearchView(request):
#
#         key_words = request.GET.get("q","")
#         s_type = request.GET.get("s_type", "article")
#
#         # redis_cli.zincrby("search_keywords_set", key_words)
#
#         # topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
#         page = request.GET.get("p", "1")
#         try:
#             page = int(page)
#         except:
#             page = 1
#
#         jobbole_count = redis_cli.get("jobbole_count")
#         start_time = datetime.now()
#         response = client.search(
#             index= "jobbole",
#             body={
#                 "query":{
#                     "multi_match":{
#                         "query":key_words,
#                         "fields":["tags", "title", "content"]
#                     }
#                 },
#                 "from":(page-1)*10,
#                 "size":10,
#                 "highlight": {
#                     "pre_tags": ['<span class="keyWord">'],
#                     "post_tags": ['</span>'],
#                     "fields": {
#                         "title": {},
#                         "content": {},
#                     }
#                 }
#             }
#         )
#
#         end_time = datetime.now()
#         last_seconds = (end_time-start_time).total_seconds()
#         total_nums = response["hits"]["total"]
#         if (page%10) > 0:
#             page_nums = int(total_nums/10) +1
#         else:
#             page_nums = int(total_nums/10)
#         hit_list = []
#         for hit in response["hits"]["hits"]:
#             hit_dict = {}
#             if "title" in hit["highlight"]:
#                 hit_dict["title"] = "".join(hit["highlight"]["title"])
#             else:
#                 hit_dict["title"] = hit["_source"]["title"]
#             if "content" in hit["highlight"]:
#                 hit_dict["content"] = "".join(hit["highlight"]["content"])[:500]
#             else:
#                 hit_dict["content"] = hit["_source"]["content"][:500]
#
#             hit_dict["create_date"] = hit["_source"]["create_date"]
#             hit_dict["url"] = hit["_source"]["link_url"]
#             hit_dict["score"] = hit["_score"]
#
#             hit_list.append(hit_dict)
#
#         return render(request, "result.html", {"page":page,
#                                                "all_hits":hit_list,
#                                                "key_words":key_words,
#                                                "total_nums":total_nums,
#                                                "page_nums":page_nums,
#                                                "last_seconds":last_seconds,
#                                                "jobbole_count":jobbole_count,
#                                                # "topn_search":topn_search
#                                                })
# #