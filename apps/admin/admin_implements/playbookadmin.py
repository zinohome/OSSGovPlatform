#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
from http.client import HTTPException
#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Capricornus

from typing import List, Callable,Union

import giteapy
import fastapi
from fastapi import UploadFile, File, Depends,Body
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from apps.admin.admin_implements.git_repoadmin import Git_repoAdmin
from models.db_models.git_repo import Git_repo
from utils.amis_admin import admin
from utils.amis_admin.amis import PageSchema, TableColumn, Action, Form, ActionType, LevelEnum, AmisAPI, \
    DisplayModeEnum, InputExcel, InputTable, InputFile, Select
from starlette.requests import Request
import simplejson as json

from utils.crud import CrudEnum, BaseApiOut, ItemListSchema
from utils.gitea import gitea_cli
from utils.log import log as log
from models.db_models.playbook import Playbook
from core import i18n as _
from utils.amis_admin import models, amis
from core.adminsite import site
from utils.crud.utils import parser_item_id
from sqlalchemy import select, update

class PlaybookAdmin(admin.ModelAdmin):
    group_schema = None
    page_schema = PageSchema(label=_('playbook'), page_title=_('playbook'), icon='far fa-file-alt')
    model = Playbook
    pk_name = 'playbook_id'
    pk_label = 'name'
    enable_bulk_create = False
    list_display = [Playbook.name,Playbook.description,Playbook.path,Playbook.tag,Playbook.download_url]
    search_fields = []
    create_fields = [Playbook.name,Playbook.description,Playbook.git_repo_id,Playbook.path,Playbook.tag,Playbook.file]
    update_fields = [Playbook.name,Playbook.description,Playbook.tag,Playbook.file]


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
        extra = {}
        if not bulk:
            fields = self.schema_update.__fields__.values()
            if self.schema_read:
                extra["initApi"] = f"get:{self.router_path}/item/${self.pk_name}"
        else:
            api = f"{self.router_path}/item/" + "${ids|raw}"
            fields = self.bulk_update_fields
        return Form(
            api=AmisAPI(
                method="put",
                url=f"{self.router_path}/item/${self.pk_name}",
                # # 修改dataType
                dataType='form-data'
            ),
            name=CrudEnum.update,
            body=await self._conv_modelfields_to_formitems(request, fields, CrudEnum.update),
            submitText=None,
            trimValues=True,
            **extra,
        )

    '''
    async def get_list_columns(self, request: Request) -> List[TableColumn]:
        c_list = await super().get_list_columns(request)
        for column in c_list:
            column.quickEdit = None
        return c_list
    '''

    async def get_create_form(self, request: Request, bulk: bool = False) -> Form:
        fields = [field for field in self.schema_create.__fields__.values() if field.name != self.pk_name]
        if not bulk:
            return Form(
                api=f"post:{self.router_path}/item",
                name=CrudEnum.create,
                body=await self._conv_modelfields_to_formitems(request, fields, CrudEnum.create),
            )
        columns, keys = [], {}
        for field in fields:
            column = await self.get_list_column(request, self.parser.get_modelfield(field))
            keys[column.name] = "${" + column.label + "}"
            column.name = column.label
            columns.append(column)
        return Form(
            api=AmisAPI(
                method="post",
                url=f"{self.router_path}/item",
                data={"&": {"$excel": keys}},
                #修改dataType
                dataType='form-data'
            ),
            mode=DisplayModeEnum.normal,
            body=[
                InputExcel(name="excel"),
                InputTable(
                    name="excel",
                    showIndex=True,
                    columns=columns,
                    addable=True,
                    copyable=True,
                    editable=True,
                    removable=True,
                ),
            ],
        )

    @property
    def route_create(self) -> Callable:
        async def route(
            file: UploadFile = File(),
            name: str = fastapi.Form(),
            # repo: str = fastapi.Form(),
            path: str = fastapi.Form(),
            description: str = fastapi.Form(),
            tag: str = fastapi.Form(),
            git_repo_id: int = fastapi.Form()
        ):
            print(git_repo_id)
            #repo = await site.db.async_get(Git_repo, git_repo_id)
            repo = await Git_repoAdmin.get_by_id(git_repo_id)
            print(repo.name)
            #repo = 'repo-test'
            fileContent = await file.read()
            filepath = path + '/' + file.filename
            # b64encode编码
            base64_data = base64.b64encode(fileContent)
            # 去除编码base64标记，创建CreateFileOptions
            body = giteapy.CreateFileOptions(content=base64_data.decode('utf-8'))
            try:
                # Create a file in a repository
                gitea_cli.repo_api_cli.repo_create_file(repo.owner, repo.name, filepath, body)
                api_response = gitea_cli.repo_api_cli.repo_get_contents(repo.owner, repo.name, filepath)
                item = {
                        'name':name,
                        'description':description,
                        'path':filepath,
                        'git_repo_id':git_repo_id,
                        'download_url':api_response.download_url,
                        'sha':api_response.sha,
                        'tag':tag
                        }
                items = []
                items.append(item)
                result = await self.db.async_run_sync(self._create_items, items=items)
                return BaseApiOut(data=result)
            except Exception as e:
                print("Exception when calling RepositoryApi->repo_create_file: %s\n" % e)

                raise HTTPException(status_code=400, detail=e)
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
            body = giteapy.DeleteFileOptions(sha=items.sha)  # DeleteFileOptions |
            try:
                # Delete a file in a repository
                api_response = gitea_cli.repo_api_cli.repo_delete_file('root', 'repo-test', items.path,
                                                                       body)
                result = await self.db.async_run_sync(self._delete_items, item_id)
                print(api_response)
            except Exception as e:
                print("Exception when calling RepositoryApi->repo_delete_file: %s\n" % e)
                raise HTTPException(status_code=400, detail=e)
            return BaseApiOut(data=result)

        return route

    @property
    def route_update(self) -> Callable:
        async def route(
                item_id: int,
                file: UploadFile = File(),
                name: str = fastapi.Form(),
                description: str = fastapi.Form(),
                tag: str = fastapi.Form()
        ):
            print(item_id)
            playbook = await site.db.async_get(Playbook, item_id)
            print(playbook.git_repo_id)
            repo = await Git_repoAdmin.get_by_id(int(playbook.git_repo_id))
            fileContent = await file.read()
            # b64encode编码
            base64_data = base64.b64encode(fileContent)
            # 去除编码base64标记，创建CreateFileOptions
            body = giteapy.UpdateFileOptions(content=base64_data.decode('utf-8'),
                                             sha=playbook.sha)
            try:
                # Create a file in a repository
                gitea_cli.repo_api_cli.repo_update_file(repo.owner, repo.name, playbook.path, body)
                api_response = gitea_cli.repo_api_cli.repo_get_contents(repo.owner, repo.name, playbook.path)
                playbook.name = name
                playbook.description = description
                playbook.tag = tag
                playbook.sha = api_response.sha
                stmt = update(Playbook).where(Playbook.playbook_id == item_id).values({'description':description,'sha':api_response.sha})
                print(playbook)
                await site.db.async_execute(stmt)
                return BaseApiOut(msg="success")
            except Exception as e:
                print("Exception when calling RepositoryApi->repo_create_file: %s\n" % e)
                raise HTTPException(status_code=400, detail=e.reason)
        return route

    async def list(data: Playbook=None) -> Callable:
        #stmt = select(Playbook).options(selectinload(Playbook.git_repo))
        stmt = select(Playbook)
        result = await site.db.async_scalars(stmt)
        # for item in result.all():
        #     print(item.git_repo)
        return result.all()

