# crm/model.py
__author__ = 'derek'

from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,PermissionsMixin
)


class Role(models.Model):
    '''角色表'''
    name = models.CharField(max_length=64,unique=True)
    # 一个角色可以访问多个菜单，一个菜单可以被多个角色访问
    menus = models.ManyToManyField('Menus',blank=True,verbose_name='动态菜单')

    def __str__(self):
        return self.name


class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )

    name = models.CharField(max_length=64)
    role = models.ManyToManyField('Role', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    #创建用户和超级用户，关联上面的
    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    #必须要有的字段
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True
    #
    # def has_module_perms(self, app_label):
    #     "Does the user have permissions to view the app `app_label`?"
    #     # Simplest possible answer: Yes, always
    #     return True

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    # @property
    # def is_staff(self):
    #     "Is the user a member of staff?"
    #     # Simplest possible answer: All admins are staff
    #     return self.is_admin

    class Meta:
        permissions = (
            ('crm_table_list','可以查看每张表里所有的数据'),
            ('crm_table_list_view','可以访问表里每条数据的修改页'),
            ('crm_table_list_change','可以对表里的每条数据进行修改'),
            ('crm_table_list_add_view','可以访问数据增加页'),
            ('crm_table_list_add','可以添加表数据'),
        )


#
# class UserProfile(models.Model):
#     '''用户信息表'''
#     #关联django自带的User，可以自己扩展字段
#     user = models.OneToOneField(User,on_delete=models.CASCADE)
#     name = models.CharField('姓名',max_length=64)
#     #一个用户可以有多个角色，一个角色可以对应多个用户
#     role = models.ManyToManyField(Role,blank=True,null=True)
#
#     def __str__(self):
#         return self.name


class CustomerInfo(models.Model):
    '''客户信息表'''
    name = models.CharField('姓名',max_length=64,default=None)
    contact_type_choices = ((0,'qq'),(1,'微信'),(2,'手机'))
    contact_type = models.SmallIntegerField(choices=contact_type_choices,default=0,verbose_name='联系类型')
    contact = models.CharField('联系方式',max_length=64,unique=True)
    source_choices = ((0,'qq群'),(1,'51CTO'),(2,'百度推广'),(3,'知乎'),(4,'转介绍'),(5,'其它'),)
    source = models.SmallIntegerField('客户来源',choices=source_choices)
    #关联自己，如果是转介绍（介绍人已经是学员，然后介绍别人过来学习），需要填写转介绍人的信息，不是转介绍，这里就可以为空
    referral_from = models.ForeignKey('self',blank=True,null=True,verbose_name='转介绍',on_delete=models.CASCADE)
    #可以咨询多个课程
    consult_courses = models.ManyToManyField('Course',verbose_name='咨询课程')
    consult_content = models.TextField(verbose_name='咨询内容',)
    status_choices = ((0,'未报名'),(1,'已报名'),(2,'已经退学'))
    status = models.SmallIntegerField('客户状态',choices=status_choices)
    consultant = models.ForeignKey('UserProfile',verbose_name='课程顾问',on_delete=models.CASCADE)

    id_num = models.CharField('身份证号',max_length=128,blank=True,null=True)
    emergency_contact = models.PositiveIntegerField('紧急联络人手机号',blank=True,null=True)
    sex_choices = ((0,'男'),(1,'女'))
    sex = models.PositiveSmallIntegerField(choices=sex_choices,verbose_name='性别',blank=True,null=True)

    date = models.DateField('创建的时间',auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '客户信息'
        verbose_name_plural = verbose_name


class Student(models.Model):
    '''学员表'''
    customer = models.OneToOneField('CustomerInfo',verbose_name='客户',on_delete=models.CASCADE)
    class_grades = models.ManyToManyField('ClassList',verbose_name='班级')

    def __str__(self):
        return "%s"%self.customer


class CustomerFollowUp(models.Model):
    '''客户跟踪记录表'''
    customer = models.ForeignKey('CustomerInfo',on_delete=models.CASCADE)
    content = models.TextField('跟踪内容',)
    user = models.ForeignKey('UserProfile',verbose_name='跟进人',on_delete=models.CASCADE)
    status_choices = ((0,'近期无报名计划'),(1,'一个月内报名'),(2,'半个月报名'),(3,'已报名'),)
    status = models.SmallIntegerField('客户状态',choices=status_choices)
    date = models.DateField('创建的时间', auto_now_add=True)


class Course(models.Model):
    '''课程表'''
    name = models.CharField('课程名称',max_length=64,unique=True)
    #价格必须为整数
    price = models.PositiveSmallIntegerField('价格',)
    period = models.PositiveSmallIntegerField('课程周期（月）',default=5)
    outline = models.TextField('大纲',)

    def __str__(self):
        return self.name


class ClassList(models.Model):
    '''班级列表'''
    branch = models.ForeignKey('Branch',verbose_name='校区',on_delete=models.CASCADE)
    #一个班级只能有一个课程，一个课程可以有多个班级
    course = models.ForeignKey('Course',verbose_name='课程',on_delete=models.CASCADE)
    class_type_choices = ((0,'脱产'),(1,'周末'),(2,'网络班'))
    class_type = models.SmallIntegerField('班级类型',choices=class_type_choices,default=0)
    semester = models.SmallIntegerField('学期',)
    teachers = models.ManyToManyField('UserProfile',verbose_name='讲师')
    start_date = models.DateField('开班日期',)
    #毕业日期因为不固定，所以可以为空
    graduate_date = models.DateField('毕业日期',blank=True,null=True)
    contract_template = models.ForeignKey('ContractTemplate',blank=True,null=True,on_delete=models.CASCADE)

    def __str__(self):
        #班级名是课程名+第几期拼接起来的
        return "%s(%s)期"%(self.course.name,self.semester)

    class Meta:
        #联合唯一，班级不能重复
        unique_together = ('branch','class_type','course','semester')


class CourseRecord(models.Model):
    '''上课记录'''
    class_grade = models.ForeignKey('ClassList',verbose_name='上课班级',on_delete=models.CASCADE)
    day_num = models.PositiveSmallIntegerField('课程节次',)
    teacher = models.ForeignKey('UserProfile',verbose_name='讲师',on_delete=models.CASCADE)
    title = models.CharField('本节主题',max_length=64)
    content = models.TextField('本节内容',)
    has_homework = models.BooleanField('本节有作业',default=True)
    homework = models.TextField('作业需求',blank=True,null=True)
    date = models.DateField('创建的时间', auto_now_add=True)

    def __str__(self):
        #上课班级+课程节次
        return "%s第(%s)节"%(self.class_grade,self.day_num)

    class Meta:
        unique_together = ('class_grade','day_num')


class StudyRecord(models.Model):
    '''学习记录表'''
    #一节课对应多个学生
    course_record = models.ForeignKey('CourseRecord',verbose_name='课程',on_delete=models.CASCADE)
    #一个学生有多个上课记录
    student = models.ForeignKey('Student',verbose_name='学生',on_delete=models.CASCADE)
    score_choices = ((100,'A+'),
                     (90,'A'),
                     (85,'B+'),
                     (80,'B'),
                     (75,'B-'),
                     (70,'C+'),
                     (60,'C'),
                     (40,'C-'),
                     (-50,'D'),
                     (0,'N/A'),         #not avaliable
                     (-100,'COPY'),     #抄作业
                     )
    score = models.SmallIntegerField('得分',choices=score_choices,default= 0)
    show_choices = ((0,'缺勤'),
                    (1,'已签到'),
                    (2,'迟到'),
                    (3,'早退'),
                    )
    show_status = models.SmallIntegerField('出勤',choices=show_choices,default=1)
    note = models.TextField('成绩备注',blank=True,null=True)
    date = models.DateField('创建的时间', auto_now_add=True)

    def __str__(self):
        return "%s %s %s"%(self.course_record,self.student,self.score)


class Branch(models.Model):
    '''校区分支'''
    name = models.CharField('校区名',max_length=64,unique=True)
    addr = models.CharField('地址',max_length=128,blank=True,null=True)

    def __str__(self):
        return self.name


class Menus(models.Model):
    '''动态菜单'''
    name = models.CharField(max_length=64)
    #绝对url和动态url
    url_type_choices = ((0,'absolute'),(1,'dynamic'))
    url_type = models.SmallIntegerField(choices=url_type_choices,default=0)
    url_name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name','url_name')


class ContractTemplate(models.Model):
    '''存储合同模板'''
    name = models.CharField(max_length=64)
    content = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class StudentEnrollment(models.Model):
    """学员报名表"""
    customer = models.ForeignKey('CustomerInfo',on_delete=models.CASCADE)
    class_grade = models.ForeignKey('ClassList',on_delete=models.CASCADE)
    consultant = models.ForeignKey('UserProfile',on_delete=models.CASCADE)
    contract_agreed = models.BooleanField(default=False)
    contract_signed_date = models.DateTimeField(blank=True,null=True)
    contract_approved = models.BooleanField(default=False)
    consultant_approved_date = models.DateTimeField('合同审核时间',blank=True,null=True)

    class Meta:
        unique_together = ('customer','class_grade')

    def __str__(self):
        return '%s'% self.customer


class PaymentRecord(models.Model):
    '''存储学员缴费记录'''
    enrollment = models.ForeignKey('StudentEnrollment',on_delete=models.CASCADE)
    payment_type_choices = ((0,'报名费'),(1,'学费'),(2,'退费'))
    payment_type = models.SmallIntegerField(choices=payment_type_choices,default=0)
    amount = models.IntegerField('费用',default=500)
    consultant = models.ForeignKey('UserProfile',on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s' %self.enrollment


