#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import os
#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: AgileOps

from typing import List, Callable, Union, Any, Optional

import giteapy
from fastapi import Body, Depends
from pydantic import BaseModel
from sqlalchemy import select, func

from sqlmodel.sql.expression import Select

from apps.admin.admin_implements.inventoryadmin import InventoryAdmin
from apps.admin.admin_implements.playbookadmin import PlaybookAdmin
from core.adminsite import site
from models.db_models.inventory import Inventory
from utils import datetime_util
from utils.amis_admin import admin, amis
from utils.amis_admin.amis import PageSchema, TableColumn, Form, Action, ActionType, LevelEnum, Page, Service, Drawer, \
    AmisAPI
from starlette.requests import Request
import simplejson as json

from utils.amis_admin.models import Field
from utils.crud import BaseApiOut, ItemListSchema
from utils.crud.parser import get_python_type_parse
from utils.crud.utils import parser_item_id
from utils.gitea import gitea_cli
from utils.log import log as log
from models.db_models.host import Host
from core import i18n as _

class GenInventoryAction(admin.ModelAction):
    action = ActionType.Drawer(icon='fa-solid fa-list',tooltip='生成清单',drawer={
            "position": "right",
            "title": "主机-生成清单"
          })

    class schema(BaseModel):
        name: str = Field(title=_('name'), nullable=False, amis_form_item='', amis_table_column='')
        group: Optional[str] = Field(default='all',title=_('host_group_name'), nullable=False, amis_form_item='', amis_table_column='')
        description: Optional[str] = Field(default=None, title=_('description'), nullable=True,
                                                  amis_form_item='', amis_table_column='')

    async def get_action(self, request: Request, **kwargs) -> Action:
        #action = self.action
        action = self.action or ActionType.Drawer(label=_("生成清单"), drawer=Drawer())
        action.drawer.title = action.drawer.title or action.label  # only override if not set
        action.drawer.body = Service(
            schemaApi=AmisAPI(
                method="post",
                #url=f"{self.router_path+self.page_path}?item_id=${self.admin.pk_name}",
                url=self.router_path + self.page_path + "?item_id=${IF(ids, ids, id)}",
                responseData={
                    "&": "${body}",
                    "api.url": "${body.api.url}?item_id=${api.query.item_id}",
                    "submitText": "",
                },
            )
        )
        return action

    # 动作处理
    async def handle(self, request: Request, item_ids: List[int], data: schema, **kwargs) -> BaseApiOut[
        Any]:
        print(item_ids)
        # job:Job = await JobAdmin.get_by_id(item_id[0])
        # awxclient = AWXClient()
        # api_result = awxclient.post_jobs_byid_cancel(id=job.awx_job_id)
        tmp_file = data.name
        with open(tmp_file,'w') as fw:
            fw.write('['+ data.group +']' + os.linesep)
            for item_id in item_ids:
                host:Host = await HostAdmin.get_by_id(item_id)
                fw.write(host.ip)
                if host.password is not None and host.password != '':
                    fw.write(' ansible_ssh_pass=' + host.password + os.linesep)
                else:
                    fw.write(os.linesep)
        # b64encode编码
        with open(tmp_file, 'rb') as fr:
            content = fr.read()
            base64_data = base64.b64encode(content)
            # 去除编码base64标记，创建CreateFileOptions
            body = giteapy.CreateFileOptions(content=base64_data.decode('utf-8'))
            res = gitea_cli.repo_api_cli.repo_create_file('root', 'awx-repo', 'inventory/' + tmp_file, body)
        await InventoryAdmin.add_one(data)
        os.remove(tmp_file)
        return BaseApiOut(msg='清单创建成功')
        # print(api_result)
        # if(api_result['code'] == 202):
        #     return BaseApiOut(msg='作业取消成功')
        # else:
        #     return BaseApiOut(status=1,msg='作业取消失败')


class HostAdmin(admin.ModelAdmin):
    # 继承自ModelAdmin，因此ModelAdmin(BaseModelAdmin, PageAdmin) 的方法都可以重写
    group_schema = None
    page_schema = PageSchema(label=_('host'), page_title=_('host'), icon='fas fa-desktop')
    model = Host
    pk_name = 'host_id'
    pk_label = 'host_name'
    enable_bulk_create = True
    list_display = [Host.host_name, Host.enabled, Host.ip, Host.created, Host.modified]
    search_fields = [Host.host_name, Host.enabled, Host.ip, Host.created, Host.modified]
    create_fields = [Host.host_name,Host.ip,Host.ssh_port,Host.username,Host.password,Host.tag,Host.enabled]
    update_fields = [Host.host_name,Host.ip,Host.ssh_port,Host.username,Host.password,Host.tag,Host.enabled]
    def __init__(self, app: "AdminApp"):
        # 初始化
        log.debug('app = %s' % app)
        # app: apps.admin.admin.HostAdminApp
        super().__init__(app)

    async def get_select(self, request: Request) -> Select:
        l_select = await super().get_select(request)
        # 修改list 初始 select 内容
        log.debug('l_select = %s' % l_select)
        #l_select = l_select.select_from(Host).join(Inventory) # 关联的Inventory内的值可以获取
        return l_select

    async def get_page(self, request: Request) -> Page:
        # 整个crud页面
        page = await super().get_page(request)
        log.debug('page.body = %s' % page.body)
        # 可以修改page.body实现crud 页面的修改
        return page

    async def get_actions_on_header_toolbar(self, request: Request) -> List[Action]:
        # 修改curd列表工具栏
        header_toolbar = await super().get_actions_on_header_toolbar(request)
        for action in header_toolbar:
            log.debug('action = %s' % action)
        return header_toolbar

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

    async def get_actions_on_bulk(self, request: Request) -> List[Action]:
        actions = await super().get_actions_on_bulk(request)
        action = await self.gen_inventory.get_action(request)
        action.label = ''
        actions.append(action.copy())
        return actions

    # 注册自定义路由
    def register_router(self):
        super().register_router()
        # 注册动作路由
        self.gen_inventory = GenInventoryAction(self).register_router()

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
                data: Union[self.schema_create, List[self.schema_create]] = Body(...),  # type: ignore
        ) -> BaseApiOut[Union[int, self.schema_model]]:  # type: ignore
            if not await self.has_create_permission(request, data):
                return self.error_no_router_permission(request)
            if not isinstance(data, list):
                data = [data]
            items = [await self.on_create_pre(request, obj) for obj in data]
            # enhanced
            for item in items:
                item['created'] = datetime_util.now()
                item['modified'] = datetime_util.now()

            if not items:
                return self.error_data_handle(request)
            try:
                result = await self.db.async_run_sync(self._create_items, items=items)
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
            # enhanced
            values['modified'] = datetime_util.now()

            if not values:
                return self.error_data_handle(request)
            result = await self.db.async_run_sync(self._update_items, item_id, values)
            return BaseApiOut(data=result)

        return route

    async def get_by_id(item_id: int) -> Callable:
        item = await site.db.async_get(Host, item_id)
        return item