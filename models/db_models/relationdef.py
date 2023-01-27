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
from typing import Optional
import sqlmodel
from core import i18n as _

class BaseSQLModel(sqlmodel.SQLModel):
    class Config:
        use_enum_values = True
        orm_mode = True
        arbitrary_types_allowed = True

class RelationDef(BaseSQLModel, table=True):
    __tablename__ = 'oss_relationdef'
    #id字段默认隐藏
    relationdef_id: int = models.Field(default=None, title=_('relationdef_id'), primary_key=True, nullable=False)
    relationdef_name: str = models.Field(title=_('relationdef_name'), nullable=False,
                                       amis_form_item=amis.InputText(name='relationdef_name', label=_('relationdef_name'), unique='true', disabled=False),
                                       amis_table_column='')
    relationdef_from: str = models.Field(title=_('relationdef_from'), nullable=False,
                                         amis_form_item=amis.InputText(name='relationdef_from',
                                                                       label=_('relationdef_from'), unique='false', inline='false',
                                                                       source='/admin/get_relation_model_select_options',
                                                                       creatable=False, clearable=False, disabled=False),
                                         amis_table_column='')
    relationdef_from_key: str = models.Field(title=_('relationdef_from_key'), nullable=False,
                                             amis_form_item=amis.InputText(name='relationdef_from_key',
                                                                           label=_('relationdef_from_key'),
                                                                           unique='false', inline='false',
                                                                           source='/admin/get_relation_model_field_select_options?coldefname=${relationdef_from}',
                                                                           creatable=False, clearable=False, initFetchOn='relationdef_from',
                                                                           disabled=False),
                                             amis_table_column='')
    relationdef_to: str = models.Field(title=_('relationdef_to'), nullable=False,
                                       amis_form_item=amis.InputText(name='relationdef_to', label=_('relationdef_to'),
                                                                     unique='false', inline='false',
                                                                     source='/admin/get_relation_model_select_options',
                                                                     creatable=False, clearable=False, disabled=False),
                                       amis_table_column='')
    relationdef_to_key: str = models.Field(title=_('relationdef_to_key'), nullable=False,
                                           amis_form_item=amis.InputText(name='relationdef_to_key',
                                                                         label=_('relationdef_to_key'), unique='false',
                                                                         source='/admin/get_relation_model_field_select_options?coldefname=${relationdef_to}',
                                                                         creatable=False, clearable=False,
                                                                         initFetchOn='relationdef_to',
                                                                         disabled=False),
                                           amis_table_column='')
    relationdef_relation: str = models.Field(title=_('relationdef_relation'), nullable=False,
                                     amis_form_item=amis.InputText(name='relationdef_relation', label=_('relationdef_relation'),
                                                                   options=[{"label": _("Equal"), "value": "Equal"},
                                                                            {"label": _("Contains"), "value": "Contains"},
                                                                            {"label": _("Belongs"), "value": "Belongs"}],
                                                                   creatable=False, clearable=False, resetValue='Equal'),
                                     amis_table_column='')
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

