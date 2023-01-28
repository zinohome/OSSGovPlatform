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
from pathlib import Path
from typing import List
from utils.amis_admin.admin.settings import Settings as AmisSettings

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(AmisSettings):
    # 基础配置
    name: str = 'Practitioner'
    host: str = '0.0.0.0'
    port: int = 8880
    debug: bool = False
    secret_key: str = 'veheyyw6pv1nqtjsdbgt56yhn0hbhjltn42k7nlaikl4rn62bwewawq0qt9o6723'
    site_icon: str = '/static/favicon.ico'
    language: str = 'zh_CN'
    amis_cdn: str = '/static/'
    amis_theme: str = 'cxd'
    allow_origins: List[str] = ["*"]

    # arangodb
    arangodb_hosts: str = 'http://192.168.32.112:8529'
    arangodb_sys_database: str = '_system'
    arangodb_database: str = '_system'
    arangodb_user: str = 'root'
    arangodb_password: str = 'passw0rd'

    # 服务器配置
    server_name: str = 'Practitioner-server'
    server_core_origins: str = '[*]'

    # API配置
    api_prefix: str = "/api/v1"
    api_access_token_expire_minutes: int = 60 * 24 * 7
    api_debug: bool = False



settings = Settings(_env_file=os.path.join(BASE_DIR, '.env'))


if __name__ == '__main__':
    print(settings.arangodb_hosts)
    print(settings.debug)
    print(settings.version)
    print(settings.site_description)
    print(settings.api_prefix)
    print(settings.secret_key)
    print(settings.amis_cdn)
    print(settings.database_url_async)
    print(settings.allow_origins)