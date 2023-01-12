#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import status
#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Capricornus

from fastapi import Body, Depends, HTTPException
from typing import List, Callable, Union

from sqlalchemy import insert, select

from apps.admin.admin_implements.credentialadmin import CredentialAdmin
from apps.admin.admin_implements.git_repoadmin import Git_repoAdmin
from models.db_models.credential import Credential


from models.db_models.git_repo import Git_repo
from utils.awxclient.awx_api_projects_client import AWXClient
from utils.crud import BaseApiOut
from utils.crud.parser import get_python_type_parse
from utils.crud.utils import parser_item_id
from core.adminsite import site


from typing import List
from utils.amis_admin import admin
from utils.amis_admin.amis import PageSchema, TableColumn, Form, Action, ActionType, LevelEnum
from starlette.requests import Request
import simplejson as json
from utils.log import log as log
from models.db_models.project import Project
from core import i18n as _

class ProjectAdmin(admin.ModelAdmin):
    group_schema = None
    page_schema = PageSchema(label=_('project'), page_title=_('project'), icon='fas fa-project-diagram')
    model = Project
    pk_name = 'project_id'
    pk_name = 'name'
    enable_bulk_create = True
    list_display = [Project.name,Project.description,Project.created,Project.modified]
    search_fields = []
    create_fields = [Project.name,Project.description,Project.credential_id,Project.git_repo_id]
    update_fields = [Project.name,Project.description,Project.credential_id,Project.git_repo_id]
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
                project: Project = data[0]
                print(project)
                credential: Credential = await CredentialAdmin.get_by_id(item_id=project.credential_id)
                print(credential)
                git_repo: Git_repo = await Git_repoAdmin.get_by_id(item_id=project.git_repo_id)
                print(git_repo)
                awx_data = {'name': project.name, 'description': project.description,
                            'scm_type':'git','scm_url':git_repo.clone_url,'scm_branch':git_repo.default_branch,'credential':credential.awx_credential_id,'organization':1}
                print(awx_data)
                awxclient = AWXClient()
                api_result = awxclient.post_projects(awx_data)
                if(api_result['code'] == 201):
                    setattr(project, 'awx_project_id', api_result['content']['id'])
                    setattr(project, 'scm_type', 'git')
                    setattr(project, 'created', api_result['content']['created'])
                    setattr(project, 'modified', api_result['content']['modified'])
                    stmt = insert(Project).values(project.dict(exclude={"id"}))
                    result = await site.db.session.execute(stmt)
                else:
                    raise HTTPException(
                        status_code=api_result['code'],
                        detail=api_result['content']
                    )
            except Exception as error:
                log.error('Exception at awx_api_credentials.post_credentials() %s ' % error)
                return self.error_execute_sql(request=request,error=error)
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
            try:
                item_id = list(map(get_python_type_parse(self.pk), item_id))
                values = await self.on_update_pre(request, data, item_id=item_id)
                project: Project = data
                print(project)
                credential: Credential = await CredentialAdmin.get_by_id(item_id=project.credential_id)
                print(credential)
                git_repo: Git_repo = await Git_repoAdmin.get_by_id(item_id=project.git_repo_id)
                print(git_repo)
                print(item_id)
                projectForUpdate:Project = await ProjectAdmin.get_by_id(item_id[0])
                awx_data = {'name': project.name, 'description': project.description,
                            'scm_type':'git','scm_url':git_repo.clone_url,'scm_branch':git_repo.default_branch,'credential':credential.awx_credential_id,'organization':1}
                print(awx_data)
                awxclient = AWXClient()
                api_result = awxclient.put_projects_byid_(id=projectForUpdate.awx_project_id,data=awx_data)
                print(api_result)
                if(api_result['code'] == 200):
                    values['modified']  = api_result['content']['modified']
                    result = await self.db.async_run_sync(self._update_items, item_id, values)
                else:
                    raise HTTPException(
                        status_code=api_result['code'],
                        detail=api_result['content']
                    )
            except Exception as error:
                log.error('Exception at awx_api_credentials.post_credentials() %s ' % error)
                return self.error_execute_sql(request=request,error=error)
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
            projectForDelete: Project = await ProjectAdmin.get_by_id(item_id[0])
            awxclient = AWXClient()
            api_result = awxclient.delete_projects_byid_(projectForDelete.awx_project_id)
            print(api_result)
            result = await self.db.async_run_sync(self._delete_items, item_id)
            return BaseApiOut(data=result)

        return route

    async def get_by_id(item_id: int) -> Callable:
        item = await site.db.async_get(Project, item_id)
        return item

    async def list(data=None) -> Callable:
        stmt = select(Project)
        result = await site.db.async_scalars(stmt)
        return result.all()