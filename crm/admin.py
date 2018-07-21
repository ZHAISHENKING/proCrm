# crm/admin.py

from django.contrib import admin
from crm import models

from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from crm.models import UserProfile


class CustomerAdmin(admin.ModelAdmin):
    #显示
    list_display = ['name','source','contact_type','contact','consultant','consult_content','status','date']
    #过滤
    list_filter = ['source','consultant','status','date']
    #搜索，consultant是外键，必须加“__字段名”
    search_fields = ['contact','consultant__name']
    #只读字段,不能修改
    # readonly_fields = ['contact','status']
    filter_horizontal = ['consult_courses']
    #每页显示多少条数据
    list_per_page = 8
    #批量操作
    actions = ['change_status',]
    def change_status(self,request,querysets):   #querysets是你选中的所有对象
        querysets.update(status=2)

class CourseRecordAdmin(admin.ModelAdmin):
    list_display = ['class_grade','day_num','has_homework']


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = UserProfile
        fields = ('email', 'name')

    #进行验证
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        #继承基类的save()
        user = super(UserCreationForm, self).save(commit=False)
        #把明文密码改成密文
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    #把密码改成哈希的了
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = UserProfile
        fields = ('email', 'password', 'name', 'is_active', 'is_superuser')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserProfileAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name','is_superuser')
    list_filter = ('is_superuser',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active','is_superuser','is_staff','role','user_permissions','groups')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2',)}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('role','user_permissions','groups')

# Now register the new UserProfileAdmin...
admin.site.register(UserProfile, UserProfileAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
# admin.site.unregister(Group)






admin.site.register(models.Role)
admin.site.register(models.CustomerInfo,CustomerAdmin)
admin.site.register(models.Student)
admin.site.register(models.CustomerFollowUp)
admin.site.register(models.Course)
admin.site.register(models.ClassList)
admin.site.register(models.CourseRecord,CourseRecordAdmin)
admin.site.register(models.StudyRecord)
admin.site.register(models.Branch)
admin.site.register(models.Menus)
# admin.site.register(models.UserProfile)
admin.site.register(models.ContractTemplate)
admin.site.register(models.StudentEnrollment)
admin.site.register(models.PaymentRecord)


