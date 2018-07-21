# kingadmin/templatetags/kingadmin_tags.py
import datetime

from django.template import Library
from django.utils.safestring import mark_safe

register = Library()

@register.simple_tag
def build_filter_ele(filter_column,admin_class):
    '''过滤功能'''
    # filter_ele = "<select name='%s'>" % filter_column
    column_obj = admin_class.model._meta.get_field(filter_column)
    try:
        filter_ele = "<div class='col-md-2'>%s<select class='form-control' name='%s'>" % (filter_column,filter_column)
        for choice in column_obj.get_choices():
            #默认过滤的字段没有被选中
            selected = ''
            #当前字段被过滤了
            if filter_column in admin_class.filter_conditions:
                #如果当前值被选中
                if str(choice[0]) == admin_class.filter_conditions.get(filter_column):
                    selected = 'selected'

            option = "<option value='%s' %s>%s</option>" %(choice[0],selected,choice[1])
            filter_ele += option

    except AttributeError as e:
        filter_ele = "<div class='col-md-2'>%s<select class='form-control' name='%s__gte'>" % (filter_column,filter_column)
        #get_internal_type():获取字段属性
        #因为时间的过滤方式是固定的（今天，过去七天，一个月.....），而不是从后台获取的
        if column_obj.get_internal_type() in ('DateField','DateTimeField'):
            time_obj = datetime.datetime.now()
            time_list = [
                ['','--------'],
                [time_obj,'Today'],
                [time_obj - datetime.timedelta(7),'七天内'],
                [time_obj.replace(day=1),'本月'],
                [time_obj - datetime.timedelta(90),'三个月内'],
                [time_obj.replace(month=1,day=1),'YearToDay(YTD)'],     #本年
                ['','ALL'],
            ]

            for i in time_list:
                selected = ''
                #因为time_list有空值（''）和时间对象，需要做个判断
                #这里运用了三元运算，if not i[0]表示为空就执行它前面的'',如果不为空则执行后面的，改变时间格式
                time_to_str = '' if not i[0] else "%s-%s-%s"%(i[0].year,i[0].month,i[0].day)
                if "%s__gte"%filter_column in admin_class.filter_conditions:
                    if time_to_str == admin_class.filter_conditions.get("%s__gte"%filter_column):
                        selected = 'selected'
                option = "<option value='%s' %s>%s</option>" %(time_to_str,selected,i[1])

                filter_ele += option

    filter_ele += "</select></div>"

    return mark_safe(filter_ele)


@register.simple_tag
def build_table_row(obj,admin_class):
    '''生成一条记录的html element'''

    ele = ''
    if admin_class.list_display:
        #添加获取下标
        for index,column_name in enumerate(admin_class.list_display):
            #获取所有字段对象
            column_obj = admin_class.model._meta.get_field(column_name)
            #字段对象的choices方法，如果有choices，则get_xxx_display
            if column_obj.choices:
                column_data = getattr(obj,'get_%s_display'%column_name)()
            else:
                column_data = getattr(obj,column_name)
            td_ele = "<td>%s</td>" % column_data
            #如果列的下标为0，就添加一个a标签，点击跳到修改页面
            if index == 0:
                td_ele = "<td><a href='%s/change/'>%s</a></td>"%(obj.id,column_data)
            ele += td_ele
    else:
        td_ele = "<td><a href='%s/change/'>%s</a></td>"%(obj.id,obj)
        ele += td_ele
    return mark_safe(ele)

@register.simple_tag
def get_model_name(admin_class):
    '''获取表名'''
    return admin_class.model._meta.model_name.upper()

@register.simple_tag
def get_sorted_column(column,sorted_column,forloop):
    '''排序'''
    if column in sorted_column:    #如果这一列被排序了
        #要判断上一次排序是按什么顺序，本次取反
        last_sort_index = sorted_column[column]
        if last_sort_index.startswith('-'):
            #利用切片，去掉‘-’
            this_time_sort_index = last_sort_index.strip('-')
        else:
            #加上 '-'
            this_time_sort_index = '-%s'% last_sort_index
        return this_time_sort_index
    else:
        return forloop

@register.simple_tag
def render_filtered_args(admin_class,render_html=True):
    '''拼接过滤的字段'''
    if admin_class.filter_conditions:
        ele = ''
        for k,v in admin_class.filter_conditions.items():
            ele += '&%s=%s'%(k,v)
        if render_html:
            return mark_safe(ele)
        else:
            return ele
    else:
        return ''

@register.simple_tag
def render_sorted_arrow(column,sorted_column):
    '''排序的图标'''

    if column in sorted_column:
        last_sort_index = sorted_column[column]
        if last_sort_index.startswith('-'):
            arrow_direction = 'bottom'

        else:
            arrow_direction = 'top'
        ele = '''<span class="glyphicon glyphicon-triangle-%s" aria-hidden="true"></span>'''% arrow_direction
        return mark_safe(ele)

    return ''

@register.simple_tag
def render_paginator(querysets,admin_class,sorted_column):
    '''分页'''
    ele = '''
        <ul class="pagination">
    '''
    #page_range是所有的页，querysets.number是当前页
    for i in querysets.paginator.page_range:
        #显示前后三页，abs是绝对值
        if abs(querysets.number - i) < 3:
            active = ''
            if querysets.number == i:     #如果是当前页,class='active'
                active = 'active'
            #组合过滤字段
            filter_ele = render_filtered_args(admin_class)
            #组合排序字段
            sorted_ele = ''
            if sorted_column:
                sorted_ele = '&_o=%s'%list(sorted_column.values())[0]
            p_ele = '''<li class="%s"><a href="?page=%s%s%s">%s</a></li>'''%(active,i,filter_ele,sorted_ele,i)
            ele += p_ele
    ele += "</ul>"
    return mark_safe(ele)

@register.simple_tag
def get_current_sorted_column_index(sorted_column):
    #三元运算，如果为True执行左边的，为False，执行右边的（''）
    return list(sorted_column.values())[0] if sorted_column else ''


@register.simple_tag
def get_obj_field_val(form_obj,field):
    '''获取只读字段的值'''

    return getattr(form_obj.instance,field)


@register.simple_tag
def get_available_m2m_data(field_name,form_obj,admin_class):
    '''返回的是m2m字段关联表的所有数据'''
    #获取字段的对象
    field_obj = admin_class.model._meta.get_field(field_name)
    #consult_courses = models.ManyToManyField('Course',verbose_name='咨询课程')
    #consult_courses是一个m2m，通过consult_courses对象获取到Course（也就是获取到所有咨询的课程）
    #所有咨询课程的集合
    obj_list = set(field_obj.related_model.objects.all())
    #如果是change
    if form_obj.instance.id:
        #选中的咨询课程集合
        selected_data = set(getattr(form_obj.instance, field_name).all())
        #返回的时候，集合求差集，得到未选中的咨询课程（左边）
        return obj_list - selected_data
    else:
        return obj_list

@register.simple_tag
def get_selected_m2m_data(field_name,form_obj,admin_class):
    '''返回已选的m2m数据'''
    #如果是change
    if form_obj.instance.id:
        #获取被选中的数据
        selected_data = getattr(form_obj.instance,field_name).all()
        return selected_data
    else:
        return []


@register.simple_tag
def display_all_related_objs(obj):
    """
    显示要被删除对象的所有关联对象
    """
    ele = "<ul><b style='color:red'>%s</b>" % obj

    #获取所有反向关联的对象
    for reversed_fk_obj in obj._meta.related_objects:
        #获取所有反向关联对象的表名
        related_table_name =  reversed_fk_obj.name
        # 通过表名反向查所有关联的数据
        related_lookup_key = "%s_set" % related_table_name
        related_objs = getattr(obj,related_lookup_key).all()
        ele += "<li>%s<ul> "% related_table_name
        #get_internal_type(),获取字段的类型，如果是m2m，就不需要深入查找
        if reversed_fk_obj.get_internal_type() == "ManyToManyField":  # 不需要深入查找
            for i in related_objs:
                ele += "<li><a href='/kingadmin/%s/%s/%s/change/'>%s</a> 记录里与[%s]相关的的数据将被删除</li>" \
                       % (i._meta.app_label,i._meta.model_name,i.id,i,obj)
        #如果不是m2m，就递归查找所有关联的数据
        else:
            for i in related_objs:
                ele += "<li><a href='/kingadmin/%s/%s/%s/change/'>%s</a></li>" %(i._meta.app_label,
                                                                                 i._meta.model_name,
                                                                                 i.id,i)
                #递归查找
                ele += display_all_related_objs(i)

        ele += "</ul></li>"

    ele += "</ul>"

    return ele

@register.simple_tag
def get_model_verbose_name(admin_class):

    return admin_class.model._meta.verbose_name