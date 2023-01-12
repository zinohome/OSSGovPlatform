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
from core import i18n as _

class BaseSQLModel(sqlmodel.SQLModel):
    class Config:
        use_enum_values = True
        orm_mode = True
        arbitrary_types_allowed = True

class ColDef(BaseSQLModel, table=True):
    __tablename__ = 'oss_coldef'
    #id字段默认隐藏
    coldef_id: int = models.Field(default=None, title=_('coldef_id'), primary_key=True, nullable=False)
    coldef_name: str = models.Field(title=_('coldef_name'), nullable=False,
                                       amis_form_item=amis.InputText(name='coldef_name', label=_('coldef_name'), unique='true', disabled=False),
                                       amis_table_column='')
    coldef: Optional[List[dict]] = models.Field(default=None, index=False, title=_('coldef'), nullable=False,
                                                sa_column=Column(JSON),
                                                amis_form_item=amis.Combo(type='combo', label=_('coldef'), id='input_combo_coldef',
                                                                          items=[
                                                    amis.InputText(name='name', label=_('Name'), unique='true'),
                                                    amis.InputText(name='type', label=_('Type'), options=[{"label":_("bool"),"value":"bool"},{"label":_("number"),"value":"number"},{"label":_("string"),"value":"string"}], creatable=False, clearable=False, resetValue='string'),
                                                    amis.Switch(name='required', label=_('Required'), onText=_('Yes'), offText=_('No'), trueValue=True, falseValue=False),
                                                    amis.Switch(name='allow_none', label=_('Allow_None'), onText=_('Yes'), offText=_('No'), trueValue=True, falseValue=False)
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
    keyfieldname: str = models.Field(title=_('keyfieldname'), nullable=False,
                                    amis_form_item=amis.InputText(name='keyfieldname', label=_('keyfieldname'), source='${coldef|pick:name}', creatable=False, clearable=False, disabled=False),
                                    amis_table_column='')
    createdate: Optional[str] = models.Field(default=datetime_util.now(), title=_('createdate'), nullable=False,
                                          amis_form_item=amis.InputDatetime(name='createdate', label=_('createdate'), inputFormat='YYYY-MM-DD HH:mm:ss', format='YYYY-MM-DD HH:mm:ss', value='now', disabled=True),
                                          amis_table_column=amis.TableColumn(type='date'))
    modifiedate: Optional[str] = models.Field(default=datetime_util.now(), title=_('modifiedate'), nullable=False,
                                           amis_form_item=amis.InputDatetime(name='modifiedate', label=_('modifiedate'), inputFormat='YYYY-MM-DD HH:mm:ss', format='YYYY-MM-DD HH:mm:ss', value='now', disabled=True),
                                           amis_table_column=amis.TableColumn(type='date'))

