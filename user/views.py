from django.shortcuts import render
from django.shortcuts import  redirect
from user import  models
from user import forms
import hashlib
from django.http import JsonResponse

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

#文章浏览  需要登录获取当前作者的id 需要传递url，title
def Search_article(requests):
    searchtitle=requests.GET('title',"")
    searchurl=requests.GET('url',"")
    user_id=requests.session.get('user_id')
    models.Search.objects.create(searchtitle=searchtitle,searchurl=searchurl,user_id=user_id)

#文章收藏 #需要登录获取当前作者的id  需要传递url，title
def Collect_article(requests):
    collecttitle = requests.GET('title', "")
    collecturl = requests.GET('url', "")
    user_id = requests.session.get('user_id')
    models.Collect.objects.create(collecttitle=collecttitle,collecturl=collecturl,user_id=user_id)
#查看个人中心的收藏记录  user_id

#返回的页面需要修改
def personal_collect(requests):
    user_id = requests.session.get('user_id')
    all_collect=models.Collect.objects.filter(user_id=user_id)
    return  render(requests,"personal.html",{"all_collect":all_collect})
# 查看个人中心的浏览记录  user_id
def personal_search(requests):
    user_id = requests.session.get('user_id')
    all_search = models.Search.objects.filter(user_id=user_id)
    return render(requests, "personal.html", {"all_collect": all_search})

def personal_pwd(requests):
    user_id = requests.session.get('user_id')
    pwd=requests.GET('pwd')
    models.User.objects.filter(user_id=user_id).update(password=pwd)
    return  render(requests,"personal.html",{"res":"修改成功"})



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
    return render(requests,"Personal/dataAnalysis.html",{"head_imgpath":"../"+head_imgpath})


