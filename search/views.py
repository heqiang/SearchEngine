from django.shortcuts import render,HttpResponse
from django.views.generic.base import View
from search.models import ArticType
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
    print(topn_search)
    for x in topn_search:
        print(x.decode(encoding='utf-8'))
        new_topn_search.append(x.decode(encoding='utf-8'))
    return render(request,'index.html',{"new_topn_search":new_topn_search})

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
        redis_cli.zincrby("search_keywords_set", 1,key_words)
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        new_topn_search=[]
        print(topn_search)
        for x  in topn_search:
            print(x.decode(encoding='utf-8'))
            new_topn_search.append(x.decode(encoding='utf-8'))
        page = request.GET.get("p", "1")

        try:
            page = int(page)
        except:
            page = 1
        if page==0:
            page=1

        # jobbole_count=redis_cli.get("jobbole_count")#搜索记录次数
        # jobbole_count=int(jobbole_count)

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
                "from": (page-1)+10,
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

                  hit_dict["create_date"] = hit['_source']["create_date"]
                  hit_dict["url"] = hit['_source']["link_url"]
                  hit_dict["score"] = hit["_score"]
                  # 将内容加入到list
                  all_list.append(hit_dict)


        return render(request, "result.html", {"all_list":all_list,
                                                 "key_words":key_words,
                                                 "total_nums":total_nums,
                                                 "page":page,
                                                 "page_nums":page_nums,
                                                 "last_seconds":last_seconds,
                                                  "topn_search": new_topn_search,
                                                  # "jobbole_count":jobbole_count,
                                                })
        #