from django.shortcuts import render
from django.shortcuts import  redirect
from user import  models
from user import forms
import hashlib
from django.http import JsonResponse
import jieba.analyse
from collections import Counter
import re
#登录逻辑
def login(requests):
    if requests.session.get('is_login', None):  # 不允许重复登录
        username = requests.session.get('user_name')
        user_id = requests.session.get('user')
        return redirect('/result/')
    if requests.method=="POST":
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
                requests.session['des']=user.description
                return  redirect('/index/')
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
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')
            sex = register_form.cleaned_data.get('sex')
            job=register_form.cleaned_data.get('job')
            destription=register_form.cleaned_data.get("description")
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

                new_user = models.User()
                new_user.username = username
                new_user.password = hashlib.sha1(password1.encode('utf-8')).hexdigest()
                new_user.email = email
                new_user.sex = sex
                new_user.job=job
                new_user.description=destription
                new_user.save()
                message="注册成功"
                return redirect('/login/',locals())
        else:
            return render(request, 'login/register.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())
#注销 清楚sesion
def logout(requests):
    #清除session  若是没有登录就直接跳转到登录页面,若是登录了在跳转到登出则跳转至文章页面
    if not requests.session.get('is_login', None):
        return redirect('/index/')
    requests.session.flush()
    return redirect("/index/")

#用户资料修改
def change(requests):
    if requests.is_ajax():
        user_id = requests.session.get('user_id')
        username=requests.POST['name']
        email=requests.POST['email']
        des = requests.POST['desc']
        user=models.User.objects.filter(username=username)
        if user:
            message="User name is nor valid"
            return JsonResponse({"message":message})
        else:
            get_email=models.User.objects.filter(email=email)
            if get_email:
                message="email is nor valid"
                return JsonResponse({"message":message})
            else:
                message="ok"
                models.User.objects.filter(id=user_id).update(username=username,email=email,description=des)
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

#路由控制
def personData(requests):
    if requests.session.get('is_login', None):
        id = requests.session.get('user_id')
        head_imgpath=models.User.objects.filter(id=id).values("headimg")[0]['headimg']
        return render(requests,"Personal/personData.html",{"head_imgpath":"../"+head_imgpath})
    else:
        return redirect("/login/")

def collection(requests):

    id = requests.session.get('user_id')
    head_imgpath = models.User.objects.filter(id=id).values("headimg")[0]['headimg']
    return render(requests,"Personal/collection.html",{"head_imgpath":"../"+head_imgpath})
def searchHistory(requests):
    id = requests.session.get('user_id')
    head_imgpath = models.User.objects.filter(id=id).values("headimg")[0]['headimg']
    return render(requests,"Personal/searchHistory.html",{"head_imgpath":"../"+head_imgpath})
def dataAnalysis(requests):
    id = requests.session.get('user_id')
    head_imgpath = models.User.objects.filter(id=id).values("headimg")[0]['headimg']
    search_title=models.Search.objects.filter(user_id=id).values("searchtitle")
    hot_search=models.Hot_search.objects.all().values("Hot_searchtitle")
    mysearch = []
    hotsearch=[]
    mysearch_cate = []
    mysearch_num = []
    hotsearch_cate=[]
    hotsearch_num=[]
    for x in  search_title:
        seg_list = jieba.analyse.extract_tags(x['searchtitle'], topK=20)
        if len(seg_list) > 1:
            for x in seg_list:
                mysearch.append(x.lower())
    for x in hot_search:
        hot_list=jieba.analyse.extract_tags(x["Hot_searchtitle"],topK=20)
        if len(hot_list)>1:
            for hot  in hot_list:
                hotsearch.append(hot.lower())
    my_search=Counter(mysearch)
    hot_search=Counter(hotsearch)
    for x  in my_search.most_common(10):
         mysearch_cate.append(x[0].lower())
         mysearch_num.append(x[1])
    for x  in hot_search.most_common(10):
        hotsearch_cate.append(x[0].lower())
        hotsearch_num.append(x[1])

    return render(requests,"Personal/dataAnalysis.html",{"head_imgpath":"../"+head_imgpath,"mysearch_cate":mysearch_cate,
                                                         "mysearch_num":mysearch_num,
                                                         "hotsearch_cate":hotsearch_cate,
                                                         "hotsearch_num":hotsearch_num
                                                         })

def collection_article(requests):
    if requests.is_ajax():
        id = requests.session.get('user_id')
        collect_url=requests.POST['url']
        collect_title=requests.POST['title']
        #去标签
        dr = re.compile(r'<[^>]+>', re.S)
        collecttitle = dr.sub('', collect_title)
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

