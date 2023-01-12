#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: AgileOps

import traceback
import simplejson as json

from utils.amis_admin import amis,admin
from utils.amis_admin.amis import PageSchema

from models.db_models.coldef import ColDef
from core import i18n as _
from utils.log import log as log

class ColAdmin(admin.ModelAdmin):
    # 继承自ModelAdmin，因此ModelAdmin(BaseModelAdmin, PageAdmin) 的方法都可以重写
    group_schema = None
    page_schema = PageSchema(label=_('Collections'), page_title=_('Collections'), icon='fas fa-table')
    model = ColDef
    pk_name = 'coldef_id'
    enable_bulk_create = True
    list_display = [ColDef.coldef_id, ColDef.coldef_name, ColDef.keyfieldname, ColDef.createdate, ColDef.modifiedate]
    search_fields = [ColDef.coldef_id, ColDef.coldef_name, ColDef.keyfieldname, ColDef.createdate, ColDef.modifiedate]

    def __init__(self, app: "AdminApp"):
        # 初始化
        log.debug('app = %s' % app)
        # app: apps.admin.admin.HostAdminApp
        super().__init__(app)