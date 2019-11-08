from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^$', views.IndexView),
    url(r'^index',views.IndexView),
    url(r'^suggest/$',views.SearchSuggest,name="suggest"),
    url(r'^search/$', views.SearchView, name="search"),
    url(r'^result/$',views.Result,name="result"),
    url(r'^Search_history/$',views.Search_history,name="Search_history"),#搜索历史
    url(r'^delete_search/$',views.delete_search,name='delete_search'),#删除搜索
    url(r'^collect_history/$',views.collect_history,name="collect_history"),#搜索历史
    url(r'^delete_collect/$',views.delete_collect,name='delete_collect'),#删除收藏

]