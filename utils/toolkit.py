#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: AgileOps


import ast
import operator
import re
from urllib import parse
import simplejson as json
import sqlalchemy.types as satypes
from sqlalchemy.engine.url import URL
from core.settings import settings
from utils.log import log as log
from datetime import datetime

type_sql2py_dict = {}
for key in satypes.__dict__['__all__']:
    sqltype = getattr(satypes, key)
    if 'python_type' in dir(sqltype) and not sqltype.__name__.startswith('Type'):
        try:
            typeinst = sqltype()
        except TypeError as e:  # List/array wants inner-type
            typeinst = sqltype(None)
        try:
            type_sql2py_dict[sqltype.__name__] = typeinst.python_type
        except NotImplementedError:
            pass

type_py2sql_dict = {}
for key, val in type_sql2py_dict.items():
    if not val in type_py2sql_dict:
        type_py2sql_dict[val] = [key]
    else:
        type_py2sql_dict[val].append(key)

def jsonstrsort(jsonstr):
    jsonobj = json.loads(jsonstr)
    return json.dumps(jsonobj, sort_keys=True)

def getpytype(sqltype):
    pytype = None
    if type_sql2py_dict.__contains__(sqltype):
        pytype = type_sql2py_dict[sqltype]
    return pytype

def sync_uri(uri):
    db_sub, dialect_sub, drv_sub = uri.split(':')[0].split('+')[0].strip(), uri.split(':')[0].split('+')[
        1].strip(), '/' + uri.split(':/')[1].strip()
    sync_dialect_sub = ''
    if db_sub == 'sqlite':
        sync_dialect_sub = 'pysqlite'
    elif db_sub == 'mysql':
        sync_dialect_sub = 'pymysql'
    elif db_sub == 'oracle':
        sync_dialect_sub = 'cx_oracle'
    elif db_sub == 'postgresql':
        sync_dialect_sub = 'psycopg2'
    else:
        sync_dialect_sub = None
    if sync_dialect_sub is None:
        return None
    else:
        syncuri = f'{db_sub}+{sync_dialect_sub}:{drv_sub}'
    return syncuri

def get_db_type_from_uri(uri):
    db_sub = uri.split(':')[0].split('+')[0].strip()
    return db_sub

def get_db_dialect_from_uri(uri):
    db_sub = uri.split(':')[0].split('+')[1].strip()
    return db_sub

def is_json(input_str):
    try:
        json.loads(input_str)
        return True
    except:
        return False


if __name__ == '__main__':
    pass
