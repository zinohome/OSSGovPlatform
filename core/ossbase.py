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


class OssBase:
    def __init__(self):
        log.info("OssBase Connect to: %s" % settings.arangodb_hosts)
        self._client1 = ArangoClient(hosts = settings.arangodb_hosts)
        self._client2 = ArangoClient(hosts = settings.arangodb_hosts)
        self._client3 = ArangoClient(hosts = settings.arangodb_hosts)
        #self._db = self._client.db(name=settings.arangodb_database, username=settings.arangodb_user, password=settings.arangodb_password)
        self._cp = ConnectionPool([self._client1, self._client2, self._client3], dbname=settings.arangodb_database, username=settings.arangodb_user, password=settings.arangodb_password)

    @property
    def db(self):
        return self._cp._db


if __name__ == '__main__':
    ossbase = OssBase().db
    log.debug(ossbase)