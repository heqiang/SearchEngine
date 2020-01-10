from django.conf.urls import url
from user import views
from BS_Search import settings


urlpatterns=[
    url(r'^login/$',views.login,name="login"),
    url(r'logout/',views.logout,name="logout"),
    url(r'register/',views.register,name="register"),
    url(r'^personDate/$',views.personData,name='personData'),#个人信息路由
    url(r'^collection/$',views.collection,name='collection') ,#个人收藏路由
    url(r'^collection_article/$',views.collection_article,name='collection_article') ,#文章收藏
    url(r'^searchHistory/$',views.searchHistory,name='searchHistory') ,#浏览历史路由
    url(r'^dataAnalysis/$',views.dataAnalysis,name='dataAnalysis') ,#数据分析路由
    url(r'^change/$',views.change,name='change'),#个人基础信息更改
    url(r'^check_pwd/$',views.check_pwd,name='check_pwd'),#密码检查
    url(r'^change_password/$',views.change_password,name='change_password'),#密码修改
    url(r'^upload/$',views.upload,name='upload'),#头像上传
    url(r'^check_code/$', views.check_code, name="check_code"),
]
