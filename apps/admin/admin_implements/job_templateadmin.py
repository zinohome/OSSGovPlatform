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

from apps.admin.admin_implements.credentialadmin import CredentialAdmin
from apps.admin.admin_implements.inventoryadmin import InventoryAdmin
from apps.admin.admin_implements.jobadmin import JobAdmin
from apps.admin.admin_implements.projectadmin import ProjectAdmin
from models.db_models.credential import Credential


from models.db_models.git_repo import Git_repo
from models.db_models.inventory import Inventory
from models.db_models.job import Job
from models.db_models.project import Project
from utils.amis_admin.models import Field
from utils.awx_util import awx_update_util
from utils.awxclient.awx_api_job_templates_client import AWXClient
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

class RunAction(admin.ModelAction):
    action = ActionType.Drawer(className='datetable-action-start-btn-cls', icon='fa-solid fa-play',drawer={
            "position": "right",
            "size": "xs",
            "title": _("Are you sure to launch the job?"), "tooltip": _("launch the job"),
            "body": ""
          })

    class schema(BaseModel):
        pass

    async def get_action(self, request: Request, **kwargs) -> Action:
        #action = self.action
        action = self.action or ActionType.Drawer(label=_("launch the job"), drawer=Drawer())
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
        jt:Job_template = await Job_templateAdmin.get_by_id(item_id[0])
        # 项目同步
        project:Project = await ProjectAdmin.get_by_id(jt.project_id)
        awx_update_util.updateProject(project.awx_project_id)
        # 清单同步
        inv:Inventory = await InventoryAdmin.get_by_id(jt.inventory_id)
        awx_update_util.updateInventorySrouce(inv.awx_inventory_id)
        #执行作业模板
        awxclient = AWXClient()
        api_result = awxclient.post_job_templates_byid_launch(id=jt.awx_job_template_id,data={})
        print(api_result)
        if(api_result['code'] == 201):
            job = Job()
            job.name = jt.name + '_' + str(api_result['content']['id'])
            job.job_template_id = jt.job_template_id
            job.awx_job_id = api_result['content']['id']
            job.status = api_result['content']['status']
            await JobAdmin.add_one(job)
            return BaseApiOut(msg=_("the job has been launched"))
        else:
            return BaseApiOut(status=1,msg=_("job launch failure"))


    # async def handle(self, request: Request, item_id: List[str], data: Optional[SchemaUpdateT], **kwargs) -> BaseApiOut[Any]:
    #         print(item_id)
    #         awxclient = AWXClient()
    #         api_result = awxclient.post_job_templates_byid_launch(id=item_id[0],data={})
    #         if(api_result['code'] == 201):
    #             return BaseApiOut()
    #         else:
    #             return BaseApiOut(status=1,msg='failure')


class Job_templateAdmin(admin.ModelAdmin):
    group_schema = None
    page_schema = PageSchema(label=_('job_template'), page_title=_('job_template'), icon='fas fa-list')
    model = Job_template
    pk_name = 'job_template_id'
    pk_label = 'name'
    enable_bulk_create = False
    list_display = [Job_template.name,Job_template.description,Job_template.playbook,Job_template.forks,
                     Job_template.job_slice_count]
    search_fields = []
    create_fields = [Job_template.name,Job_template.description,Job_template.inventory_id,Job_template.credential_id,Job_template.project_id,Job_template.playbook,Job_template.forks,
                     Job_template.job_slice_count,Job_template.verbosity]
    update_fields = [Job_template.name,Job_template.description,Job_template.inventory_id,Job_template.credential_id,Job_template.project_id,Job_template.playbook,Job_template.forks,
                     Job_template.job_slice_count,Job_template.verbosity]

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

    # 添加自定义单项操作动作
    async def get_actions_on_item(self, request: Request) -> List[Action]:
        actions = await super().get_actions_on_item(request)
        action = await self.run_action.get_action(request)
        actions.append(action)
        return actions

    # 注册自定义路由
    def register_router(self):
        super().register_router()
        self.run_action = RunAction(self).register_router()
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
                jt: Job_template = data[0]
                print(jt)
                inv: Inventory = await InventoryAdmin.get_by_id(item_id=jt.inventory_id)
                print(inv)
                project: Project = await ProjectAdmin.get_by_id(item_id=jt.project_id)
                print(project)

                awx_data = {'name': jt.name, 'description': jt.description,'inventory':inv.awx_inventory_id,'project':project.awx_project_id,
                            'playbook':jt.playbook,'forks':jt.forks,'job_slice_count':jt.job_slice_count,'verbosity':jt.verbosity,
                             'organization': 1}
                print(awx_data)
                awxclient = AWXClient()
                api_result = awxclient.post_job_templates(awx_data)
                if api_result['code'] != 201:
                    log.error(api_result['content'])
                    return self.error_data_handle()
                setattr(jt, 'awx_job_template_id', api_result['content']['id'])
                setattr(jt, 'created', api_result['content']['created'])
                setattr(jt, 'modified', api_result['content']['modified'])
                stmt = insert(Job_template).values(jt.dict(exclude={"id"}))
                result = await site.db.session.execute(stmt)
                #关联凭证
                if jt.credential_id is not None:
                    credential: Credential = await CredentialAdmin.get_by_id(item_id=jt.credential_id)
                    api_result = awxclient.post_job_templates_byid_credentials(id=jt.awx_job_template_id,data={'id':credential.awx_credential_id})
                    if api_result['code'] != 204:
                        log.error(api_result['content'])
                        return self.error_data_handle()
                #awxclient.post_job_templates_byid_launch(id=jt.awx_job_template_id,data={})
            except Exception as error:
                log.error('Exception at awx_api_credentials.post_credentials() %s ' % error)
                return self.error_execute_sql(request=request, error=error)
            return BaseApiOut(data=result)

        return route

    @property
    def route_update(self) -> Callable:
        async def route(
                request: Request,
                item_id: List[str] = Depends(parser_item_id),
                data: self.schema_model = Body(...),  # type: ignore
        ):
            if not await self.has_update_permission(request, item_id, data):
                return self.error_no_router_permission(request)
            item_id = list(map(get_python_type_parse(self.pk), item_id))
            values = await self.on_update_pre(request, data, item_id=item_id)
            jt: Job_template = data

            inv: Inventory = await InventoryAdmin.get_by_id(item_id=jt.inventory_id)

            project: Project = await ProjectAdmin.get_by_id(item_id=jt.project_id)

            jtForUpdate: Job_template = await Job_templateAdmin.get_by_id(item_id[0])
            awx_data = {'name': jt.name, 'description': jt.description, 'inventory': inv.awx_inventory_id,
                        'project': project.awx_project_id,
                        'playbook': jt.playbook, 'forks': jt.forks, 'job_slice_count': jt.job_slice_count,
                        'verbosity': jt.verbosity,
                        'organization': 1}
            print(awx_data)
            awxclient = AWXClient()
            api_result = awxclient.put_job_templates_byid_(id=jtForUpdate.awx_job_template_id, data=awx_data)
            print(api_result['code'] != 200)
            if api_result['code'] != 200:
                log.error(api_result)
                return self.error_data_handle()
            values['modified'] = api_result['content']['modified']
            #关联凭证
            if jt.credential_id is not None:
                if jtForUpdate.credential_id is not None:
                    credential: Credential = await CredentialAdmin.get_by_id(item_id=jtForUpdate.credential_id)
                    api_result = awxclient.post_job_templates_byid_credentials(id=jt.awx_job_template_id,data={'id': credential.awx_credential_id,'disassociate': 'true'})
                    print(api_result)
                    if api_result['code'] != 204:
                        log.error(api_result)
                        return self.error_data_handle()
                credential: Credential = await CredentialAdmin.get_by_id(item_id=jt.credential_id)
                api_result = awxclient.post_job_templates_byid_credentials(id=jt.awx_job_template_id,data={'id':credential.awx_credential_id})
                print(api_result)
                if api_result['code'] != 204:
                    print(api_result)
                    log.error(api_result)
                    return self.error_data_handle()
            print(values)
            result = await self.db.async_run_sync(self._update_items, item_id, values)
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
            print(item_id)
            jt: Job_template = await Job_templateAdmin.get_by_id(item_id[0])
            awxclient = AWXClient()
            api_result = awxclient.delete_job_templates_byid_(jt.awx_job_template_id)
            print(api_result)
            result = await self.db.async_run_sync(self._delete_items, item_id)
            return BaseApiOut(data=result)

        return route

    async def get_by_id(item_id: int) -> Callable:
        item = await site.db.async_get(Job_template, item_id)
        return item