# kingadmin/app_setup.py

from django import conf

def kingadmin_auto_discover():
    for app_name in conf.settings.INSTALLED_APPS:
        try:
            #去每个app下面执行kingadmin.py文件
            mod = __import__('%s.kingadmin'%app_name)
            #打印每个app已注册的model名字
            # print(mod.kingadmin)
        except ImportError:
            pass