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

class NavDef(BaseSQLModel, table=True):
    __tablename__ = 'navdef'
    #id字段默认隐藏
    navdef_id: int = models.Field(default=None, title=_('navdef_id'), primary_key=True, nullable=False)
    navdef_name: str = models.Field(title=_('navdef_name'), nullable=False,
                                       amis_form_item=amis.InputText(name='navdef_name', label=_('navdef_name'), unique='true', disabled=False),
                                       amis_table_column='')
    navdef_title: str = models.Field(title=_('navdef_title'), nullable=False,
                                       amis_form_item=amis.InputText(name='navdef_title', label=_('navdef_title'), unique='true', disabled=False),
                                       amis_table_column='')
    navdef_icon: str = models.Field(title=_('navdef_icon'), nullable=False,
                                       amis_form_item=amis.InputText(name='navdef_icon', label=_('navdef_icon'), unique='true', disabled=False),
                                       amis_table_column='')
    navdef_class: str = models.Field(title=_('navdef_class'), nullable=False,
                                       amis_form_item=amis.InputText(name='navdef_class', label=_('navdef_class'), unique='true', disabled=False),
                                       amis_table_column='')
    navdef_order: str = models.Field(title=_('navdef_order'), nullable=False,
                                       amis_form_item=amis.InputText(name='navdef_order', label=_('navdef_order'), unique='true', disabled=False),
                                       amis_table_column='')
    createdate: Optional[str] = models.Field(default=None, title=_('createdate'), nullable=True,
                                          amis_form_item=amis.InputDatetime(name='createdate', label=_('createdate'), inputFormat='YYYY-MM-DD HH:mm:ss'),
                                          amis_table_column=amis.TableColumn(type='date'))
    modifiedate: Optional[str] = models.Field(default=None, title=_('modifiedate'), nullable=True,
                                           amis_form_item=amis.InputDatetime(name='modifiedate', label=_('modifiedate'), inputFormat='YYYY-MM-DD HH:mm:ss'),
                                           amis_table_column=amis.TableColumn(type='date'))

