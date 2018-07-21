# crm/form.py

from django.forms import ModelForm
from crm import models
from django import forms

class CustomerForm(ModelForm):
    class Meta:
        model = models.CustomerInfo
        fields = "__all__"
        #不显示的字段
        exclude = ['consult_content','status','consult_courses']
        #只读的字段
        readonly_fields = ['contact_type','contact','consultant','referral_from','source']

    #django是通过“__new__”方法，找到ModelForm里面的每个字段的，然后循环出每个字段添加自定义样式
    def __new__(cls, *args, **kwargs):
        #cls.base_fields是一个元祖，里面是 所有的  【(字段名，字段的对象),(),()】
        for field_name in cls.base_fields:
            field_obj = cls.base_fields[field_name]
            #添加属性
            field_obj.widget.attrs.update({'class':'form-control'})

            if field_name in cls.Meta.readonly_fields:
                field_obj.widget.attrs.update({'disabled':'true'})
        return ModelForm.__new__(cls)

    #只读字段不让用户通过浏览器改html代码的方式改
    def clean(self):
        # 表单级别的错误
        if self.errors:
            raise forms.ValidationError(("Please fix errors before re-submit."))
        # means this is a change form ,should check the readonly fields
        if self.instance.id is not None:
            #取出只读字段，是一个字符串形式
            for field in self.Meta.readonly_fields:
                #通过反射取出字段的值（数据库里的数据）
                old_field_val = getattr(self.instance, field)
                #提交过来的数据
                form_val = self.cleaned_data.get(field)
                #如果两个数据不匹配
                if old_field_val != form_val:
                    #就提示只读字段不能修改
                    #add_error是字段级别的错误
                    self.add_error(field, "Readonly Field: field should be '{value}' ,not '{new_value}' ". \
                                   format(**{'value': old_field_val, 'new_value': form_val}))


class EnrollmentForm(ModelForm):
    '''审核页面'''
    class Meta:
        model = models.StudentEnrollment
        fields = "__all__"
        exclude = ['consultant_approved_date']
        readonly_fields = ['contract_agreed',]

    #django是通过“__new__”方法，找到ModelForm里面的每个字段的，然后循环出每个字段添加自定义样式
    def __new__(cls, *args, **kwargs):
        #cls.base_fields是一个元祖，里面是 所有的  【(字段名，字段的对象),(),()】
        for field_name in cls.base_fields:
            field_obj = cls.base_fields[field_name]
            #添加属性
            field_obj.widget.attrs.update({'class':'form-control'})

            if field_name in cls.Meta.readonly_fields:
                field_obj.widget.attrs.update({'disabled':'true'})
        return ModelForm.__new__(cls)

    #只读字段不让用户通过浏览器改html代码的方式改
    def clean(self):
        # 表单级别的错误
        if self.errors:
            raise forms.ValidationError(("Please fix errors before re-submit."))
        # means this is a change form ,should check the readonly fields
        if self.instance.id is not None:
            #取出只读字段，是一个字符串形式
            for field in self.Meta.readonly_fields:
                #通过反射取出字段的值（数据库里的数据）
                old_field_val = getattr(self.instance, field)
                #提交过来的数据
                form_val = self.cleaned_data.get(field)
                #如果两个数据不匹配
                if old_field_val != form_val:
                    #就提示只读字段不能修改
                    #add_error是字段级别的错误
                    self.add_error(field, "Readonly Field: field should be '{value}' ,not '{new_value}' ". \
                                   format(**{'value': old_field_val, 'new_value': form_val}))

