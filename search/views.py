from django.shortcuts import render,HttpResponse

from django.views.generic.base import View
from search.models import ArticType
import json

def  indexArticle(request):
    return render(request,'index.html')

def suggestluoji(request):                                      # 搜索自动补全逻辑处理
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



