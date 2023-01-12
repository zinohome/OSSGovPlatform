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

class ColDef(BaseSQLModel, table=True):
    __tablename__ = 'coldef'
    #id字段默认隐藏
    coldef_id: int = models.Field(default=None, title=_('coldef_id'), primary_key=True, nullable=False)
    coldef_name: str = models.Field(title=_('coldef_name'), nullable=False,
                                       amis_form_item=amis.InputText(name='coldef_name', label=_('coldef_name'), unique='true', disabled=False),
                                       amis_table_column='')
    keyfieldname: str = models.Field(title=_('keyfieldname'), nullable=False,
                                    amis_form_item=amis.InputText(name='keyfieldname', label=_('keyfieldname'),
                                                                  unique='true', disabled=False),
                                    amis_table_column='')
    coldef: Optional[dict] = models.Field(default=None, title=_('coldef'), nullable=True, sa_column=Column(JSON),
                                              amis_form_item=amis.Textarea(name='coldef', label=_('coldef')),
                                              amis_table_column='')
    createdate: Optional[str] = models.Field(default=None, title=_('createdate'), nullable=True,
                                          amis_form_item=amis.InputDatetime(name='createdate', label=_('createdate'), inputFormat='YYYY-MM-DD HH:mm:ss'),
                                          amis_table_column=amis.TableColumn(type='date'))
    modifiedate: Optional[str] = models.Field(default=None, title=_('modifiedate'), nullable=True,
                                           amis_form_item=amis.InputDatetime(name='modifiedate', label=_('modifiedate'), inputFormat='YYYY-MM-DD HH:mm:ss'),
                                           amis_table_column=amis.TableColumn(type='date'))

