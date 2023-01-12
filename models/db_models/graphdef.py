#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software:

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

class GraphDef(BaseSQLModel, table=True):
    __tablename__ = 'oss_graphdef'
    #id字段默认隐藏
    graphdef_id: int = models.Field(default=None, title=_('graphdef_id'), primary_key=True, nullable=False)
    graphdef_name: str = models.Field(title=_('graphdef_name'), nullable=False,
                                       amis_form_item=amis.InputText(name='graphdef_name', label=_('graphdef_name'), unique='true', disabled=False),
                                       amis_table_column='')
    graphdef_startmodel: str = models.Field(title=_('graphdef_startmodel'), nullable=False,
                                       amis_form_item=amis.InputText(name='graphdef_startmodel', label=_('graphdef_startmodel'), unique='true', disabled=False),
                                       amis_table_column='')
    graphdef_relations: str = models.Field(title=_('graphdef_relations'), nullable=False,
                                       amis_form_item=amis.InputText(name='graphdef_relations', label=_('graphdef_relations'), unique='true', disabled=False),
                                       amis_table_column='')
    createdate: Optional[str] = models.Field(default=None, title=_('createdate'), nullable=True,
                                          amis_form_item=amis.InputDatetime(name='createdate', label=_('createdate'), inputFormat='YYYY-MM-DD HH:mm:ss'),
                                          amis_table_column=amis.TableColumn(type='date'))
    modifiedate: Optional[str] = models.Field(default=None, title=_('modifiedate'), nullable=True,
                                           amis_form_item=amis.InputDatetime(name='modifiedate', label=_('modifiedate'), inputFormat='YYYY-MM-DD HH:mm:ss'),
                                           amis_table_column=amis.TableColumn(type='date'))

