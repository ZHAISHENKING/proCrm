# kingadmin/admin_base.py

import json
from django.shortcuts import render

class BaseKingAdmin(object):

    def __init__(self):
        self.actions.extend(list(set(self.default_actions)))

    list_display = []
    list_filter = []
    search_fields = []
    #只读
    readonly_fields = []
    filter_horizontal = []
    list_per_page = 5
    default_actions = ['delete_selected_objs']
    actions = []


    def delete_selected_objs(self,request,querysets):

        querysets_ids = json.dumps([i.id for i in querysets])

        return render(request,'kingadmin/table_obj_delete.html',{'admin_class':self,      #self就是admin_class
                                                                 'objs':querysets,
                                                                 'querysets_ids':querysets_ids
                                                                 })