#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Capricornus

from fastapi import Body, Depends
from typing import List, Callable, Union

from apps.admin.admin_implements.credential_typeadmin import Credential_typeAdmin
from models.db_models.credential_type import Credential_type
from utils.awxclient.awx_api_credentials_client import AWXClient
from utils.crud.parser import get_python_type_parse
from utils.crud.utils import parser_item_id
from core.adminsite import site

from utils.amis_admin import admin
from utils.amis_admin.amis import PageSchema, TableColumn, Form, Action, ActionType, LevelEnum
from starlette.requests import Request
import simplejson as json

from utils.crud import BaseApiOut
from utils.log import log as log
from models.db_models.credential import Credential
from core import i18n as _


class CredentialAdmin(admin.ModelAdmin):
    group_schema = None
    page_schema = PageSchema(label=_('credential'), page_title=_('credential'), icon='fas fa-stream')
    model = Credential
    pk_name = 'credential_id'
    pk_label = 'name'
    enable_bulk_create = False
    list_display = [Credential.name,Credential.description,Credential.created,Credential.modified]
    search_fields = []
    create_fields = [Credential.name,Credential.description,Credential.credential_type_id,Credential.username,Credential.password,Credential.ssh_key_data]
    update_fields = [Credential.name,Credential.description,Credential.username,Credential.password,Credential.ssh_key_data]

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

    @property
    def route_create(self) -> Callable:
        async def route(
                request: Request,
                data: Union[self.schema_model, List[self.schema_model]] = Body(...),  # type: ignore
        ) -> BaseApiOut[Union[int, self.schema_model]]:  # type: ignore
            if not await self.has_create_permission(request, data):
                return self.error_no_router_permission(request)
            if not isinstance(data, list):
                data = [data]
            items = [await self.on_create_pre(request, obj) for obj in data]
            if not items:
                return self.error_data_handle(request)
            try:

                credential:Credential = data[0]
                print(credential)
                ct:Credential_type = await Credential_typeAdmin.get_by_id(credential.credential_type_id)
                print(ct)
                awxclient = AWXClient()
                awx_data = {'name':credential.name,'description':credential.description,'credential_type':ct.awx_credential_type_id
                            ,'organization':1,'inputs':{'username':credential.username,'password':credential.password,'ssh_key_data':credential.ssh_key_data}}
                print(awx_data)
                api_result = awxclient.post_credentials(awx_data)
                print(api_result)
                if(api_result['code'] == 201):
                    items[0]['awx_credential_id'] = api_result['content']['id']
                    result = await self.db.async_run_sync(self._create_items, items=items)
            except Exception as error:
                log.error('Exception at awx_api_credentials.post_credentials() %s ' % error)
                return self.error_execute_sql(request=request, error=error)
            return BaseApiOut(data=result)

        return route

    @property
    def route_delete(self) -> Callable:
        async def route(
                request: Request,
                item_id: List[str] = Depends(parser_item_id),
        ):
            if not await self.has_delete_permission(request, item_id):
                return self.error_no_router_permission(request)
            try:
                item = await site.db.async_get(Credential, item_id)
                awxclient = AWXClient()
                api_result = awxclient.delete_credentials_byid_(item.awx_credential_id)
                result = await self.db.async_run_sync(self._delete_items, item_id)
            except Exception as exp:
                log.error('Exception at awx_api_credentials.delete_credentials_byid_() %s ' % exp)
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
            credential: Credential = data
            if not values:
                return self.error_data_handle(request)
            try:
                item = await site.db.async_get(Credential, item_id)
                awx_data = {'name': credential.name, 'description': credential.description
                    ,'inputs': {'username': credential.username, 'password': credential.password,'ssh_key_data':credential.ssh_key_data}}
                awxclient = AWXClient()
                print(awx_data)
                api_result = awxclient.put_credentials_byid_(item.awx_credential_id, awx_data)
                result = await self.db.async_run_sync(self._update_items, item_id, values)
            except Exception as exp:
                log.error('Exception at awx_api_credentials.put_credentials_byid_() %s ' % exp)
            return BaseApiOut(data=result)

        return route


    async def get_by_id(item_id: int) -> Callable:
        item = await site.db.async_get(Credential, item_id)
        return item