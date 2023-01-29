#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Practitioner

from sqlmodel import Column, JSON

from utils import datetime_util
from utils.amis_admin import models, amis
from typing import TYPE_CHECKING,Optional, List
import simplejson as json
import sqlmodel
from arango_orm import Collection
from core import i18n as _

class BaseSQLModel(sqlmodel.SQLModel):
    class Config:
        use_enum_values = True
        orm_mode = True
        arbitrary_types_allowed = True

class Student(BaseSQLModel, table=True):
    __tablename__ = 'student'
    __ISARANGODB__ = True
    student_id: int = models.Field(default=None, title=_('student_id'), primary_key=True, nullable=False)
    name: str = models.Field(title=_('name'), nullable=False,
                                    amis_form_item=amis.InputText(name='name', label=_('name'), disabled=False),
                                    amis_table_column='')
    age: int = models.Field(title=_('age'), nullable=False,
                                    amis_form_item=amis.InputText(name='age', label=_('age'), disabled=False),
                                    amis_table_column='')
    teachers: str = models.Field(title=_('teachers'), nullable=False,
                                    amis_form_item=amis.InputText(name='teachers', label=_('teachers'), disabled=False),
                                    amis_table_column='')
    subjects: str = models.Field(title=_('subjects'), nullable=False,
                                    amis_form_item=amis.InputText(name='subjects', label=_('subjects'), disabled=False),
                                    amis_table_column='')