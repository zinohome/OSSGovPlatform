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
from typing import List, Callable, Union, Optional, Any

from pydantic import BaseModel
from sqlalchemy import insert

from apps.admin.admin_implements.inventoryadmin import InventoryAdmin
from apps.admin.admin_implements.job_templateadmin import Job_templateAdmin
from apps.admin.admin_implements.jobadmin import JobAdmin
from apps.admin.admin_implements.projectadmin import ProjectAdmin
from models.db_models.credential import Credential


from models.db_models.git_repo import Git_repo
from models.db_models.inventory import Inventory
from models.db_models.job import Job
from models.db_models.project import Project
from utils import datetime_util
from utils.amis_admin.models import Field
from utils.awx_util import awx_update_util
from utils.awxclient.awx_api_job_templates_client import AWXClient as Jt_client
from utils.awxclient.awx_api_schedules_client import AWXClient as Schedules_client

from utils.awxclient.awx_api_inventories_client import AWXClient as Inv_client
from utils.awxclient.awx_api_projects_client import AWXClient as Project_client
from utils.crud import BaseApiOut
from utils.crud.base import SchemaUpdateT
from utils.crud.parser import get_python_type_parse
from utils.crud.utils import parser_item_id
from core.adminsite import site

from utils.amis_admin import admin
from utils.amis_admin.amis import PageSchema, TableColumn, Form, Action, ActionType, LevelEnum, Dialog, Service, \
    AmisAPI, Drawer
from starlette.requests import Request
import simplejson as json
from utils.log import log as log
from models.db_models.job_template import Job_template
from core import i18n as _
from models.db_models.schedule import Schedule
from dateutil import rrule
from datetime import datetime
class ScheduleAdmin(admin.ModelAdmin):
    group_schema = None
    page_schema = PageSchema(label=_('schedule'), page_title=_('schedule'), icon='fas fa-list-alt')
    model = Schedule
    pk_name = 'schedule_id'
    enable_bulk_create = False
    list_display = [Schedule.name,Schedule.description,Schedule.start_time,Schedule.next_run,Schedule.unit,Schedule.interval,Schedule.enabled]
    search_fields = [Schedule.name]
    create_fields = [Schedule.name,Schedule.description,Schedule.job_template_id,Schedule.start_time,Schedule.unit,Schedule.interval,Schedule.enabled]
    update_fields = [Schedule.name,Schedule.description,Schedule.start_time,Schedule.unit,Schedule.interval,Schedule.enabled]

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
                data: Union[self.schema_create, List[self.schema_create]] = Body(...),  # type: ignore
        ) -> BaseApiOut[Union[int, self.schema_model]]:  # type: ignore
            if not await self.has_create_permission(request, data):
                return self.error_no_router_permission(request)
            if not isinstance(data, list):
                data = [data]
            items = [await self.on_create_pre(request, obj) for obj in data]
            if not items:
                return self.error_data_handle(request)
            for item in items:
                jt:Job_template = await Job_templateAdmin.get_by_id(item['job_template_id'])
                start_time = datetime.fromtimestamp(int(item['start_time']))
                #rrule.rrule(freq=item['unit'],interval=item['interval'],dtstart=start_time)
                rrule_str = str(rrule.rrule(freq=item['unit'], interval=item['interval'], dtstart=start_time)).split('\n')
                rrule_str[0] = rrule_str[0] + 'Z '
                if not rrule_str[1].__contains__('INTERVAL'):
                    rrule_str[1]  = rrule_str[1] + ';INTERVAL=1'
                #print(str(rrule.rrule(freq=item['unit'],interval=item['interval'],dtstart=start_time)).replace('\n',';'))
                awx_data = {"name":item['name'],'description':item['description'],'rrule':rrule_str[0]+rrule_str[1]}
                print(awx_data)
                jt_client = Jt_client()
                api_result = jt_client.post_job_templates_byid_schedules(id=jt.awx_job_template_id,data=awx_data)
                print(api_result)
                if(api_result['code']==201):
                    item['awx_schedule_id'] = api_result['content']['id']
                    item['next_run'] = datetime_util.handelDatetime(awx_time=api_result['content']['next_run'],format='%Y-%m-%dT%H:%M:%SZ')
                    await self.db.async_run_sync(self._create_items, items=[item])
            return BaseApiOut()

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
            if not values:
                return self.error_data_handle(request)
            print(values)
            schedule:Schedule = await ScheduleAdmin.get_by_id(item_id[0])
            start_time = datetime.fromtimestamp(int(values['start_time']))
            rrule_str = str(rrule.rrule(freq=values['unit'], interval=values['interval'], dtstart=start_time)).split(
                '\n')
            rrule_str[0] = rrule_str[0] + 'Z '
            if not rrule_str[1].__contains__('INTERVAL'):
                rrule_str[1] = rrule_str[1] + ';INTERVAL=1'
            awx_data = {"name": values['name'], 'description': values['description'],
                        'rrule': rrule_str[0] + rrule_str[1]}
            print(awx_data)
            schedules_client = Schedules_client()
            api_result = schedules_client.patch_schedules_byid_(id=schedule.awx_schedule_id,data=awx_data)
            print(api_result)
            if (api_result['code'] == 200):
                values['next_run'] = api_result['content']['next_run']
                await self.db.async_run_sync(self._update_items, item_id, values)
            return BaseApiOut()

        return route

    @property
    def route_delete(self) -> Callable:
        async def route(
                request: Request,
                item_ids: List[str] = Depends(parser_item_id),
        ):
            if not await self.has_delete_permission(request, item_ids):
                return self.error_no_router_permission(request)
            for item_id in item_ids:
                schedule: Schedule = await ScheduleAdmin.get_by_id(item_id[0])
                schedules_client = Schedules_client()
                api_result = schedules_client.delete_schedules_byid_(id=schedule.awx_schedule_id)
                print(api_result)
                if (api_result['code'] == 204):
                    await self.db.async_run_sync(self._delete_items, [item_id])
            return BaseApiOut()

        return route

    async def get_by_id(item_id: int) -> Callable:
        item = await site.db.async_get(Schedule, item_id)
        return item
