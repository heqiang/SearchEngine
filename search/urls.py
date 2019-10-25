from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^$', views.IndexView),
    url(r'^index',views.IndexView),
    url(r'^suggest/$',views.SearchSuggest,name="suggest"),
    url(r'^search/$', views.SearchView, name="search"),
    # url(r'^collect_search',)

]