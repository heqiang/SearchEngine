from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^$', views.indexArticle),
    url(r'^index',views.indexArticle),
    url(r'^suggest/$',views.suggest_article,name="suggest"),
    url(r'^search/$', views.Search_View, name="search"),

]