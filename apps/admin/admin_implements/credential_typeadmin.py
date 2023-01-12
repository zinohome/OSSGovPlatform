#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Capricornus

from typing import List, Callable
from utils.amis_admin import admin
from utils.amis_admin.amis import PageSchema, TableColumn, Form, Action, ActionType, LevelEnum
from starlette.requests import Request
import simplejson as json
from utils.log import log as log
from models.db_models.credential_type import Credential_type
from core import i18n as _
from core.adminsite import site
class Credential_typeAdmin(admin.ModelAdmin):
    group_schema = None
    page_schema = PageSchema(label=_('credential_type'), page_title=_('credential_type'), icon='fas fa-layer-group')
    model = Credential_type
    pk_name = 'credential_type_id'
    enable_bulk_create = True
    list_display = [Credential_type.name,Credential_type.description,Credential_type.kind,Credential_type.created,Credential_type.modified]
    search_fields = []
    create_fields = [Credential_type.name,Credential_type.description,Credential_type.kind]
    async def get_update_action(self, request: Request, bulk: bool = False) -> Action:
        u_action = await super().get_update_action(request, bulk)
        if not bulk:
            drawer = u_action.drawer
            actions = []
            actions.append(Action(actionType='cancel', label=_('Cancel'), level=LevelEnum.default))
            actions.append(Action(actionType='submit', label=_('Submit'), level=LevelEnum.primary))
            drawer.actions = actions
        return u_action

    async def get_update_form(self, request: Request, bulk: bool = False) -> Form:
        u_form = await super().get_update_form(request, bulk)
        return u_form

    '''
    async def get_list_columns(self, request: Request) -> List[TableColumn]:
        c_list = await super().get_list_columns(request)
        for column in c_list:
            column.quickEdit = None
        return c_list
    '''

    async def get_by_id(item_id: int) -> Callable:
        item = await site.db.async_get(Credential_type, item_id)
        return item