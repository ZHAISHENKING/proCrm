# crm/kingadmin.py

from kingadmin.sites import site
from crm import models
from kingadmin.admin_base import BaseKingAdmin

# print('crm kingadmin....')

#注册model
class CustomerAdmin(BaseKingAdmin):
    list_display = ['id','name','source','contact_type','contact','consultant','consult_content','status','date']
    list_filter = ['source','consultant','status','date']
    search_fields = ['contact','consultant__name']
    readonly_fields = ['contact', 'status']
    filter_horizontal = ['consult_courses']
    # 批量操作
    actions = ['change_status', ]

    def change_status(self, request, querysets):  # querysets是你选中的所有对象
        querysets.update(status=0)

class StudentAdmin(BaseKingAdmin):
    filter_horizontal = ['class_grades']



site.register(models.CustomerInfo,CustomerAdmin)
site.register(models.Role)
site.register(models.Menus)
site.register(models.UserProfile)
site.register(models.Course)
site.register(models.ClassList)
site.register(models.StudyRecord)
site.register(models.CourseRecord)
site.register(models.Student,StudentAdmin)
