#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Practitioner

from fastapi import APIRouter, Depends

from models.db_models.coldef import ColDef
from utils.user_auth.auth.models import User
from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import create_async_engine
import traceback
import simplejson as json
from utils.log import log as log
from core import i18n as _
from core.adminsite import site, auth

router = APIRouter(prefix='/admin', tags=['admin'], dependencies=[Depends(auth.requires()())])

@router.get('/get_home_statis',
         tags=["admin"],
         summary="Get homepage statistics infomation.",
         description="Get homepage statistics infomation",
         include_in_schema=False)
async def get_home_statis():
    try:
        returndict = {'status':0,'msg':_("Welcom to use Capricornus")}
        datadict = {
                            'items': [
                                {
                                    'avatarTX': 'Host',
                                    'title': _('Host'),
                                    'subtitle': _('Number of Hosts'),
                                    'usenum': 2,
                                    'sysnum': 10,
                                    'tag':'Data'
                                },
                                {
                                    'avatarTX': 'Inventory',
                                    'title': _('Inventory'),
                                    'subtitle': _('Number of Inventorys'),
                                    'usenum': 4,
                                    'sysnum': 12,
                                    'tag':'Data'
                                },
                                {
                                    'avatarTX': 'Job',
                                    'title': 'Job',
                                    'subtitle': _('Number of Jobs'),
                                    'usenum': 21,
                                    'sysnum': 44,
                                    'tag':'System'
                                },
                                {
                                    'avatarTX': 'Error',
                                    'title': _('Error'),
                                    'subtitle': _('Number of Errors'),
                                    'usenum': 2,
                                    'sysnum': 35,
                                    'tag':'Admin'
                                }
                            ]
                        }
        systablenum = 30
        sysviewnum = 40
        curtablenum = 25
        curviewnum = 23
        sysusernum = 3
        sysapinum = 3 + 5*systablenum + 2*sysviewnum
        curapinum = 3 + 5 * curtablenum + 2 * curviewnum
        datadict['items'][0]['usenum'] = curtablenum
        datadict['items'][0]['sysnum'] = systablenum
        datadict['items'][1]['usenum'] = curviewnum
        datadict['items'][1]['sysnum'] = sysviewnum
        datadict['items'][2]['usenum'] = curapinum
        datadict['items'][2]['sysnum'] = sysapinum
        datadict['items'][3]['usenum'] = sysusernum
        datadict['items'][3]['sysnum'] = sysusernum
        returndict['data'] = datadict
        #log.debug(returndict)
        return returndict
    except Exception as e:
        log.error('Get home statistics Error !')
        traceback.print_exc()
        return returndict

# relation model select
@router.get('/get_relation_model_select_options',
         tags=["admin"],
         summary="Get relation model select options list.",
         description="Return relation model select options list",
         include_in_schema=True)
async def get_relation_model_select_options():
    try:
        returndict = {'status':1,'msg':_("Get relation mode select options Error")}
        stmt = select(ColDef)
        result = (await site.db.async_scalars(stmt)).all()
        if len(result) > 0:
            datalist = []
            for col in result:
                datalist.append({'label':col.coldef_name,'value':col.coldef_name})
            returndict['status'] = 0
            returndict['msg'] = 'Success'
            returndict['data'] = datalist
        return returndict
    except Exception as e:
        log.error('Get datasource select options Error !')
        traceback.print_exc()
        return returndict

# relation model field select
@router.get('/get_relation_model_field_select_options',
         tags=["admin"],
         summary="Get relation model field select options list.",
         description="Return relation model field select options list",
         include_in_schema=True)
async def get_relation_model_field_select_options(coldefname: str):
    try:
        returndict = {'status':1,'msg':_("Get relation mode field select options Error")}
        stmt = select(ColDef).where(ColDef.coldef_name == coldefname)
        result = (await site.db.async_scalars(stmt)).all()
        if len(result) == 1:
            col = result[0]
            datalist = []
            for obj in col.coldef:
                datalist.append({'label': obj['name'], 'value': obj['name']})
            returndict['status'] = 0
            returndict['msg'] = 'Success'
            returndict['data'] = datalist
        return returndict
    except Exception as e:
        log.error('Get datasource select options Error !')
        traceback.print_exc()
        return returndict
"""
Example：get_ds_select_options
"""
"""
@router.get('/get_ds_select_options',
         tags=["admin"],
         summary="Get datasource select options list.",
         description="Return datasource select options list",
         include_in_schema=False)
async def get_ds_select_options():
    try:
        returndict = {'status':1,'msg':_("Get datasource select options Error")}
        stmt = select(Datasource)
        result = (await site.db.async_scalars(stmt)).all()
        if len(result) > 0:
            datalist = []
            for ds in result:
                datalist.append({'label':ds.ds_name,'value':ds.ds_uri,'uri':ds.ds_uri})
            returndict['status'] = 0
            returndict['msg'] = 'Success'
            returndict['data'] = datalist
        return returndict
    except Exception as e:
        log.error('Get datasource select options Error !')
        traceback.print_exc()
        return returndict
"""