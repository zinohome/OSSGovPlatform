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
from typing import List, Callable, Union, Optional, Any, Dict
import datetime
from pydantic import BaseModel
from sqlalchemy import insert, select, update
from utils import datetime_util
from apps.admin.admin_implements.inventoryadmin import InventoryAdmin
from apps.admin.admin_implements.projectadmin import ProjectAdmin
from models.db_models.credential import Credential


from models.db_models.git_repo import Git_repo
from models.db_models.inventory import Inventory
from models.db_models.job import Job, Status
from models.db_models.project import Project
from utils.amis_admin.models import Field
from utils.crud import BaseApiOut, ItemListSchema
from utils.crud.base import SchemaUpdateT, SchemaFilterT
from utils.crud.parser import get_python_type_parse
from utils.crud.utils import parser_item_id
from core.adminsite import site
from utils.awxclient.awx_api_jobs_client import AWXClient

from utils.amis_admin import admin, amis
from utils.amis_admin.amis import PageSchema, TableColumn, Form, Action, ActionType, LevelEnum, Service, Drawer, AmisAPI
from starlette.requests import Request
import simplejson as json
from utils.log import log as log
from models.db_models.job import Job
from core import i18n as _

class CancelAction(admin.ModelAction):
    #action = ActionType.Drawer(icon='fa-regular fa-circle-stop',tooltip='取消作业',drawer={
    action = ActionType.Drawer(className='datetable-action-start-btn-cls', icon='fa-regular fa-circle-stop',drawer={
            "position": "right",
            "size": "xs",
            "title": _("Are you sure you want to cancel the job?"), "tooltip": _("cancel the job"),
            "body": ""
          })

    class schema(BaseModel):
        pass

    async def get_action(self, request: Request, **kwargs) -> Action:
        #action = self.action
        action = self.action or ActionType.Drawer(label=_("cancel the job"), drawer=Drawer())
        action.drawer.title = action.drawer.title or action.label  # only override if not set
        action.drawer.body = Service(
        #action.url = Service(
            schemaApi=AmisAPI(
                method="post",
                url=f"{self.router_path+self.page_path}?item_id=${self.admin.pk_name}",
                #url=self.router_path + self.page_path + "?item_id=${IF(ids, ids, id)}",
                responseData={
                    "&": "${body}",
                    "api.url": "${body.api.url}?item_id=${api.query.item_id}",
                    "submitText": "",
                },
            )
        )
        return action

    # 动作处理
    async def handle(self, request: Request, item_id: List[int], data: schema, **kwargs) -> BaseApiOut[
        Any]:
        print(item_id)
        job:Job = await JobAdmin.get_by_id(item_id[0])
        awxclient = AWXClient()
        api_result = awxclient.post_jobs_byid_cancel(id=job.awx_job_id)
        print(api_result)
        if(api_result['code'] == 202):
            return BaseApiOut(msg=_("job cancelled successfully"))
        else:
            return BaseApiOut(status=1,msg=_("job cancelled failure"))

class LogAction(admin.ModelAction):
    #action = ActionType.Drawer(icon='fa-solid fa-code',tooltip='作业日志',drawer={
    action = ActionType.Drawer(className='datetable-action-start-btn-cls', icon='fa-solid fa-code',drawer={
            "position": "right",
            "size": "xl",
            "title": "",
            "body": ""
          })

    class schema(BaseModel):
        pass

    async def get_action(self, request: Request, **kwargs) -> Action:
        #action = self.action
        action = self.action or ActionType.Drawer(label=_("job log"), drawer=Drawer())
        action.drawer.title = action.drawer.title or action.label  # only override if not set
        action.drawer.body = amis.CRUD(columns=[{
          "name": "log",
          "label": "作业日志",
          "type": "code",
          "label": _("job log"),
          "maxRows": 1000,
          "readOnly": 'true'
        }],api=amis.AmisAPI(
                method="get",
                url=f"/custom/job_log/${self.admin.pk_name}",
            ))
        return action

    # 动作处理
    async def handle(self, request: Request, item_id: List[int], data: schema, **kwargs) -> BaseApiOut[
        Any]:
        print(item_id)
        job:Job = await JobAdmin.get_by_id(item_id[0])
        awxclient = AWXClient()
        api_result = awxclient.post_jobs_byid_cancel(id=job.awx_job_id)
        print(api_result)
        if(api_result['code'] == 202):
            return BaseApiOut(msg=_("job cancelled successfully"))
        else:
            return BaseApiOut(status=1,msg=_("job cancelled failure"))

class JobAdmin(admin.ModelAdmin):
    group_schema = None
    page_schema = PageSchema(label=_('job'), page_title=_('job'), icon='fas fa-list')
    model = Job
    pk_name = 'job_id'
    pk_label = 'name'
    enable_bulk_create = False
    list_display = [Job.name,Job.status,Job.started,Job.finished,Job.elapsed]
    search_fields = []
    update_fields = [Job.description]

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
    async def get_actions_on_item(self, request: Request) -> List[Action]:
        #actions = await super().get_actions_on_item(request)
        actions = [await self.get_delete_action(request, bulk=False)]
        log_action = await self.log_action.get_action(request)
        actions.append(log_action)
        cancel_action = await self.cancel_action.get_action(request)
        for modelfield in self.search_fields:
            formitem = await self.get_form_item(request, modelfield)
            if formitem.status == 'canceled' or formitem.status == 'pending' or formitem.status == 'new':
                actions.append(cancel_action)
        print(actions)
        return actions

    # 注册自定义路由
    def register_router(self):
        super().register_router()
        self.cancel_action = CancelAction(self).register_router()
        self.log_action = LogAction(self).register_router()


    async def on_filter_pre(self, request: Request, obj: SchemaFilterT, **kwargs) -> Dict[str, Any]:
        jobs = await JobAdmin.list(job=None)
        job_ids = []
        for job in jobs:
            job_ids.append(job.awx_job_id)
        print(job_ids)
        awxclient = AWXClient()
        api_result = awxclient.get_jobs(params={'page_size':100})
        print(api_result['content']['count'])
        for item in api_result['content']['results']:
            if item['id'] in job_ids:
                #print(item)
                for job in jobs:
                    if job.awx_job_id == item['id']:
                        job.status = item['status']
                        if item['started'] != None:
                            job.started = datetime_util.transform(item['started'])
                        if item['finished'] != None:
                            job.finished = datetime_util.transform(item['finished'])
                        if item['canceled_on'] != None:
                            job.canceled_on = datetime_util.transform(item['canceled_on'])
                        job.elapsed = item['elapsed']
                        await JobAdmin.update(job.job_id,job)
        return obj and {k: v for k, v in obj.dict(exclude_unset=True, by_alias=True).items() if v is not None}

    @property
    def route_delete(self) -> Callable:
        async def route(
                request: Request,
                item_ids: List[str] = Depends(parser_item_id),
        ):
            if not await self.has_delete_permission(request, item_ids):
                return self.error_no_router_permission(request)
            for item_id in item_ids:
                job:Job = await  JobAdmin.get_by_id(item_id)
                awxclient = AWXClient()
                api_result = awxclient.delete_jobs_byid_(id=job.awx_job_id)
                if(api_result['code']==202):
                    result = await self.db.async_run_sync(self._delete_items, item_id)
            return BaseApiOut()

        return route

    async def get_by_id(item_id: int) -> Callable:
        item = await site.db.async_get(Job, item_id)
        return item

    async def add_one(data: Job) -> Callable:
        stmt = insert(Job).values(data.dict(exclude={"id"}))
        result = await site.db.async_execute(stmt)
        return result

    async def list(job:Job) -> Callable:
        stmt = select(Job)
        result = await site.db.async_scalars(stmt)
        return result.all()

    async def update(id: int,data: Job) -> Callable:
        stmt = update(Job).where(Job.job_id == id).values(data.dict(exclude={"id"}))
        await site.db.async_execute(stmt)
        return await JobAdmin.get_by_id(id)

