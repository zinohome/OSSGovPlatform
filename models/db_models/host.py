#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: AgileOps

from datetime import date
from decimal import Decimal
from utils.amis_admin import models, amis
from typing import Optional
import sqlmodel
from core import i18n as _

class BaseSQLModel(sqlmodel.SQLModel):
    class Config:
        use_enum_values = True
        orm_mode = True
        arbitrary_types_allowed = True

class Host(BaseSQLModel, table=True):
    __tablename__ = 'host'
    #id字段默认隐藏
    host_id: int = models.Field(default=None, title=_('host_id'), primary_key=True, nullable=False)
    host_name: str = models.Field(title=_('host_name'), nullable=False,
                                       amis_form_item=amis.InputText(name='host_name', label=_('host_name'), unique='true', disabled=False),
                                       amis_table_column='')
    '''
    type: Optional[str] = models.Field(default=None, title=_('type'), nullable=True,
                                       amis_form_item=amis.Select(name='type', label=_('type'), options = [
                                           {'label':_('physical'),'value':'physical'},
                                           {'label':_('virtual') , 'value':'virtual'}
                                            ],
                                       creatable = True),
                                       amis_table_column='')
    '''
    description: Optional[str] = models.Field(default=None, title=_('description'), nullable=True,
                                              amis_form_item=amis.Textarea(name='description', label=_('description')),
                                              amis_table_column='')
    enabled: Optional[int] = models.Field(default=1, title=_('enabled'), nullable=True,
                                          amis_form_item=amis.Radios(name='enabled', label=_('enabled'), options = [
                                             {'label': _('Enabled'), 'value': 1},
                                             {'label': _('Disabled'), 'value': 0}
                                            ]),
                                          amis_table_column=amis.TableColumn(type='status'))
    url: Optional[str] = models.Field(default=None, title=_('url'), nullable=True,
                                      amis_form_item='',
                                      amis_table_column='')
    ip: str = models.Field(title=_('ip'), nullable=True, amis_form_item='',
                                     amis_table_column='')
    ssh_port: Optional[int] = models.Field(default=22, title=_('ssh_port'), nullable=True, amis_form_item='',
                                     amis_table_column='')
    username: Optional[str] = models.Field(default='root', title=_('username'), nullable=True, amis_form_item='',
                                           amis_table_column='')
    password: str = models.Field(title=_('password'), nullable=True, amis_form_item=amis.InputPassword(),
                                           amis_table_column='')
    awx_host_id: Optional[int] = models.Field(default=None, title=_('awx_host_id'), nullable=True, amis_form_item='',
                                              amis_table_column='')
    created: Optional[str] = models.Field(default=None, title=_('created'), nullable=True,
                                          amis_form_item=amis.InputDatetime(name='created', label=_('created'), inputFormat='YYYY-MM-DD HH:mm:ss'),
                                          amis_table_column=amis.TableColumn(type='date'))
    modified: Optional[str] = models.Field(default=None, title=_('modified'), nullable=True,
                                           amis_form_item=amis.InputDatetime(name='modified', label=_('modified'), inputFormat='YYYY-MM-DD HH:mm:ss'),
                                           amis_table_column=amis.TableColumn(type='date'))
    tag: Optional[str] = models.Field(default=None, title=_('tag'), nullable=True, amis_form_item='',
                                      amis_table_column='')

