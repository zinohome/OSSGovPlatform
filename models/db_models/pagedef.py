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
from typing import Optional, List
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
    pagedef_title: str = models.Field(title=_('pagedef_title'), nullable=False,
                                       amis_form_item=amis.InputText(name='pagedef_title', label=_('pagedef_title'), unique='false', disabled=False),
                                       amis_table_column='')
    pagedef: Optional[List[dict]] = models.Field(default=None, index=False, title=_('pagedef'), nullable=True,
                                                sa_column=Column(JSON),
                                                amis_form_item=amis.Combo(type='combo', label=_('pagedef'),
                                                                          id='input_combo_coldef',
                                                                          items=[
                                                                              amis.InputText(name='name',
                                                                                             label=_('Name'),
                                                                                             unique='true'),
                                                                              amis.InputText(name='type',
                                                                                             label=_('Type'), options=[
                                                                                      {"label": _("bool"),
                                                                                       "value": "bool"},
                                                                                      {"label": _("number"),
                                                                                       "value": "number"},
                                                                                      {"label": _("string"),
                                                                                       "value": "string"}],
                                                                                             creatable=False,
                                                                                             clearable=False,
                                                                                             resetValue='string'),
                                                                              amis.Switch(name='required',
                                                                                          label=_('Required'),
                                                                                          onText=_('Yes'),
                                                                                          offText=_('No'),
                                                                                          trueValue=True,
                                                                                          falseValue=False),
                                                                              amis.Switch(name='allow_none',
                                                                                          label=_('Allow_None'),
                                                                                          onText=_('Yes'),
                                                                                          offText=_('No'),
                                                                                          trueValue=True,
                                                                                          falseValue=False)
                                                                          ],
                                                                          canAccessSuperData=True,
                                                                          tabsMode=False,
                                                                          addable=True,
                                                                          removable=True,
                                                                          tabsStyle='line',
                                                                          multiple=True,
                                                                          draggable=True,
                                                                          deleteConfirmText=_('Confirm to delete?'),
                                                                          tabsLabelTpl='${coldef[${index}].name}'),
                                                amis_table_column=amis.TableColumn(type='json', levelExpand=0))
    createdate: Optional[str] = models.Field(default=datetime_util.now(), title=_('createdate'), nullable=False,
                                             amis_form_item=amis.InputDatetime(name='createdate', label=_('createdate'),
                                                                               inputFormat='YYYY-MM-DD HH:mm:ss',
                                                                               format='YYYY-MM-DD HH:mm:ss',
                                                                               value='now', disabled=True),
                                             amis_table_column=amis.TableColumn(type='date'))
    modifiedate: Optional[str] = models.Field(default=datetime_util.now(), title=_('modifiedate'), nullable=False,
                                              amis_form_item=amis.InputDatetime(name='modifiedate',
                                                                                label=_('modifiedate'),
                                                                                inputFormat='YYYY-MM-DD HH:mm:ss',
                                                                                format='YYYY-MM-DD HH:mm:ss',
                                                                                value='now', disabled=True),
                                              amis_table_column=amis.TableColumn(type='date'))

