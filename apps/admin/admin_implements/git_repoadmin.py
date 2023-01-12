#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Capricornus

from fastapi import Body, Depends, FastAPI, HTTPException, Query, Request
from typing import List, Callable, Union
from utils.amis_admin import admin
from utils.amis_admin.amis import PageSchema, TableColumn, Form, Action, ActionType, LevelEnum, Dialog
from starlette.requests import Request
import simplejson as json
from utils.log import log as log
from models.db_models.git_repo import Git_repo
from core import i18n as _
from typing import Optional
from utils.crud.schema import BaseApiOut
from utils.gitea import gitea_cli
import giteapy
from utils.crud.utils import parser_item_id
from core.adminsite import site


class Git_repoAdmin(admin.ModelAdmin):
    group_schema = None
    page_schema = PageSchema(label=_('git_repo'), page_title=_('git_repo'), icon='fas fa-code-branch')
    model = Git_repo
    pk_name = 'git_repo_id'
    pk_label = 'name'
    enable_bulk_create = False
    list_display = [Git_repo.git_repo_id,Git_repo.name,Git_repo.description,Git_repo.private,Git_repo.clone_url,Git_repo.ssh_url]
    search_fields = []
    create_fields = [Git_repo.name,Git_repo.description,Git_repo.default_branch,Git_repo.private]
    update_fields = [Git_repo.description]
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
            print(data)
            if not await self.has_create_permission(request, data):
                return self.error_no_router_permission(request)
            if not isinstance(data, list):
                data = [data]
            items = [await self.on_create_pre(request, obj) for obj in data]
            if not items:
                return self.error_data_handle(request)
            try:
                body = giteapy.CreateRepoOption(name=items[0]['name'],description=items[0]['description'])
                # Create a repository
                api_response = gitea_cli.repo_api_cli.create_current_user_repo(body=body)
                print(api_response)
                items[0]['gitea_repo_id'] = api_response.id
                items[0]['ssh_url'] = api_response.ssh_url
                items[0]['clone_url'] = api_response.clone_url
                items[0]['owner'] = api_response.owner.login
                result = await self.db.async_run_sync(self._create_items, items=items)
            except Exception as error:
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
            items = await self.db.async_run_sync(self._read_items, item_id)
            if len(items) == 1:
                items = items[0]
            print(items)
            owner = items.owner # str | owner of the repo to delete
            repo = items.name  # str | name of the repo to delete
            try:
                # Delete a repository
                gitea_cli.repo_api_cli.repo_delete(owner, repo)
            except Exception as e:
                print("Exception when calling RepositoryApi->repo_delete: %s\n" % e)
            result = await self.db.async_run_sync(self._delete_items, item_id)
            return BaseApiOut(data=result)

        return route


    async def get_by_id(item_id:int) -> Callable:
        item = await site.db.async_get(Git_repo, item_id)
        return item
