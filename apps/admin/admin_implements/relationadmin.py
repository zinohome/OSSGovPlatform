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

from models.db_models.relationdef import RelationDef
from utils.amis_admin import amis,admin
from utils.amis_admin.amis import PageSchema

from core import i18n as _
from utils.log import log as log

class RelationAdmin(admin.ModelAdmin):
    # 继承自ModelAdmin，因此ModelAdmin(BaseModelAdmin, PageAdmin) 的方法都可以重写
    group_schema = None
    page_schema = PageSchema(label=_('Relations'), page_title=_('Relations'), icon='fas fa-desktop')
    model = RelationDef
    pk_name = 'relationdef_id'
    enable_bulk_create = True
    list_display = [RelationDef.relationdef_id, RelationDef.relationdef_name, RelationDef.relationdef_from, RelationDef.relationdef_from_key, RelationDef.relationdef_to, RelationDef.relationdef_to_key, RelationDef.relationdef_relation, RelationDef.createdate, RelationDef.modifiedate]
    search_fields = [RelationDef.relationdef_id, RelationDef.relationdef_name, RelationDef.relationdef_from, RelationDef.relationdef_from_key, RelationDef.relationdef_to, RelationDef.relationdef_to_key, RelationDef.relationdef_relation, RelationDef.createdate, RelationDef.modifiedate]

    def __init__(self, app: "AdminApp"):
        # 初始化
        log.debug('app = %s' % app)
        # app: apps.admin.admin.HostAdminApp
        super().__init__(app)