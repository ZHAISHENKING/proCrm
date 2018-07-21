# crm/views.py

import os,json
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.decorators import login_required
from crm import models
from crm import form
from django.views.decorators.csrf import csrf_exempt
from django import conf
from django.utils.timezone import datetime
from django.db.utils import IntegrityError


# @login_required
def dashboard(request):

    return render(request,'crm/dashboard.html')

@login_required
def stu_enrollment(request):
    '''学员报名'''
    customers = models.CustomerInfo.objects.all()
    class_lists = models.ClassList.objects.all()

    if request.method == 'POST':
        #获取提交的客户id和班级id，然后生成报名链接
        customer_id = request.POST.get('customer_id')
        class_grade_id = request.POST.get('class_grade_id')
        try:
            enrollment_obj = models.StudentEnrollment.objects.create(
                customer_id = customer_id,
                class_grade_id = class_grade_id,
                consultant_id = request.user.userprofile.id
            )
        #已经生成过报名链接，就进入审核页面
        except IntegrityError as e:
            enrollment_obj = models.StudentEnrollment.objects.get(customer_id = customer_id,class_grade_id = class_grade_id)
            if enrollment_obj.contract_agreed:
                return redirect("/crm/stu_enrollment/%s/contract_audit/"% enrollment_obj.id)

        #生成链接返回到前端
        enrollment_link = "http://localhost:8000/crm/enrollment/%s"% enrollment_obj.id

    return render(request,'crm/stu_enrollment.html',locals())

@csrf_exempt
def enrollment_fileupload(request,enrollment_id):
    '''学员报名文件上传'''
    enrollment_upload_dir = os.path.join(conf.settings.CRM_FILE_UOLOAD_DIR,enrollment_id)
    #第一次上传图片就创建目录，学员上传第二章图片的时候，会判断目录是否已经存在
    #因为如果目录存在还mkdir就会报错，所以这里要做判断
    if not os.path.isdir(enrollment_upload_dir):
        os.mkdir(enrollment_upload_dir)
    #获取上传文件的对象
    file_obj = request.FILES.get('file')
    #最多只允许上传3个文件
    if len(os.listdir(enrollment_upload_dir)) <= 3:
        #把图片名字拼接起来（file.name：上传的文件名字）
        with open(os.path.join(enrollment_upload_dir,file_obj.name),'wb') as f:
            for chunks in file_obj.chunks():
                f.write(chunks)
    else:
        return HttpResponse(json.dumps({'status':False,'err_msg':'最多只能上传三个文件'}))

    return HttpResponse(json.dumps({'status':True,}),)



def enrollment(request,enrollment_id):
    '''学员在线报名表地址'''

    enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_id)
    if enrollment_obj.contract_agreed:
        return HttpResponse("报名合同已提交，正在审核中，请耐心等待！")

    if request.method == 'POST':
        customer_form = form.CustomerForm(instance=enrollment_obj.customer,data=request.POST)
        if customer_form.is_valid():
            customer_form.save()
            #提交报名信息后，把合同状态给为True
            enrollment_obj.contract_agreed = True
            #提交的时间,from django.utils.timezone import datetime
            enrollment_obj.contract_signed_date = datetime.now()
            enrollment_obj.save()
            return HttpResponse("你已成功提交报名信息，请等待审核，欢迎加入仙剑奇侠传")
    else:
        customer_form = form.CustomerForm(instance=enrollment_obj.customer)

    # 列出学员已上传的文件
    upload_files = []
    enrollment_upload_dir = os.path.join(conf.settings.CRM_FILE_UOLOAD_DIR, enrollment_id)
    if os.path.isdir(enrollment_upload_dir):
        upload_files = os.listdir(enrollment_upload_dir)

    return render(request,'crm/enrollment.html',locals())

@login_required
def contract_audit(request,enrollment_id):
    '''合同审核'''

    enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_id)
    if request.method == 'POST':
        enrollment_form = form.EnrollmentForm(instance=enrollment_obj,data=request.POST)
        if enrollment_form.is_valid():
            enrollment_form.save()
            stu_obj = models.Student.objects.get_or_create(customer=enrollment_obj.customer)[0]
            #m2m, 添加班级
            stu_obj.class_grades.add(enrollment_obj.class_grade_id)
            stu_obj.save()
            #改变报名
            enrollment_obj.customer.status = 1
            enrollment_obj.save()
            return redirect("/kingadmin/crm/customerinfo/%s/change"%enrollment_obj.customer.id)
    else:
        #拿到客户信息的表单
        customer_form = form.CustomerForm(instance=enrollment_obj.customer)
        enrollment_form = form.EnrollmentForm(instance=enrollment_obj)
    return render(request,'crm/contract_audit.html',locals())





