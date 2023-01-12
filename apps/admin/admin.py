#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: AgileOps

import traceback
import simplejson as json

from utils.amis_admin.amis import PageSchema, Page
from utils.log import log as log
from core import i18n as _
import importlib
from typing import List
from core.adminsite import site
from starlette.requests import Request
from utils.amis_admin import amis,admin
from utils.amis_admin.admin import AdminApp

# HomeAdmin
@site.register_admin
class HomeAdmin(admin.PageAdmin):
    group_schema = None
    page_schema = PageSchema(label=_('Home'), icon='fa fa-home', url='/home', isDefaultPage=True, sort=100)
    page_path = '/home'
    page = Page.parse_obj(
        {
            "type": "page",
            "title": _("Home"),
            "body":{
                "type": "service",
                "api": "/admin/get_home_statis",
                "body": [
                    {
                        "type": "cards",
                        "source": "${items}",
                        "columnsCount": 4,
                        "card": {
                            "type": "card",
                            "className": "m-b-none",
                            "header": {
                                "avatarText": "${avatarTX}",
                                "avatarTextBackground": [
                                    "#FFB900",
                                    "#D83B01",
                                    "#B50E0E",
                                    "#E81123",
                                    "#B4009E",
                                    "#5C2D91",
                                    "#0078D7",
                                    "#00B4FF",
                                    "#008272"
                                ],
                                "title": "${title}",
                                "subTitle": "${subtitle}"
                            },
                            "body": [
                                {
                                    "name": "usenum",
                                    "id": "u:114a9393eaa4",
                                    "label": _("Current:")
                                },
                                {
                                    "name": "sysnum",
                                    "id": "u:beb3b22ee4bc",
                                    "label": _("All:")
                                }
                            ],
                            "actions": [
                                {
                                    "label": "",
                                    "type": "button",
                                    "id": "u:d26c2b0d730c"
                                }
                            ],
                            "toolbar": [
                              {
                                "type": "tpl",
                                "tpl": "${tag}",
                                "className": "label label-warning"
                              }
                            ],
                            "id": "u:ec25ab7b71bb"
                        },
                        "id": "u:c3ad6665eb77",
                        "placeholder": _("No Data Found"),
                        "title": ""
                    }
                ]
            },
            "id": "u:05f50d832729",
            "messages": {
            },
            "pullRefresh": {
            },
            "regions": [
                "body"
            ]
        }
    )

# HostAdmin
# @site.register_admin
# class AssetAdminApp(admin.AdminApp):
#     page_schema = amis.PageSchema(label=_('Asset Admin'), title='AgileOps - '+_('Asset Admin'), icon='fas fa-database', sort=99)
#     router_prefix = '/asset'
#
#     def __init__(self, app: "AssetAdminApp"):
#         super().__init__(app)
#         self.register_admin(Git_repoAdmin, PlaybookAdmin)

'''
# HostAdmin
@site.register_admin
class RepoAdminApp(admin.AdminApp):
    page_schema = amis.PageSchema(label=_('Repo Admin'), title='AgileOps - '+_('Repo Admin'), icon='fas fa-database', sort=95)
    router_prefix = '/repo'

    def __init__(self, app: "RepoAdminApp"):
        super().__init__(app)
        self.register_admin(Git_repoAdmin, PlaybookAdmin)
'''

# API docs
@site.register_admin
class DocsAdmin(admin.IframeAdmin):
    group_schema = PageSchema(label=_('APIDocs'), icon='fa fa-book', sort=-100)
    page_schema = PageSchema(label=_('Docs'), icon='fa fa-file-code')

    # src = '/apidocs'
    @property
    def src(self):
        return f'{self.app.site.settings.site_url}/apidocs'


@site.register_admin
class ReDocsAdmin(admin.IframeAdmin):
    group_schema = PageSchema(label=_('APIDocs'), icon='fa fa-book', sort=-100)
    page_schema = PageSchema(label=_('Redocs'), icon='fa fa-file-code')

    # 设置跳转链接
    @property
    def src(self):
        return f'{self.app.site.settings.site_url}/apiredoc'


@site.register_admin
class AmisDocAdmin(admin.IframeAdmin):
    group_schema = PageSchema(label=_('APIDocs'), icon='fa fa-book', sort=-100)
    page_schema = PageSchema(label=_('AmisDocument'), icon='fa fa-file-image')
    src = 'https://aisuda.bce.baidu.com/amis/zh-CN/components/html'


@site.register_admin
class AmisEditorAdmin(admin.IframeAdmin):
    group_schema = PageSchema(label=_('APIDocs'), icon='fa fa-book', sort=-100)
    page_schema = PageSchema(label=_('AmisEditor'), icon='fa fa-edit')
    src = 'https://aisuda.github.io/amis-editor-demo/'