from django.conf.urls import url
from user import views

urlpatterns=[

    url(r'^login/$',views.login,name="login"),
    url(r'logout/',views.logout,name="logout"),
    url(r'register/',views.register,name="register"),
    url(r'^Search_article/$',views.Search_article,name='Search_article'),#文航浏览
    url(r'^Collect_article/$',views.Collect_article,name='Collect_article'),#文章收藏
    url(r'^personal_collect/$',views.personal_collect,name='personal_collect'),#个人中心收藏内容查看
    url(r'^personal_search/$',views.personal_search,name='personal_search'),#个人中心搜索历史记录查看
    url(r'^personal/$',views.personal,name='personal'),#个人基础信息修改
    url(r'^personal_pwd/$',views.personal_pwd,name='personal_pwd')
]