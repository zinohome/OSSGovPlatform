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
from utils.amis_admin import models, amis
from typing import Optional
import sqlmodel
from core import i18n as _

class BaseSQLModel(sqlmodel.SQLModel):
    class Config:
        use_enum_values = True
        orm_mode = True
        arbitrary_types_allowed = True

class PageDef(BaseSQLModel, table=True):
    __tablename__ = 'oss_pagedef'
    #id字段默认隐藏
    pagedef_id: int = models.Field(default=None, title=_('pagedef_id'), primary_key=True, nullable=False)
    pagedef_col: str = models.Field(title=_('pagedef_col'), nullable=False,
                                       amis_form_item=amis.InputText(name='pagedef_col', label=_('pagedef_col'), unique='true', disabled=False),
                                       amis_table_column='')
    pagedef_name: str = models.Field(title=_('pagedef_name'), nullable=False,
                                       amis_form_item=amis.InputText(name='pagedef_name', label=_('pagedef_name'), unique='true', disabled=False),
                                       amis_table_column='')
    pagedef: Optional[dict] = models.Field(default=None, title=_('pagedef'), nullable=True, sa_column=Column(JSON),
                                              amis_form_item=amis.Textarea(name='pagedef', label=_('pagedef')),
                                              amis_table_column='')
    createdate: Optional[str] = models.Field(default=None, title=_('createdate'), nullable=True,
                                          amis_form_item=amis.InputDatetime(name='createdate', label=_('createdate'), inputFormat='YYYY-MM-DD HH:mm:ss'),
                                          amis_table_column=amis.TableColumn(type='date'))
    modifiedate: Optional[str] = models.Field(default=None, title=_('modifiedate'), nullable=True,
                                           amis_form_item=amis.InputDatetime(name='modifiedate', label=_('modifiedate'), inputFormat='YYYY-MM-DD HH:mm:ss'),
                                           amis_table_column=amis.TableColumn(type='date'))

