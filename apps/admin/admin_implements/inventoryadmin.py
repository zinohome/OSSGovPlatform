#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Capricornus

from fastapi import Body, Depends, HTTPException
from typing import List, Callable, Union

from sqlalchemy import insert

from apps.admin.admin_implements.credentialadmin import CredentialAdmin
from apps.admin.admin_implements.git_repoadmin import Git_repoAdmin
from models.db_models.credential import Credential

from utils.amis_admin import amis
from models.db_models.git_repo import Git_repo
from utils.awx_util import awx_update_util
from utils.awxclient.awx_api_inventories_client import AWXClient as Inv_client
from utils.awxclient.awx_api_inventory_sources_client import AWXClient as Inv_src_client
from utils.awxclient.awx_api_projects_client import AWXClient as Project_client

from utils.crud import BaseApiOut
from utils.crud.parser import get_python_type_parse
from utils.crud.utils import parser_item_id
from core.adminsite import site

from apps.admin.admin_implements.projectadmin import ProjectAdmin
from models.db_models.project import Project
from utils.amis_admin import admin
from utils.amis_admin.amis import PageSchema, TableColumn, Form, Action, ActionType, LevelEnum
from starlette.requests import Request
import simplejson as json
from utils.log import log as log
from models.db_models.inventory import Inventory
from core import i18n as _

class InventoryAdmin(admin.ModelAdmin):
    group_schema = None
    page_schema = PageSchema(label=_('inventory'), page_title=_('inventory'), icon='fas fa-dice-d6')
    model = Inventory
    pk_name = 'inventory_id'
    pk_label = 'name'
    enable_bulk_create = True
    list_display = [Inventory.name,Inventory.description,Inventory.project_id,Inventory.source_path]
    search_fields = []
    create_fields = [Inventory.name,Inventory.description,Inventory.project_id,Inventory.source_path]
    update_fields = [Inventory.name,Inventory.description,Inventory.project_id,Inventory.source_path]
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

    async def get_read_form(self, request: Request) -> Form:
        return amis.CRUD(columns=[{
          "name": "host",
          "label": "主机",
          "type": "text",
          "maxRows": 1000
        }],api=amis.AmisAPI(
                method="get",
                url=f"/custom/hosts/${self.pk_name}",
            ))
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
                inventory: Inventory = data[0]
                print(inventory)
                project: Project = await ProjectAdmin.get_by_id(item_id=inventory.project_id)
                print(project)
                inventory_awx_data = {'name': inventory.name, 'description': inventory.description,
                          'organization': 1}
                print(inventory_awx_data)
                inv_client = Inv_client()
                api_result = inv_client.post_inventories(inventory_awx_data)
                if (api_result['code'] == 201):
                    setattr(inventory, 'awx_inventory_id', api_result['content']['id'])
                    setattr(inventory, 'created', api_result['content']['created'])
                    setattr(inventory, 'modified', api_result['content']['modified'])
                    setattr(inventory, 'source', 'scm')

                    inventory_src_awx_data = {'name': inventory.name, 'description': inventory.description,
                                          'inventory':inventory.awx_inventory_id,'source':inventory.source,'source_path':inventory.source_path,
                                          'source_project':project.awx_project_id}
                    inv_src_client = Inv_src_client()
                    api_result = inv_src_client.post_inventory_sources(inventory_src_awx_data)
                    if (api_result['code'] == 201):
                        setattr(inventory, 'awx_inventory_src_id', api_result['content']['id'])
                        stmt = insert(Inventory).values(inventory.dict(exclude={"id"}))
                        result = await site.db.session.execute(stmt)
                        # 项目同步
                        awx_update_util.updateProject(project.awx_project_id)
                        # 清单同步
                        awx_update_util.updateInventorySrouce(inventory.awx_inventory_id)
                        print(result.lastrowid)
                else:
                    raise HTTPException(
                        status_code=api_result['code'],
                        detail=api_result['content']
                    )
            except Exception as error:
                log.error('Exception at awx_api_credentials.post_credentials() %s ' % error)
                return self.error_execute_sql(request=request, error=error)
            return BaseApiOut(data=result.lastrowid)

        return route

    @property
    def route_delete(self) -> Callable:
        async def route(
                request: Request,
                item_id: List[str] = Depends(parser_item_id),
        ):
            if not await self.has_delete_permission(request, item_id):
                return self.error_no_router_permission(request)
            print(item_id)
            itemForDelete: Inventory = await InventoryAdmin.get_by_id(item_id[0])
            inv_client = Inv_client()
            api_result = inv_client.delete_inventories_byid_(itemForDelete.awx_inventory_id)
            print(api_result)
            result = await self.db.async_run_sync(self._delete_items, item_id)
            return BaseApiOut(data=result)

        return route

    async def get_by_id(item_id: int) -> Callable:
        item = await site.db.async_get(Inventory, item_id)
        return item

    async def add_one(data) -> Callable:
        inventory_awx_data = {'name': data.name, 'description': data.description,
                              'organization': 1}
        inv_client = Inv_client()
        api_result = inv_client.post_inventories(inventory_awx_data)
        if api_result['code'] == 201:
            inventory = Inventory()
            inventory.name = data.name
            inventory.description = data.description
            #for temporary solution
            inventory.project_id = 2
            inventory.source = 'scm'
            inventory.source_path = 'inventory/'+ data.name
            inventory.created = api_result['content']['created']
            inventory.modified = api_result['content']['modified']
            inventory.awx_inventory_id = api_result['content']['id']

            project: Project = await ProjectAdmin.get_by_id(item_id=inventory.project_id)

            inventory_src_awx_data = {'name': inventory.name, 'description': inventory.description,
                                      'inventory': inventory.awx_inventory_id, 'source': inventory.source,
                                      'source_path': inventory.source_path,
                                      'source_project': project.awx_project_id}
            inv_src_client = Inv_src_client()
            api_result = inv_src_client.post_inventory_sources(inventory_src_awx_data)
            if (api_result['code'] == 201):
                setattr(inventory, 'awx_inventory_src_id', api_result['content']['id'])
                stmt = insert(Inventory).values(inventory.dict())
                result = await site.db.async_execute(stmt)
                #项目同步
                awx_update_util.updateProject(project.awx_project_id)
                #清单同步
                awx_update_util.updateInventorySrouce(inventory.awx_inventory_id)
            return result
        return None