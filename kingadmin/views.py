# kingadmin/views.py

import json

from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.db.models import Q
from kingadmin import form_handle
from kingadmin import permissions


from kingadmin import app_setup
#程序已启动就自动执行
app_setup.kingadmin_auto_discover()

from kingadmin.sites import site
# print('site',site.enable_admins)

def app_index(request):

    return render(request,'kingadmin/app_index.html',{'site':site})

def get_filter_result(request,querysets):
    filter_conditions = {}
    #获取过滤的字段
    for key,val in request.GET.items():
        if key in ('page','_o','_q'):continue
        if val:
            filter_conditions[key] = val
    #返回过滤后的数据
    return querysets.filter(**filter_conditions),filter_conditions

def get_searched_result(request,querysets,admin_class):
    '''搜索'''

    search_key = request.GET.get('_q')
    if search_key:
        q = Q()
        q.connector = 'OR'

        for search_field in admin_class.search_fields:
            q.children.append(("%s__contains"%search_field,search_key))

        return querysets.filter(q)
    return querysets



def get_orderby_result(request,querysets,admin_class):
    '''排序'''

    current_ordered_column = {}
    #通过前端获取到要排序的字段的索引（是个字符串）
    orderby_index = request.GET.get('_o')
    if orderby_index:
        #通过索引找到要排序的字段,因为索引有可能是负数也有可能是负数，要用绝对值，否则负值的时候取到了其它字段了
        orderby_key = admin_class.list_display[abs(int(orderby_index))]
        #记录下当前是按什么排序字段的
        current_ordered_column[orderby_key] = orderby_index
        if orderby_index.startswith('-'):
            orderby_key = '-' + orderby_key

        return querysets.order_by(orderby_key),current_ordered_column
    else:
        return querysets,current_ordered_column

@permissions.check_permission
@login_required
def table_obj_list(request, app_name, model_name):
    '''取出指定model里的数据返回给前端'''
    #拿到admin_class后，通过它找到拿到model
    admin_class = site.enable_admins[app_name][model_name]
    #kingadmin actoin
    if request.method == "POST":
        #获取action
        selected_action = request.POST.get('action')
        #获取选中的id
        selected_ids = json.loads(request.POST.get('selected_ids'))
        #如果有action参数，代表这是一个正常的action执行动作,如果没有，代表可能是一个删除动作
        if not selected_action:
            #选中的数据(selected_ids)都删除
            if selected_ids:
                admin_class.model.objects.filter(id__in=selected_ids).delete()
        else:
            #获取所有选中id的对象
            selected_objs = admin_class.model.objects.filter(id__in=selected_ids)
            admin_action_func = getattr(admin_class,selected_action)
            #把数据返回到前端
            response = admin_action_func(request,selected_objs)
            if response:
                return response

    querysets = admin_class.model.objects.all().order_by('-id')
    #过滤
    querysets,filter_conditions = get_filter_result(request,querysets)
    admin_class.filter_conditions = filter_conditions
    #搜索
    querysets = get_searched_result(request, querysets, admin_class)
    #显示搜索的search_key
    admin_class.search_key = request.GET.get('_q','')

    #排序
    querysets,sorted_column = get_orderby_result(request,querysets,admin_class)

    #分页
    paginator = Paginator(querysets,admin_class.list_per_page)
    page = request.GET.get('page')
    try:
        querysets = paginator.page(page)
    except PageNotAnInteger:
        querysets = paginator.page(1)
    except EmptyPage:
        querysets = paginator.page(paginator.num_pages)

    return render(request, 'kingadmin/table_obj_list.html',locals())

@permissions.check_permission
@login_required
def table_obj_change(request,app_name,model_name,obj_id):
    '''kingadmin 数据修改页'''

    admin_class = site.enable_admins[app_name][model_name]
    model_form = form_handle.create_dynamic_model_form(admin_class)
    #让表单变成是修改的表单
    obj = admin_class.model.objects.get(id=obj_id)

    #修改
    if request.method == 'GET':
        form_obj = model_form(instance=obj)

    elif request.method == 'POST':
        form_obj = model_form(instance=obj,data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            #修改后跳转到的页面
            return redirect("/kingadmin/%s/%s/"%(app_name,model_name))

    return render(request,'kingadmin/table_obj_change.html',locals())

@permissions.check_permission
@login_required
def table_obj_add(request,app_name,model_name):
    '''kingadmin 数据添加'''

    admin_class = site.enable_admins[app_name][model_name]
    model_form = form_handle.create_dynamic_model_form(admin_class,form_add=True)

    if request.method == 'GET':
        form_obj = model_form()
    elif request.method == 'POST':
        form_obj = model_form(data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            #跳转到的页面
            return redirect("/kingadmin/%s/%s/"%(app_name,model_name))
    return render(request, 'kingadmin/table_obj_add.html', locals())

@permissions.check_permission
def table_obj_delete(request,app_name,model_name,obj_id):
    '''删除功能'''
    admin_class = site.enable_admins[app_name][model_name]
    obj = admin_class.model.objects.get(id=obj_id)
    if request.method == 'POST':
        obj.delete()
        return redirect("/kingadmin/%s/%s/" % (app_name, model_name))

    return render(request,'kingadmin/table_obj_delete.html',locals())



def acc_login(request):
    error_msg = ''
    if request.method == 'POST':
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        #user是一个对象
        #验证
        user = authenticate(username=username,password=password)
        if user:
            #登录（已生成session）
            login(request, user)
            #如果有next值就获取next值，没有就跳转到首页
            return redirect(request.GET.get('next','/kingadmin/'))
        else:
            error_msg = '用户名或密码错误！'

    return render(request,'kingadmin/login.html',{'error_msg':error_msg})


def acc_logout(request):
    logout(request)
    return redirect("/login/")

