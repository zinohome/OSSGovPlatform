import contextlib
from typing import Any, Callable, Dict, List, Type
from fastapi import Depends, HTTPException
from utils.amis_admin.admin import FormAdmin, ModelAdmin
from utils.amis_admin.amis.components import (
    Action,
    ActionType,
    ButtonToolbar,
    Form,
    Grid,
    Horizontal,
    Html,
    Page,
    PageSchema,
)
from utils.amis_admin.amis.constants import DisplayModeEnum, LevelEnum
from utils.crud.base import SchemaUpdateT
from utils.crud.schema import BaseApiOut
from pydantic import BaseModel
from sqlalchemy import select
from starlette import status
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import NoMatchFound
from utils.user_auth.auth import Auth
from utils.user_auth.auth.models import BaseUser, Group, Permission, Role, User
from utils.user_auth.auth.schemas import UserLoginOut
from core import i18n as _

def attach_page_head(page: Page) -> Page:
    # if page.body.submitText=='登录':
    #     title = _("Welcome to login")
    # else:
    #     title = _("Welcome to sign up")
    title=_("Welcome to login OSSGov")
    page.className="ao-signup-wrapper"
    page.body = [
        Page(
            className="ao-column-signup-left",
            style={
                'width': '70%',
                'float': 'left',
                'height': '100',
                'margin': '0',
                'padding': '0',
                'background-color': '#F3F4F8',
                'background-image': 'url(/static/images/login_picture.png)',
                'background-size': '70% 70%',
                'background-repeat': 'no-repeat',
                'background-position-x': 'center',
                'background-position-y': 'center'
            }
        ),
        Page(
            className="ao-column-signup",
            style={
                'width': '30%',
                'float': 'left',
                'height': '100',
                'margin': '0',
                'padding': '0'
            },
            body=[
                Html(
                    html=f'<div style="color: #161616; font-size: 30px; font-weight: 400; margin: 150px 0px 50px 20px">{title}</div>'
                ),
                Grid(
                    columns=[
                        {"body": [page.body], "valign": "middle"}
                    ],
                    align="left",
                    valign="middle"
                )
            ]
        )
    ]
    return page

# 登录
class UserLoginFormAdmin(FormAdmin):
    page_path = "/login"
    page_parser_mode = "html"
    schema: Type[SchemaUpdateT] = None
    schema_submit_out: Type[UserLoginOut] = None
    page_schema = None
    page_route_kwargs = {"name": "login"}

    async def handle(self, request: Request, data: SchemaUpdateT, **kwargs) -> BaseApiOut[BaseModel]:  # self.schema_submit_out
        if request.user:
            return BaseApiOut(code=1, msg=_("User logged in!"), data=self.schema_submit_out.parse_obj(request.user))
        user = await request.auth.authenticate_user(username=data.username, password=data.password)  # type:ignore
        if not user:
            return BaseApiOut(status=-1, msg=_("Incorrect username or password!"))
        if not user.is_active:
            return BaseApiOut(status=-2, msg=_("Inactive user status!"))
        token_info = self.schema_submit_out.parse_obj(user)
        auth: Auth = request.auth
        token_info.access_token = await auth.backend.token_store.write_token(user.dict())
        return BaseApiOut(code=0, data=token_info)

    @property
    def route_submit(self):
        async def route(response: Response, result: BaseApiOut = Depends(super().route_submit)):
            if result.status == 0 and result.code == 0:  # 登录成功,设置用户信息
                response.set_cookie("Authorization", f"bearer {result.data.access_token}")
            return result
        return route

    async def get_form(self, request: Request) -> Form:
        # account = _("Don`t have an account?")
        form = await super().get_form(request)
        buttons = []
        with contextlib.suppress(NoMatchFound):
            # buttons.append(
            #     Html(
            #         html=f'<div style="color: #161616; margin: 20px 0px 20px 20px">{account}</div>',
            #         className = "create-account-cls"
            #     )
            # )
            # buttons.append(
            #     ActionType.Link(
            #         actionType="link",
            #         link=f"{self.site.router_path}{self.app.router.url_path_for('reg')}",
            #         label=_("Sign up"),
            #         className="sign-up-btn-cls"
            #     )
            # )
            buttons.append(
                Action(
                    actionType="submit",
                    className="sign-in-btn-cls",
                    label=_("Sign in"),
                    level=LevelEnum.primary
                )
            )
        form.body.sort(key=lambda form_item: form_item.type, reverse=True)
        form.update_from_kwargs(
            title="",
            mode=DisplayModeEnum.horizontal,
            submitText="",
            panelClassName="",
            wrapWithPanel=True,
            horizontal=Horizontal(left=3, right=9),
            actions=[ButtonToolbar(buttons=buttons)],
        ),
        form.redirect = request.query_params.get("redirect") or "/"
        return form

    async def get_page(self, request: Request) -> Page:
        page = await super().get_page(request)
        return attach_page_head(page)

    @property
    def route_page(self) -> Callable:
        async def route(request: Request, result=Depends(super().route_page)):
            if request.user:
                raise HTTPException(
                    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                    detail="already logged in",
                    headers={"location": request.query_params.get("redirect") or "/"},
                )
            return result
        return route

    async def has_page_permission(self, request: Request) -> bool:
        return True

# 注册
class UserRegFormAdmin(FormAdmin):
    user_model: Type[BaseUser] = User
    page_path = "/reg"
    page_parser_mode = "html"
    schema: Type[SchemaUpdateT] = None
    schema_submit_out: Type[UserLoginOut] = None
    page_schema = None
    page_route_kwargs = {"name": "reg"}

    async def handle(self, request: Request, data: SchemaUpdateT, **kwargs) -> BaseApiOut[BaseModel]:  # self.schema_submit_out
        auth: Auth = request.auth
        user = await auth.db.async_scalar(select(self.user_model).where(self.user_model.username == data.username))
        if user:
            return BaseApiOut(status=-1, msg=_("Username has been registered!"), data=None)
        user = await auth.db.async_scalar(select(self.user_model).where(self.user_model.email == data.email))
        if user:
            return BaseApiOut(status=-2, msg=_("Email has been registered!"), data=None)
        values = data.dict(exclude={"id", "password"})
        values["password"] = auth.pwd_context.hash(data.password.get_secret_value())  # 密码hash保存
        user = self.user_model.parse_obj(values)
        try:
            auth.db.add(user)
            await auth.db.async_flush()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error Execute SQL：{e}",
            ) from e
        # 注册成功,设置用户信息
        token_info = self.schema_submit_out.parse_obj(user)
        token_info.access_token = await auth.backend.token_store.write_token(user.dict())
        return BaseApiOut(code=0, msg=_("Registered successfully!"), data=token_info)

    @property
    def route_submit(self):
        async def route(response: Response, result: BaseApiOut = Depends(super().route_submit)):
            if result.status == 0 and result.code == 0:  # 登录成功,设置用户信息
                response.set_cookie("Authorization", f"bearer {result.data.access_token}")
            return result
        return route

    # async def get_form(self, request: Request) -> Form:
    #     form = await super().get_form(request)
    #     form.redirect = request.query_params.get("redirect") or "/"
    #     form.update_from_kwargs(
    #         title="",
    #         mode=DisplayModeEnum.horizontal,
    #         submitText=_("Sign up"),
    #         actionsClassName="no-border m-none p-none",
    #         panelClassName="",
    #         wrapWithPanel=True,
    #         horizontal=Horizontal(left=3, right=9),
    #         actions=[
    #             ButtonToolbar(
    #                 buttons=[
    #                     ActionType.Link(
    #                         actionType="link",
    #                         link=f"{self.router_path}/login",
    #                         label=_("Sign in"),
    #                         className="sign-in-btn-cls",
    #                     ),
    #                     Action(
    #                         actionType="submit",
    #                         label=_("Sign up"),
    #                         level=LevelEnum.primary,
    #                         className="reg-sign-up-btn-cls"
    #                     )
    #                 ]
    #             )
    #         ],
    #     )
    #     return form

    async def get_page(self, request: Request) -> Page:
        page = await super().get_page(request)
        return attach_page_head(page)

    async def has_page_permission(self, request: Request) -> bool:
        return True


class UserInfoFormAdmin(FormAdmin):
    page_schema = None
    group_schema = None
    user_model: Type[BaseUser] = User
    page = Page(title=_("User Profile"))
    page_path = "/userinfo"
    schema: Type[SchemaUpdateT] = None
    schema_submit_out: Type[BaseUser] = None
    form_init = True
    form = Form(mode=DisplayModeEnum.horizontal)
    page_route_kwargs = {"name": "userinfo"}

    async def get_init_data(self, request: Request, **kwargs) -> BaseApiOut[Any]:
        return BaseApiOut(data=request.user.dict(exclude={"password"}))

    async def get_form(self, request: Request) -> Form:
        form = await super().get_form(request)
        formitems = [
            await self.get_form_item(request, modelfield)
            for k, modelfield in self.user_model.__fields__.items()
            if k not in self.schema.__fields__ and k != "password"
        ]
        form.body.extend(formitem.update_from_kwargs(disabled=True) for formitem in formitems if formitem)
        return form

    async def handle(self, request: Request, data: SchemaUpdateT, **kwargs) -> BaseApiOut[Any]:
        for k, v in data.dict().items():
            setattr(request.user, k, v)
        return BaseApiOut(data=self.schema_submit_out.parse_obj(request.user))

    async def has_page_permission(self, request: Request) -> bool:
        return await self.site.auth.requires(response=False)(request)

class UserAdmin(ModelAdmin):
    group_schema = None
    page_schema = PageSchema(label=_("User"), icon="fa fa-user")
    model: Type[BaseUser] = None
    exclude = ["password"]
    link_model_fields = [User.roles, User.groups]
    search_fields = [User.username]

    async def on_create_pre(self, request: Request, obj, **kwargs) -> Dict[str, Any]:
        data = await super(UserAdmin, self).on_create_pre(request, obj, **kwargs)
        data["password"] = request.auth.pwd_context.hash(data["password"])  # 密码hash保存
        return data

    async def on_update_pre(self, request: Request, obj, item_id: List[int], **kwargs) -> Dict[str, Any]:
        data = await super(UserAdmin, self).on_update_pre(request, obj, item_id, **kwargs)
        password = data.get("password")
        if password:
            data["password"] = request.auth.pwd_context.hash(data["password"])  # 密码hash保存
        return data

class RoleAdmin(ModelAdmin):
    group_schema = None
    page_schema = PageSchema(label=_("Role"), icon="fa fa-group")
    model = Role
    link_model_fields = [Role.permissions]
    readonly_fields = ["key"]

class GroupAdmin(ModelAdmin):
    group_schema = None
    page_schema = PageSchema(label=_("Group"), icon="fa fa-group")
    model = Group
    link_model_fields = [Group.roles]
    readonly_fields = ["key"]

class PermissionAdmin(ModelAdmin):
    group_schema = None
    page_schema = PageSchema(label=_("Permission"), icon="fa fa-lock")
    model = Permission
    readonly_fields = ["key"]
