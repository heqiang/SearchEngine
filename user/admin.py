from django.contrib import admin

# Register your models here.
from user.models import User,Collect,Hot_search,Search

class  MyAdminSite(admin.AdminSite):
        site_header = "ItSearch"
        site_title = 'ItSearch'


@admin.register(User)
class  UserAdmin(admin.ModelAdmin):
    list_display = ('username','sex','email','createtime')
    search_fields = ('username',)
@admin.register(Collect)
class  Collect(admin.ModelAdmin):
    list_display = ('id','get_userName','collecttitle','collecturl','collecttime')
    list_per_page = 20
    ordering = ('-collecttime',)
    search_fields = ('user__username','collecttitle',)
    def  get_userName(self,obj):
        return obj.user.username
    get_userName.short_description = '用户'

@admin.register(Search)
class  Search(admin.ModelAdmin):
    list_display = ('id','get_userName','searchtitle','searchurl','searchtime')
    list_per_page = 20
    ordering = ('id','-searchtime',)
    search_fields = ('user__username','searchtitle',)
    def get_userName(self, obj):
        return obj.user.username
    get_userName.short_description = '用户'
@admin.register(Hot_search)
class  hot_Search(admin.ModelAdmin):
    list_display = ('id','Hot_searchtitle','Hot_searchurl','Hot_searchtime')
    list_per_page = 20
    ordering = ('-Hot_searchtime',)



