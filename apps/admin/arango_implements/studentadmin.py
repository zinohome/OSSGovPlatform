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
import sqlalchemy.sql.selectable
from fastapi import Body, Depends
from sqlalchemy import insert, delete

from core.adminsite import site
from models.db_models.pagedef import PageDef
from models.sql_models.student import Student
from utils import datetime_util, toolkit
from utils.amis_admin import amis,admin
from utils.amis_admin.amis import PageSchema
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Pattern,
    Tuple,
    Type,
    Union,
)
from starlette.requests import Request
from models.db_models.coldef import ColDef
from utils.crud.parser import get_python_type_parse
from core import i18n as _
from utils.crud import BaseApiOut, SQLModelCrud, ItemListSchema
from utils.crud.utils import parser_item_id
from utils.log import log as log

class StudentAdmin(admin.ModelAdmin):
    group_schema = None
    page_schema = PageSchema(label=_('Student'), page_title=_('Student'), icon='fas fa-table')
    model = Student
    pk_name = 'name'
    enable_bulk_create = True
    list_display = [Student.id, Student.name, Student.age, Student.teachers, Student.subjects]
    search_fields = [Student.id, Student.name, Student.age, Student.teachers, Student.subjects]

    def __init__(self, app: "AdminApp"):
        # 初始化
        log.debug('app = %s' % app)
        # app: apps.admin.admin.HostAdminApp
        super().__init__(app)
