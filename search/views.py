from django.shortcuts import render,HttpResponse
from django.views.generic.base import View
from search.models import ArticType,TechnologyType
import json
from elasticsearch import Elasticsearch
from datetime import datetime
import redis
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

client=Elasticsearch(hosts=["127.0.0.1"])

redis_cli=redis.StrictRedis()

def  IndexView(request):
    topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
    new_topn_search = []
    for x in topn_search:
        new_topn_search.append(x.decode(encoding='utf-8'))
    return render(request,'index.html',{"new_topn_search":new_topn_search})

def SearchSuggest(request):                                      # 搜索自动补全逻辑处理
    key_words = request.GET.get('s', '')# 获取到请求词
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
        key_words=request.GET.get('q',"")
        redis_cli.zincrby("search_keywords_set", 1,key_words)
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        new_topn_search=[]
        for x  in topn_search:
            # print(x.decode(encoding='utf-8'))
            new_topn_search.append(x.decode(encoding='utf-8'))
        page = request.GET.get("p", "1")

        print("当前是{0}页".format(str(page)))
        try:
            page = int(page)
        except:
            page = 1
        # if int(page)<=1:
        #     page=1
        # else:
        #     page=int(page)+1

        # jobbole_count=redis_cli.get("jobbole_count")#搜索记录次数
        # jobbole_count=int(jobbole_count)

        start_time=datetime.now()
        response=client.search(
            index="technology",
            body={
                "query": {
                  "multi_match": {
                    "query": key_words,
                    "fields": ["title","tags","content"]
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
        total_nums = response["hits"]["total"]
        if total_nums>10:
            page_nums=int(total_nums/10)+1
        else:
            page_nums=int(total_nums/10)
        all_list=[]
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
                  hit_dict["time"] = hit['_source']["time"]
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
                                                  # "jobbole_count":jobbole_count,
                                                })
# def SearchView(request):                                       # 搜索逻辑处理
#     key_words = request.GET.get('q', '')                        # 获取到请求词
#     page = request.GET.get('p', '1')                            # 获取访问页码
#     try:
#         page = int(page)
#     except:
#         page = 1
#     start_time = datetime.now()                                 # 获取当前时间
#     response = client.search(                                   # 原生的elasticsearch接口的search()方法，就是搜索，可以支持原生elasticsearch语句查询
#         index="jobbole",                                          # 设置索引名称
#         doc_type="ArticType",                                        # 设置表名称
#         body={                                                  # 书写elasticsearch语句
#             "query": {
#                 "multi_match": {                                # multi_match查询
#                     "query": key_words,                         # 查询关键词
#                     "fields": ["title", "content"]          # 查询字段
#                 }
#             },
#             "from": (page-1)*10,                                          # 从第几条开始获取
#             "size": 10,                                         # 获取多少条数据
#             "highlight": {                                      # 查询关键词高亮处理
#                 "pre_tags": ['<span class="keyWord">'],         # 高亮开始标签
#                 "post_tags": ['</span>'],                       # 高亮结束标签
#                 "fields": {                                     # 高亮设置
#                     "title": {},                                # 高亮字段
#                     "description": {}                           # 高亮字段
#                 }
#             }
#         }
#     )
#     end_time = datetime.now()                                   # 获取当前时间
#     last_time = (end_time-start_time).total_seconds()           # 结束时间减去开始时间等于用时,转换成秒
#     total_nums = response["hits"]["total"]                      # 获取查询结果的总条数
#     if (page % 10) > 0:                                         # 计算页数
#         paga_nums = int(total_nums/10)+1
#     else:
#         paga_nums = int(total_nums/10)
#     hit_list = []                                               # 设置一个列表来储存搜索到的信息，返回给html页面
#     for hit in response["hits"]["hits"]:                        # 循环查询到的结果
#         hit_dict = {}                                           # 设置一个字典来储存循环结果
#         if "title" in hit["highlight"]:                         # 判断title字段，如果高亮字段有类容
#             hit_dict["title"] = "".join(hit["highlight"]["title"])      # 获取高亮里的title
#         else:
#             hit_dict["title"] = hit["_source"]["title"]                 # 否则获取不是高亮里的title
#
#         if "description" in hit["highlight"]:                           # 判断description字段，如果高亮字段有类容
#             hit_dict["description"] = "".join(hit["highlight"]["description"])[:500]    # 获取高亮里的description
#         else:
#             hit_dict["description"] = hit["_source"]["description"]     # 否则获取不是高亮里的description
#
#         hit_dict["url"] = hit["_source"]["url"]                         # 获取返回url
#
#         hit_list.append(hit_dict)                                       # 将获取到内容的字典，添加到列表
#     return render(request, 'result.html', {"page": page,                # 当前页码
#                                            "total_nums": total_nums,    # 数据总条数
#                                            "all_hits": hit_list,        # 数据列表
#                                            "key_words": key_words,      # 搜索词
#                                            "paga_nums": paga_nums,      # 页数
#                                            "last_time": last_time       # 搜索时间
#                                            })                           # 显示页面和将列表和搜索词返回到html

