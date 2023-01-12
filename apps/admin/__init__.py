from fastapi import FastAPI

def setup(app: FastAPI):
    # 1. 导入管理应用
    from . import admin
    # 2. 导入定时任务
    from . import jobs
    # 3. 注册普通路由
    from . import apis
    app.include_router(apis.router)
    # 4. 注册Ansible API路由
    from . import ansibleapis
    app.include_router(ansibleapis.router)

