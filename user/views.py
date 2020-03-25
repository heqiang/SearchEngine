from django.shortcuts import render
from django.shortcuts import  redirect
from user import  models
from user import forms
import hashlib
from django.http import JsonResponse,HttpResponse
import jieba.analyse
from collections import Counter
import re
import pymysql
import redis
from elasticsearch import Elasticsearch
from datetime import datetime
import io
from backend import check_code as CheckCode


db = pymysql.connect("localhost","root","1422127065","bishe" ,charset="utf8" )
cursor = db.cursor()
client=Elasticsearch(hosts=["127.0.0.1"])
redis_cli=redis.StrictRedis()

#验证码
def check_code(request):
    stream = io.BytesIO()
    # img图片对象,code在图像中写的内容
    img, code = CheckCode.create_validate_code()
    img.save(stream, "png")
    # 图片页面中显示,立即把session中的CheckCode更改为目前的随机字符串值
    request.session["CheckCode"] = code
    print("进入验证码")
    return HttpResponse(stream.getvalue())
    # 代码：生成一张图片，在图片中写文件
    # request.session['CheckCode'] =  图片上的内容
    # 自动生成图片，并且将图片中的文字保存在session中
    # 将图片内容返回给用户

#登录逻辑
def login(requests):
    if requests.session.get('is_login', None):  # 不允许重复登录
        username = requests.session.get('user_name')
        user_id = requests.session.get('user')
        return redirect('/result/')
    if requests.method=="POST":
        input_code = requests.POST.get('check_code').upper()
        login_form=forms.UserForm(requests.POST)
        message="请检查填写的内容！"
        if login_form.is_valid():
            username=login_form.cleaned_data.get("username")
            password = hashlib.sha1(login_form.cleaned_data.get("password").encode('utf-8')).hexdigest()
            try:
                user= models.User.objects.get(username=username)
            except:
                message="用户不存在"
                return render(requests,'login/login.html',locals())
            if user.password==password:
                #向session字典中写入用户状态和数据
                requests.session['is_login']=True
                requests.session['user_id']=user.id
                requests.session['user_name']=user.username
                requests.session['sex']=user.sex
                requests.session['email']=user.email

                if requests.session['CheckCode'].upper()==input_code:

                    return render(requests, "Personal/personData.html" )

                else:
                    message="验证码错误,请从新输入"
                    return render(requests, 'login/login.html', locals())
            else:
                message='密码错误'
                return render(requests,'login/login.html',locals())
        else:
            return render(requests,'login/login.html',locals())
    login_form=forms.UserForm()
    return  render(requests,'login/login.html',locals())
#注册
def register(request):
    if request.session.get('is_login', None):
        return redirect('/index/')
    if request.method == 'POST':
        input_code = request.POST.get('check_code').upper()
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')
            sex = register_form.cleaned_data.get('sex')
            if password1 != password2:
                message = '两次输入的密码不同！'
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(username=username)
                if same_name_user:
                    message = '用户名已经存在'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:
                    message = '该邮箱已经被注册了！'
                    return render(request, 'login/register.html', locals())
                if request.session['CheckCode'].upper()==input_code:
                        new_user = models.User()
                        new_user.username = username
                        new_user.password = hashlib.sha1(password1.encode('utf-8')).hexdigest()
                        new_user.email = email
                        new_user.sex = sex
                        new_user.save()
                        message="注册成功"
                        return redirect('/login/',locals())
                else:
                    message='验证码输入错误'
                    return render(request, 'login/register.html', locals())

        else:
            return render(request, 'login/register.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())
#注销 清除sesion
def logout(requests):
    #清除session  若是没有登录就直接跳转到登录页面,若是登录了在跳转到登出则跳转至文章页面
    # if not requests.session.get('is_login', None):
    #     return redirect('/index/')
    requests.session.flush()
    res = models.Hot_search.objects.values("Hot_searchtitle", "Hot_searchtime").order_by("-Hot_searchtime")
    if res:
        key_words = res[0]['Hot_searchtitle']
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
                                            # "topn_search": new_topn_search,
                                            })


#用户资料修改
def change(requests):
    if requests.is_ajax():
        user_id = requests.session.get('user_id')
        username=requests.POST['name']
        email=requests.POST['email']
        des = requests.POST['desc']
        job=requests.POST['job']
        user=models.User.objects.filter(username=username)
        if user:
            message="用户名重复"
            return JsonResponse({"message":message})
        else:
            get_email=models.User.objects.filter(email=email)
            if get_email:
                message="邮箱重复"
                return JsonResponse({"message":message})
            else:
                message="ok"
                models.User.objects.filter(id=user_id).update(username=username,email=email,description=des,job=job)
                requests.session['user_name'] = username
                requests.session['email'] = email
                requests.session['des'] = des
                return JsonResponse({"message":message})

#检查前端传过来的密码是否正确
def check_pwd(requests):
    if requests.is_ajax():
        data=requests.POST['pwd'] #获取前端传过来的密码
        user_id = requests.session.get('user_id')
        pwd=hashlib.sha1(data.encode('utf-8')).hexdigest()#对密码进行加密
        #查询当前用户的密码
        database_pwd=models.User.objects.get(id=user_id).password
        if str(pwd)==str(database_pwd):
            return JsonResponse({"message": "ok"})
        else:
            return JsonResponse({"message": "密码错误"})

#用户密码修改
def change_password(requests):
        if requests.is_ajax():
            user_id = requests.session.get('user_id')
            data=requests.POST['newPw']
            pwd = hashlib.sha1(data.encode('utf-8')).hexdigest()
            res=models.User.objects.filter(id=user_id).update(password=pwd)
            if res == 1:
                return JsonResponse({"status":'0'})
            else:
                return JsonResponse({"status": '1'})

#用户头像更改
def  upload(requests):
    if requests.method=="POST":
        username=requests.session.get('user_name')
        avatar = requests.FILES.get('avator')
        with open("media/"+avatar.name, 'wb') as f:
            for line in avatar:
                f.write(line)
        head_imgpath="media/%s"%(avatar)
        models.User.objects.filter(username=username).update(headimg=head_imgpath)
    return render(requests,"Personal/personData.html",{"head_imgpath":"../"+head_imgpath})



#个人资料
def personData(requests):
    if requests.session.get('is_login', None):
        id = requests.session.get('user_id')
        collect_count=models.Collect.objects.filter(user_id=id).count()
        Search_count = models.Search.objects.filter(user_id=id).count()
        head_imgpath=models.User.objects.filter(id=id).values("headimg")[0]['headimg']
        if head_imgpath:
            return render(requests, "Personal/personData.html", {"head_imgpath": "../" + head_imgpath,
                                                                 "collect_count": collect_count,
                                                                 "Search_count": Search_count
                                                                 })
        else:
            head_imgpath = 'https://uploadfile.huiyi8.com/up/51/3d/68/513d68ffef5924fc8e4309f4681be484.jpg'
            return render(requests, "Personal/personData.html", {"head_imgpath": head_imgpath,
                                                                 "collect_count": collect_count,
                                                                 "Search_count": Search_count
                                                                 })

    else:
        return redirect("/login/")

def collection(requests):
    id = requests.session.get('user_id')
    head_imgpath = models.User.objects.filter(id=id).values("headimg")[0]['headimg']
    if head_imgpath:
        return render(requests, "Personal/collection.html", {"head_imgpath": "../" + head_imgpath})
    else:
        head_imgpath='https://uploadfile.huiyi8.com/up/51/3d/68/513d68ffef5924fc8e4309f4681be484.jpg'
        return render(requests, "Personal/collection.html", {"head_imgpath": head_imgpath})


def searchHistory(requests):
    id = requests.session.get('user_id')
    head_imgpath = models.User.objects.filter(id=id).values("headimg")[0]['headimg']
    if head_imgpath:
        return render(requests, "Personal/searchHistory.html", {"head_imgpath": "../" + head_imgpath})
    else:
        head_imgpath = 'https://uploadfile.huiyi8.com/up/51/3d/68/513d68ffef5924fc8e4309f4681be484.jpg'
        return render(requests, "Personal/searchHistory.html", {"head_imgpath": head_imgpath})

def dataAnalysis(requests):
    id = requests.session.get('user_id')

    search_title=models.Search.objects.filter(user_id=id).values("searchtitle")
    hot_search=models.Hot_search.objects.all().values("Hot_searchtitle")

    #将关键词提取并放入对应的list
    mysearch = []
    hotsearch=[]
    for x in  search_title:
        seg_list = jieba.analyse.extract_tags(x['searchtitle'], topK=20)
        if len(seg_list) >=1:
            for x in seg_list:
                mysearch.append(x.lower())
    for x in hot_search:
        hot_list=jieba.analyse.extract_tags(x["Hot_searchtitle"],topK=20)
        if len(hot_list)>=1:
            for hot  in hot_list:
                hotsearch.append(hot.lower())
    my_search=Counter(mysearch)
    hot_search=Counter(hotsearch)

    #将统计的关键词及数量分别写入
    mysearch_cate = []
    mysearch_num = []
    hotsearch_cate = []
    hotsearch_num = []

    for x  in my_search.most_common(10):
         mysearch_cate.append(x[0].lower())
         mysearch_num.append(x[1])
    for x  in hot_search.most_common(10):

        hotsearch_cate.append(x[0].lower())
        hotsearch_num.append(x[1])
    mysearch= my_search.most_common(1)[0][0]
    hot_reaearch=hot_search.most_common(1)[0][0]
    head_imgpath = models.User.objects.filter(id=id).values("headimg")[0]['headimg']
    if head_imgpath:
        return render(requests, "Personal/dataAnalysis.html",
                      {"head_imgpath": "../" + head_imgpath, "mysearch_cate": mysearch_cate,
                       "mysearch_num": mysearch_num,
                       "hotsearch_cate": hotsearch_cate,
                       "hotsearch_num": hotsearch_num,
                       "mysearch": mysearch,
                       "hot_reaearch": hot_reaearch
                       })
    else:
        #设置默认头像
        head_imgpath = 'https://uploadfile.huiyi8.com/up/51/3d/68/513d68ffef5924fc8e4309f4681be484.jpg'
        return render(requests, "Personal/dataAnalysis.html",
                      {"head_imgpath": head_imgpath, "mysearch_cate": mysearch_cate,
                       "mysearch_num": mysearch_num,
                       "hotsearch_cate": hotsearch_cate,
                       "hotsearch_num": hotsearch_num,
                       "mysearch": mysearch,
                       "hot_reaearch": hot_reaearch
                       })


def collection_article(requests):
    if requests.session.get('is_login', None):
        if requests.is_ajax():
            id = requests.session.get('user_id')
            collect_url=requests.POST['url']
            collect_title=requests.POST['title']
            #去标签
            dr = re.compile(r'<[^>]+>', re.S)
            collecttitle = dr.sub('', collect_title)
            print(collecttitle)
            #判断收藏的是否存在于数据库
            exist=models.Collect.objects.filter(user_id=id).values("collecturl")
            if exist:
                if exist[0]['collecturl']==collect_url:
                    return JsonResponse({"status":"1"})
            else:
                res=models.Collect.objects.create(user_id=id,collecturl=collect_url,collecttitle=collecttitle)
                if res:
                        return JsonResponse({"status":'0'})
                else:
                        return JsonResponse({"status":"1"})
    else:
        return JsonResponse({"status": '2'})

