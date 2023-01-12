import logging
from typing import Any, Union

from pydantic import BaseSettings, Field, root_validator, validator
from typing_extensions import Literal

from utils.amis_admin.amis import API


class Settings(BaseSettings):
    """Project configuration"""
    name: str = 'OSSGov'
    host: str = '0.0.0.0'
    port: int = 8880
    debug: bool = False
    secret_key: str = Field('changeit', env='SECRET_KEY')
    version: str = '0.1.6'
    site_title: str = "OSSGov"
    site_description: str = 'An OSS Governance Platform'
    site_icon: str = "https://baidu.gitee.io/amis/static/favicon_b3b0647.png"
    site_url: str = ""
    root_path: str = "/admin"
    database_url_async: str = Field("", env="DATABASE_URL_ASYNC")
    database_url: str = Field("", env="DATABASE_URL")
    language: Union[Literal["zh_CN", "en_US"], str] = Field('en_US', env='LANGUAGE')
    amis_cdn: str = "https://unpkg.com"
    amis_pkg: str = "amis@2.4.0"
    amis_theme: Literal["cxd", "antd", "dark", "ang"] =  Field('cxd', env='AMIS_THEME')
    amis_image_receiver: API = None  # Image upload interface
    amis_file_receiver: API = None  # File upload interface
    logger: Union[logging.Logger, Any] = logging.getLogger("utils.amis_admin")
    app_exception_detail: bool = Field('', env='APP_EXCEPTIONN_DETAIL')
    app_log_level: str = Field('', env='APP_LOG_LEVEL')
    app_log_filename: str = Field('', env='APP_LOG_FILENAME')

    # 服务器配置
    server_name: str = Field('OSSGov-server', env='SERVER_NAME')
    # SERVER_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    server_core_origins: str = Field('[*]', env='SERVER_CORS_ORIGINS')

    # API配置
    api_prefix: str = "/api/v1"
    api_access_token_expire_minutes: int = 60 * 24 * 7
    api_debug: bool = Field(True, env='API_DEBUG')

    @validator("amis_cdn", "root_path", "site_url", pre=True)
    def valid_url(cls, url: str):
        return url[:-1] if url.endswith("/") else url

    @root_validator(pre=True)
    def valid_database_url(cls, values):
        if not values.get("database_url") and not values.get("database_url_async"):
            values.setdefault(
                "database_url",
                "sqlite+aiosqlite:///amisadmin.db?check_same_thread=False",
            )
        return values

    @validator("amis_image_receiver", "amis_file_receiver", pre=True)
    def valid_receiver(cls, v, values):
        return v or f"post:{values.get('root_path', '')}/file/upload"
