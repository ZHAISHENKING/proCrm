# kingadmin/permission_hook.py

def view_my_own_customers(request):
    #当前登录的用户id 等于客户的顾问的id（销售创建客户的时候，顾问就是销售自己）
    #实现销售只能看自己的客户功能
    if str(request.user.id) == request.GET.get('consultant'):
        return True
    else:
        return False