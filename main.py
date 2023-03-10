#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Practitioner

import os
import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware

from core.sysbase import SysBase
from models.db_models.navdef import NavDef
from models.db_models.coldef import ColDef
from models.db_models.pagedef import PageDef
from models.db_models.relationdef import RelationDef
from models.db_models.graphdef import GraphDef
from utils.sqlalchemy_database import Database
from sqlmodel import SQLModel, create_engine
from starlette.responses import RedirectResponse
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from fastapi_utils.timing import add_timing_middleware
from starlette_exporter import PrometheusMiddleware, handle_metrics

from core.adminsite import site
from core.settings import settings
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from utils.log import log as log
from utils.toolkit import sync_uri
from core import i18n as _

from jaeger_client import Config as jaeger_config
from opentracing.scope_managers.contextvars import ContextVarsScopeManager
from opentracing_instrumentation.client_hooks import install_all_patches

from starlette_opentracing import StarletteTracingMiddleWare

# Initialize Tables
asyncurl = str(site.db.engine.sync_engine.url)
syncurl = sync_uri(asyncurl)
syncengine = create_engine(syncurl, echo=False)
metatables = GraphDef.metadata.tables
log.debug(metatables.keys())
Database(syncengine).run_sync(SQLModel.metadata.create_all, tables=[metatables['auth_user_roles'],
                                                                    metatables['auth_user_groups'],
                                                                    metatables['auth_group_roles'],
                                                                    metatables['auth_role_permissions'],
                                                                    metatables['auth_user'],
                                                                    metatables['auth_role'],
                                                                    metatables['auth_group'],
                                                                    metatables['auth_permission'],
                                                                    metatables['oss_coldef'],
                                                                    metatables['oss_navdef'],
                                                                    metatables['oss_pagedef'],
                                                                    metatables['oss_relationdef'],
                                                                    metatables['oss_graphdef'],
                                                                    metatables['auth_token']], is_session=False)
syncengine.dispose()
sysbase = SysBase()
sysbase.initossbase()
sysbase=None

# API prefix
prefix = settings.api_prefix
if prefix.startswith('/'):
    pass
else:
    prefix = '/' + prefix

# Create fastapi app
app = FastAPI(debug=settings.debug,
              title=settings.site_title,
              description=settings.site_description,
              version=settings.version,
              openapi_url=prefix + "/openapi.json",
              docs_url=None,
              redoc_url=None
              )

# fastapi_utils.timing profiling
add_timing_middleware(app, record=log.debug, prefix="app", exclude="untimed")
# asgi-correlation-id
app.add_middleware(CorrelationIdMiddleware)
# starlette_exporter
app.add_middleware(
    PrometheusMiddleware,
    app_name=settings.server_name,
    prefix='admin',
    labels={
        "server_name": os.getenv("HOSTNAME"),
    },
    group_paths=True,
    buckets=[0.1, 0.25, 0.5],
    skip_paths=['/health'],
    always_use_int_status=False)
app.add_route("/metrics", handle_metrics)

'''
# jaeger_tracer
opentracing_config = jaeger_config(
    config={
        "sampler": {"type": "const", "param": 1},
        "logging": True,
        "local_agent": {"reporting_host": settings.jaeger_host},
    },
    scope_manager=ContextVarsScopeManager(),
    service_name=settings.server_name,
)
jaeger_tracer = opentracing_config.initialize_tracer()
install_all_patches()
app.add_middleware(StarletteTracingMiddleWare, tracer=jaeger_tracer)
'''

# setup app
from apps import admin
admin.setup(app)

# mount admin app
site.mount_app(app)

@app.on_event("startup")
async def startup():

    from core.adminsite import auth
    await auth.create_role_user(role_key='admin')
    await auth.create_role_user(role_key='writer')
    await auth.create_role_user(role_key='reader')

    #from core.adminsite import scheduler
    #scheduler.start()

@app.get('/', include_in_schema=False)
async def index():
    return RedirectResponse(url=site.router_path)

# 1.?????? CORSMiddleware
from starlette.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,  # ??????????????????
    allow_credentials=True,  # ?????? cookie
    allow_methods=["*"],  # ???????????????????????????
    allow_headers=["*"]  # ??????????????? Headers
)

# 2. ????????????????????????
app.mount("/static", StaticFiles(directory="apps/static"), name="static")

# 3.?????? Swagger UI CDN
from fastapi.openapi.docs import get_swagger_ui_html
@app.get("/apidocs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-dist@4/swagger-ui-bundle.js",
        swagger_favicon_url="/static/favicon.ico",
        swagger_css_url="/static/swagger-ui-dist@4/swagger-ui.css",
    )
@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

# 4.?????? Redoc CDN
@app.get("/apiredoc", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="/static/redoc/redoc.standalone.js",
        redoc_favicon_url="/static/favicon.ico",
        with_google_fonts=False,
    )


