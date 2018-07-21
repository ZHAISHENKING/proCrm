# crm/urls.py

from django.conf.urls import url,include
from crm import views

urlpatterns = [
    url(r'^$', views.dashboard,name='sales_dashboard'),
    #学员报名
    # url(r'^stu_enrollment/$', views.stu_enrollment,name='stu_enrollment'),
    # #学员注册
    # url(r'^enrollment/(\d+)/$', views.enrollment,name='enrollment'),
    # #上传个人证件信息
    # url(r'^enrollment/(\d+)/fileupload/$', views.enrollment_fileupload,name='enrollment_fileupload'),
    # #合同审核
    # url(r'^stu_enrollment/(\d+)/contract_audit/$', views.contract_audit,name='contract_audit'),
]