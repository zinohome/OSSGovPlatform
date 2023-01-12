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

class RelationDef(BaseSQLModel, table=True):
    __tablename__ = 'relationdef'
    #id字段默认隐藏
    relationdef_id: int = models.Field(default=None, title=_('relationdef_id'), primary_key=True, nullable=False)
    relationdef_name: str = models.Field(title=_('relationdef_name'), nullable=False,
                                       amis_form_item=amis.InputText(name='relationdef_name', label=_('relationdef_name'), unique='true', disabled=False),
                                       amis_table_column='')
    relationdef_from: str = models.Field(title=_('relationdef_from'), nullable=False,
                                       amis_form_item=amis.InputText(name='relationdef_from', label=_('relationdef_from'), unique='true', disabled=False),
                                       amis_table_column='')
    relationdef_from_key: str = models.Field(title=_('relationdef_from_key'), nullable=False,
                                       amis_form_item=amis.InputText(name='relationdef_from_key', label=_('relationdef_from_key'), unique='true', disabled=False),
                                       amis_table_column='')
    relationdef_to: str = models.Field(title=_('relationdef_to'), nullable=False,
                                       amis_form_item=amis.InputText(name='relationdef_to', label=_('relationdef_to'), unique='true', disabled=False),
                                       amis_table_column='')
    relationdef_to_key: str = models.Field(title=_('relationdef_to_key'), nullable=False,
                                       amis_form_item=amis.InputText(name='relationdef_to_key', label=_('relationdef_to_key'), unique='true', disabled=False),
                                       amis_table_column='')
    relationdef_relation: str = models.Field(title=_('relationdef_relation'), nullable=False,
                                       amis_form_item=amis.InputText(name='relationdef_relation', label=_('relationdef_relation'), unique='true', disabled=False),
                                       amis_table_column='')
    createdate: Optional[str] = models.Field(default=None, title=_('createdate'), nullable=True,
                                          amis_form_item=amis.InputDatetime(name='createdate', label=_('createdate'), inputFormat='YYYY-MM-DD HH:mm:ss'),
                                          amis_table_column=amis.TableColumn(type='date'))
    modifiedate: Optional[str] = models.Field(default=None, title=_('modifiedate'), nullable=True,
                                           amis_form_item=amis.InputDatetime(name='modifiedate', label=_('modifiedate'), inputFormat='YYYY-MM-DD HH:mm:ss'),
                                           amis_table_column=amis.TableColumn(type='date'))

