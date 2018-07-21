# student/kingadmin.py

from student import models
from kingadmin.sites import site

# print('student kingadmin.....')

#注册model
class TestAdmin(object):
    list_display = ['name']

site.register(models.Test,TestAdmin)