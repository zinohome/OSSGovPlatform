#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: AgileOps

import os
from pathlib import Path
from typing import List
from utils.amis_admin.admin.settings import Settings as AmisSettings

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(AmisSettings):
    # 基础配置
    name: str = 'AgileOps'
    host: str = '0.0.0.0'
    port: int = 8880
    debug: bool = False
    secret_key: str = 'veheyyw6pv1nqtjsdbgt56yhn0hbhjltn42k7nlaikl4rn62bwewawq0qt9o6723'
    site_icon: str = '/static/favicon.ico'
    language: str = 'zh_CN'
    amis_cdn: str = '/static/'
    amis_theme: str = 'cxd'
    allow_origins: List[str] = ["*"]

    # 服务器配置
    server_name: str = 'AgileOps-server'
    server_core_origins: str = '[*]'

    # jaeger 配置
    jaeger_host: str = '127.0.0.1'

    # API配置
    api_prefix: str = "/api/v1"
    api_access_token_expire_minutes: int = 60 * 24 * 7
    api_ansible_backend: str = 'AWX'
    api_debug: bool = False

    # AWX Client 配置
    AWX_API_URL: str = 'http://192.168.32.1:30080/api/v2'
    AWX_USERNAME: str = 'admin'
    AWX_PASSWORD: str = 'CEJ4xaOcUxKXIbnBlevMHDcBnTHmfdja'
    AWX_TOKEN: str = None

    # Semaphore Client 配置
    semph_api_url: str = 'http://192.168.122.81:3000/api'
    semph_username: str = 'admin'
    semph_password: str = 'passw0rd'
    semph_token: str = 'loru0zlu_bvgi8vqix58mmdfawomow0lzhy-xsxubcm='

    # Gitea配置
    gitea_api_url: str = 'http://localhost:3000/api/v1'
    gitea_api_token: str = '9f18a4dc35783bdb864f92bda50dfbe94f99cbfb'


settings = Settings(_env_file=os.path.join(BASE_DIR, '.env'))


if __name__ == '__main__':
    print(settings.debug)
    print(settings.version)
    print(settings.site_description)
    print(settings.api_prefix)
    print(settings.secret_key)
    print(settings.amis_cdn)
    print(settings.database_url_async)
    print(settings.awx_api_url)
    print(settings.semph_api_url)
    print(settings.allow_origins)