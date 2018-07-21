# kingadmin/urls.py

from django.conf.urls import url

from kingadmin import views

urlpatterns = [
    url(r'^$', views.app_index,name='app_index'),
    url(r'^login/', views.acc_login,name='login'),
    url(r'^logout/', views.acc_logout,name='logout'),
    #获取column列表
    url(r'^(\w+)/(\w+)/$', views.table_obj_list,name='table_obj_list'),
    #修改
    url(r'^(\w+)/(\w+)/(\d+)/change/$', views.table_obj_change,name='table_obj_change'),
    #增加
    url(r'^(\w+)/(\w+)/add/$', views.table_obj_add,name='table_obj_add'),
    #删除
    url(r'^(\w+)/(\w+)/(\d+)/delete/$', views.table_obj_delete,name='obj_delete'),
]
