#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2022 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2022
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: OSSGovPlatform

import os
from arango import ArangoClient
from arango_orm import Database, ConnectionPool
from core.settings import settings
from core import i18n as _
from utils.log import log as log


class SysBase:
    def __init__(self):
        log.info("SysBase Connect to: %s" % settings.arangodb_hosts)
        self._client = ArangoClient(hosts = settings.arangodb_hosts)
        self._db = self._client.db(name=settings.arangodb_sys_database, username=settings.arangodb_user,
                                         password=settings.arangodb_password)
    @property
    def db(self):
        return self._db

    def initossbase(self):
        if not self._db.has_database(settings.arangodb_database):
            self._db.create_database(
                name=settings.arangodb_database,
                users=[
                    {'username':settings.arangodb_user, 'password':settings.arangodb_password, 'active':True}
                ],
            )

if __name__ == '__main__':
    sysbase = SysBase()
    log.debug(sysbase.db)
    sysbase.initossbase()
