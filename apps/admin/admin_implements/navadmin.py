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

from models.db_models.navdef import NavDef
from fastapi import Body, Depends
from utils import datetime_util
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
from utils.crud.parser import get_python_type_parse
from core import i18n as _
from utils.crud import BaseApiOut
from utils.crud.utils import parser_item_id
from utils.log import log as log

class NavAdmin(admin.ModelAdmin):
    # 继承自ModelAdmin，因此ModelAdmin(BaseModelAdmin, PageAdmin) 的方法都可以重写
    group_schema = None
    page_schema = PageSchema(label=_('Navgations'), page_title=_('Navgations'), icon='fas fa-bars')
    model = NavDef
    pk_name = 'navdef_id'
    enable_bulk_create = True
    list_display = [NavDef.navdef_order, NavDef.navdef_title, NavDef.navdef_name, NavDef.navdef_class, NavDef.createdate, NavDef.modifiedate]
    search_fields = [NavDef.navdef_order, NavDef.navdef_title, NavDef.navdef_name, NavDef.navdef_class, NavDef.createdate, NavDef.modifiedate]

    def __init__(self, app: "AdminApp"):
        # 初始化
        log.debug('app = %s' % app)
        # app: apps.admin.admin.HostAdminApp
        super().__init__(app)

    @property
    def route_create(self) -> Callable:
        async def route(
            request: Request,
            data: Union[self.schema_create, List[self.schema_create]] = Body(...),  # type: ignore
        ) -> BaseApiOut[Union[int, self.schema_model]]:  # type: ignore
            if not await self.has_create_permission(request, data):
                return self.error_no_router_permission(request)
            if not isinstance(data, list):
                data = [data]
            items = [await self.on_create_pre(request, obj) for obj in data]
            for item in items:
                if item.__contains__('createdate'):
                    item['createdate'] = datetime_util.now()
                if item.__contains__('modifiedate'):
                    item['modified'] = datetime_util.now()
            if not items:
                return self.error_data_handle(request)
            try:
                result = await self.db.async_run_sync(self._create_items, items=items)
                log.debug(result)
                log.debug(result.__dict__)
            except Exception as error:
                return self.error_execute_sql(request=request, error=error)
            return BaseApiOut(data=result)
        return route

    @property
    def route_update(self) -> Callable:
        async def route(
                request: Request,
                item_id: List[str] = Depends(parser_item_id),
                data: self.schema_update = Body(...),  # type: ignore
        ):
            if not await self.has_update_permission(request, item_id, data):
                return self.error_no_router_permission(request)
            item_id = list(map(get_python_type_parse(self.pk), item_id))
            values = await self.on_update_pre(request, data, item_id=item_id)
            if values.__contains__('modifiedate'):
                values['modifiedate'] = datetime_util.now()
            if not values:
                return self.error_data_handle(request)
            result = await self.db.async_run_sync(self._update_items, item_id, values)
            return BaseApiOut(data=result)
        return route

    @property
    def route_delete(self) -> Callable:
        async def route(
                request: Request,
                item_ids: List[str] = Depends(parser_item_id),
        ):
            if not await self.has_delete_permission(request, item_ids):
                return self.error_no_router_permission(request)
            result = await self.db.async_run_sync(self._delete_items, item_ids)
            return BaseApiOut(data=result)
        return route