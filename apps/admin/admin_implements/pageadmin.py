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

from models.db_models.pagedef import PageDef
from utils.amis_admin import amis,admin
from utils.amis_admin.amis import PageSchema

from core import i18n as _
from utils.log import log as log

class PageAdmin(admin.ModelAdmin):
    # 继承自ModelAdmin，因此ModelAdmin(BaseModelAdmin, PageAdmin) 的方法都可以重写
    group_schema = None
    page_schema = PageSchema(label=_('Pages'), page_title=_('Pages'), icon='fas fa-outdent')
    model = PageDef
    pk_name = 'pagedef_id'
    enable_bulk_create = True
    list_display = [PageDef.pagedef_name, PageDef.pagedef_title, PageDef.createdate, PageDef.modifiedate]
    search_fields = [PageDef.pagedef_name, PageDef.pagedef_title, PageDef.createdate, PageDef.modifiedate]

    def __init__(self, app: "AdminApp"):
        # 初始化
        log.debug('app = %s' % app)
        # app: apps.admin.admin.HostAdminApp
        super().__init__(app)