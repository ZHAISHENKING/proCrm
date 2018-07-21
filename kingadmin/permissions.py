# kingadmin/permissions.py

# from django.core.urlresolvers import resolve
from django.urls import resolve
from django.shortcuts import render,redirect,HttpResponse
from kingadmin.permission_list import perm_dic
from django.conf import settings


def perm_check(*args,**kwargs):
    #1.获取当前请求的url
    #2.把url解析成url_name（通过resolve）
    #3.判断用户是否已登录（user.is_authenticated()）
    #3.拿url_name到permission_dict去匹配，匹配时要包括请求方法和参数
    #4.拿匹配到可权限key，调用user.has_perm(key)
    match_results = [None,]
    request = args[0]
    resolve_url_obj = resolve(request.path)
    #通过resolve解析出当前访问的url_name
    current_url_name = resolve_url_obj.url_name
    print('---perm:',request.user,request.user.is_authenticated(),current_url_name)
    #match_flag = False
    match_key = None
    #判断用户是否登录
    if request.user.is_authenticated() is False:
         return redirect(settings.LOGIN_URL)

    for permission_key,permission_val in  perm_dic.items():
        #key和value（值有四个参数）: 比如 'crm_table_index': ['table_index', 'GET', [], {}, ]
        per_url_name = permission_val[0]
        per_method  = permission_val[1]
        perm_args = permission_val[2]
        perm_kwargs = permission_val[3]

        #如果当前访问的url_name匹配上了权限里面定义的url_name
        if per_url_name == current_url_name:
            #url_name匹配上，接着匹配方法（post,get....）
            if per_method == request.method:
                # if not  perm_args: #if no args defined in perm dic, then set this request to passed perm

                #逐个匹配参数，看每个参数是否都能对应的上。
                args_matched = False      #for args only
                for item in perm_args:
                    #通过反射获取到request.xxx函数   这里request_methon_func = request.GET/request.POST
                    request_method_func = getattr(request,per_method)

                    if request_method_func.get(item,None):   # request字典中有此参数
                        args_matched = True
                    else:
                        print("arg not match......")
                        args_matched = False
                        break          # 有一个参数不能匹配成功，则判定为假，退出该循环。因为可能有很多参数，必须所有参数都一样才匹配成功
                else:         # perm_dic里面的参数可能定义的就是空的，就走这里
                    args_matched = True

                #匹配有特定值的参数
                kwargs_matched = False
                for k,v in perm_kwargs.items():
                    request_method_func = getattr(request, per_method)
                    arg_val = request_method_func.get(k, None)  # request字典中有此参数
                    print("perm kwargs check:",arg_val,type(arg_val),v,type(v))
                    if arg_val == str(v): #匹配上了特定的参数 及对应的 参数值， 比如，需要request 对象里必须有一个叫 user_id=3的参数
                        kwargs_matched = True
                    else:
                        kwargs_matched = False
                        break # 有一个参数不能匹配成功，则判定为假，退出该循环。

                else:
                    kwargs_matched = True


                match_results = [args_matched,kwargs_matched]
                print("--->match_results ", match_results)
                #列表里面的元素都为真
                if all(match_results): #都匹配上了
                    match_key = permission_key
                    break

    if all(match_results):
        #主要是获取到app_name
        app_name, per_name = match_key.split('_')
        print("--->matched ",match_results,match_key)
        # print(app_name, *per_name)
        #per_obj = 例如：crm.crm_obj_list
        perm_obj = '%s.%s' % (app_name,match_key)
        print("perm str:",perm_obj)
        if request.user.has_perm(perm_obj):
            print('当前用户有此权限')
            return True
        else:
            print('当前用户没有该权限')
            return True

    else:
        print("未匹配到权限项，当前用户无权限")


def check_permission(func):
    def inner(*args,**kwargs):
        if not perm_check(*args,**kwargs):
            request = args[0]
            return render(request,'kingadmin/page_403.html')
        return func(*args,**kwargs)
    return  inner