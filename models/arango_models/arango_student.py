#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2022 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2022
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Practitioner

import traceback

import simplejson as json
import os
from arango_orm import Collection
from marshmallow.fields import *
from core.ossbase import OssBase
from core.settings import settings
from core import i18n as _
from utils.log import log as log
import uuid


class Arango_Student(Collection):
    __collection__ = 'student'
    _index = [{'type':'hash', 'fields':['id'], 'unique':True}]
    _key = String(required=True)
    id = String(required=True, allow_none=False)
    name = String(required=True, allow_none=False)
    age = Integer(required=True, allow_none=False)
    teachers = String(required=True, allow_none=False)
    subjects = String(required=True, allow_none=False)

    def hasCollection(self):
        try:
            ossbase = OssBase().db
            if ossbase.has_collection(self.__collection__):
                return True
            else:
                return False
        except Exception as exp:
            log.error('Exception at Arango_Student.hasCollection() %s ' % exp)
            if settings.app_exception_detail:
                traceback.print_exc()
            return False;

    def existedDocument(self, document_key):
        try:
            ossbase = OssBase().db
            if ossbase.has(Arango_Student, document_key):
                return True
            else:
                return False
        except Exception as exp:
            log.error('Exception at Arango_Student.existedDocument() %s ' % exp)
            if settings.app_exception_detail:
                traceback.print_exc()
            return False

    def create(self, list):
        try:
            ossbase = OssBase().db
            count = len(list)
            addobj = None
            for item in list:
                if not item.__contains__('id'):
                    item['id'] = str(uuid.uuid4()).replace('-','')
                else:
                    item['id'] = str(uuid.uuid4()).replace('-','')
                if not item.__contains__('_key'):
                    item['_key'] = item['id']
                if not self.existedDocument(item['id']):
                    addobj = Arango_Student._load(item)
                    ossbase.add(addobj)
                else:
                    count = count - 1
            if count == 1:
                return addobj
            return count
        except Exception as exp:
            log.error('Exception at Arango_Student.create() %s ' % exp)
            if settings.app_exception_detail:
                traceback.print_exc()

    def query(self, request, paginator, filters):
        ossbase = OssBase().db
        sortstr = paginator.orderBy + ' ' + paginator.orderDir
        filterstr = ''
        first = True
        for k,v in filters.__dict__.items():
            if first:
                first = False if v != '[~]' else True
                filterstr = filterstr + f"LIKE(rec.{k}, '%{v.replace('[~]','')}%')" if v != '[~]' else filterstr
            else:
                filterstr = filterstr + f" AND LIKE(rec.{k}, '%{v.replace('[~]','')}%')" if v != '[~]' else filterstr
        if len(filterstr.strip()) > 0:
            if len(sortstr.strip()) > 0:
                records = ossbase.query(Arango_Student).filter(filterstr, prepend_rec_name=False).sort(
                    paginator.orderBy + ' ' + paginator.orderDir).limit(
                    paginator.perPage, start_from=(paginator.page - 1) * paginator.perPage).all()
            else:
                records = ossbase.query(Arango_Student).filter(filterstr, prepend_rec_name=False).limit(
                    paginator.perPage, start_from=(paginator.page - 1) * paginator.perPage).all()

        else:
            if len(sortstr.strip()) > 0:
                records = ossbase.query(Arango_Student).sort(paginator.orderBy + ' ' + paginator.orderDir).limit(
                    paginator.perPage, start_from=(paginator.page - 1) * paginator.perPage).all()
            else:
                records = ossbase.query(Arango_Student).limit(paginator.perPage,
                                                              start_from=(paginator.page - 1) * paginator.perPage).all()
        return records, ossbase.query(Arango_Student).count()

    @property
    def dict(self):
        jdict = self.__dict__.copy()
        del jdict['_dirty']
        del jdict['_refs_vals']
        del jdict['_instance_schema']
        del jdict['_db']
        del jdict['_key']
        # del jdict['__collection__']
        # jdict.update((k, str(v)) for k, v in jdict.items())
        return jdict