#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: AgileOps

from fastapi import APIRouter, Depends

from main import prefix
from utils.user_auth.auth import AuthRouter
from utils.user_auth.auth.models import User
from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import create_async_engine
import traceback
import simplejson as json
from utils.log import log as log
from core import i18n as _, settings
from core.adminsite import site, auth

router = APIRouter(prefix=prefix)
apiauthrouter = AuthRouter(auth)
for route in apiauthrouter.router.routes:
    if route.name == 'oauth_token':
        for depend in route.dependencies:
            if isinstance(depend.dependency, apiauthrouter.OAuth2):
                route.dependencies.remove(depend)
                route.dependencies.append(Depends(apiauthrouter.OAuth2(tokenUrl=f"{prefix}{apiauthrouter.router_path}/gettoken", auto_error=False)))
                break
        break
router.include_router(apiauthrouter.router)


if settings.api_ansible_backend == 'AWX':
    # Include route Authentication
    # from apps.api_endpoints.awx_endpoints import awx_api_authentication
    # router.include_router(awx_api_authentication.router, prefix="/awx", tags=["Authentication"])

    # Include route Instances
    from apps.api_endpoints.awx_endpoints import awx_api_instances

    router.include_router(awx_api_instances.router, prefix="/awx", tags=["Instances"])

    # Include route Instance Groups
    from apps.api_endpoints.awx_endpoints import awx_api_instance_groups

    router.include_router(awx_api_instance_groups.router, prefix="/awx", tags=["Instance Groups"])

    # Include route System Configuration
    from apps.api_endpoints.awx_endpoints import awx_api_system_configuration

    router.include_router(awx_api_system_configuration.router, prefix="/awx", tags=["System Configuration"])

    # Include route Settings
    from apps.api_endpoints.awx_endpoints import awx_api_settings

    router.include_router(awx_api_settings.router, prefix="/awx", tags=["Settings"])

    # Include route Dashboard
    from apps.api_endpoints.awx_endpoints import awx_api_dashboard

    router.include_router(awx_api_dashboard.router, prefix="/awx", tags=["Dashboard"])

    # Include route Organizations
    from apps.api_endpoints.awx_endpoints import awx_api_organizations

    router.include_router(awx_api_organizations.router, prefix="/awx", tags=["Organizations"])

    # Include route Users
    from apps.api_endpoints.awx_endpoints import awx_api_users

    router.include_router(awx_api_users.router, prefix="/awx", tags=["Users"])

    # Include route Projects
    from apps.api_endpoints.awx_endpoints import awx_api_projects

    router.include_router(awx_api_projects.router, prefix="/awx", tags=["Projects"])

    # Include route Project Updates
    from apps.api_endpoints.awx_endpoints import awx_api_project_updates

    router.include_router(awx_api_project_updates.router, prefix="/awx", tags=["Project Updates"])

    # Include route Teams
    from apps.api_endpoints.awx_endpoints import awx_api_teams

    router.include_router(awx_api_teams.router, prefix="/awx", tags=["Teams"])

    # Include route Credentials
    from apps.api_endpoints.awx_endpoints import awx_api_credentials

    router.include_router(awx_api_credentials.router, prefix="/awx", tags=["Credentials"])

    # Include route Credential Types
    from apps.api_endpoints.awx_endpoints import awx_api_credential_types

    router.include_router(awx_api_credential_types.router, prefix="/awx", tags=["Credential Types"])

    # Include route Inventories
    from apps.api_endpoints.awx_endpoints import awx_api_inventories

    router.include_router(awx_api_inventories.router, prefix="/awx", tags=["Inventories"])

    # Include route Custom Inventory Scripts
    from apps.api_endpoints.awx_endpoints import awx_api_custom_inventory_scripts

    router.include_router(awx_api_custom_inventory_scripts.router, prefix="/awx", tags=["Custom Inventory Scripts"])

    # Include route Inventory Sources
    from apps.api_endpoints.awx_endpoints import awx_api_inventory_sources

    router.include_router(awx_api_inventory_sources.router, prefix="/awx", tags=["Inventory Sources"])

    # Include route Inventory Updates
    from apps.api_endpoints.awx_endpoints import awx_api_inventory_updates

    router.include_router(awx_api_inventory_updates.router, prefix="/awx", tags=["Inventory Updates"])

    # Include route Groups
    from apps.api_endpoints.awx_endpoints import awx_api_groups

    router.include_router(awx_api_groups.router, prefix="/awx", tags=["Groups"])

    # Include route Hosts
    from apps.api_endpoints.awx_endpoints import awx_api_hosts

    router.include_router(awx_api_hosts.router, prefix="/awx", tags=["Hosts"])

    # Include route Job Templates
    from apps.api_endpoints.awx_endpoints import awx_api_job_templates

    router.include_router(awx_api_job_templates.router, prefix="/awx", tags=["Job Templates"])

    # Include route Jobs
    from apps.api_endpoints.awx_endpoints import awx_api_jobs

    router.include_router(awx_api_jobs.router, prefix="/awx", tags=["Jobs"])

    # Include route Job Events
    from apps.api_endpoints.awx_endpoints import awx_api_job_events

    router.include_router(awx_api_job_events.router, prefix="/awx", tags=["Job Events"])

    # Include route Job Host Summaries
    from apps.api_endpoints.awx_endpoints import awx_api_job_host_summaries

    router.include_router(awx_api_job_host_summaries.router, prefix="/awx", tags=["Job Host Summaries"])

    # Include route Ad Hoc Commands
    from apps.api_endpoints.awx_endpoints import awx_api_ad_hoc_commands

    router.include_router(awx_api_ad_hoc_commands.router, prefix="/awx", tags=["Ad Hoc Commands"])

    # Include route Ad Hoc Command Events
    from apps.api_endpoints.awx_endpoints import awx_api_ad_hoc_command_events

    router.include_router(awx_api_ad_hoc_command_events.router, prefix="/awx", tags=["Ad Hoc Command Events"])

    # Include route System Job Templates
    from apps.api_endpoints.awx_endpoints import awx_api_system_job_templates

    router.include_router(awx_api_system_job_templates.router, prefix="/awx", tags=["System Job Templates"])

    # Include route System Jobs
    from apps.api_endpoints.awx_endpoints import awx_api_system_jobs

    router.include_router(awx_api_system_jobs.router, prefix="/awx", tags=["System Jobs"])

    # Include route Schedules
    from apps.api_endpoints.awx_endpoints import awx_api_schedules

    router.include_router(awx_api_schedules.router, prefix="/awx", tags=["Schedules"])

    # Include route Roles
    from apps.api_endpoints.awx_endpoints import awx_api_roles

    router.include_router(awx_api_roles.router, prefix="/awx", tags=["Roles"])

    # Include route Notification Templates
    from apps.api_endpoints.awx_endpoints import awx_api_notification_templates

    router.include_router(awx_api_notification_templates.router, prefix="/awx", tags=["Notification Templates"])

    # Include route Notifications
    from apps.api_endpoints.awx_endpoints import awx_api_notifications

    router.include_router(awx_api_notifications.router, prefix="/awx", tags=["Notifications"])

    # Include route Labels
    from apps.api_endpoints.awx_endpoints import awx_api_labels

    router.include_router(awx_api_labels.router, prefix="/awx", tags=["Labels"])

    # Include route Unified Job Templates
    from apps.api_endpoints.awx_endpoints import awx_api_unified_job_templates

    router.include_router(awx_api_unified_job_templates.router, prefix="/awx", tags=["Unified Job Templates"])

    # Include route Unified Jobs
    from apps.api_endpoints.awx_endpoints import awx_api_unified_jobs

    router.include_router(awx_api_unified_jobs.router, prefix="/awx", tags=["Unified Jobs"])

    # Include route Activity Streams
    from apps.api_endpoints.awx_endpoints import awx_api_activity_streams

    router.include_router(awx_api_activity_streams.router, prefix="/awx", tags=["Activity Streams"])

    # Include route Workflow Job Templates
    from apps.api_endpoints.awx_endpoints import awx_api_workflow_job_templates

    router.include_router(awx_api_workflow_job_templates.router, prefix="/awx", tags=["Workflow Job Templates"])

    # Include route Workflow Jobs
    from apps.api_endpoints.awx_endpoints import awx_api_workflow_jobs

    router.include_router(awx_api_workflow_jobs.router, prefix="/awx", tags=["Workflow Jobs"])

    # Include route Workflow Job Template Nodes
    from apps.api_endpoints.awx_endpoints import awx_api_workflow_job_template_nodes

    router.include_router(awx_api_workflow_job_template_nodes.router, prefix="/awx",
                              tags=["Workflow Job Template Nodes"])

    # Include route Workflow Job Nodes
    from apps.api_endpoints.awx_endpoints import awx_api_workflow_job_nodes

    router.include_router(awx_api_workflow_job_nodes.router, prefix="/awx", tags=["Workflow Job Nodes"])

    # Include route Credential Input Sources
    from apps.api_endpoints.awx_endpoints import awx_api_credential_input_sources

    router.include_router(awx_api_credential_input_sources.router, prefix="/awx", tags=["Credential Input Sources"])

    # Include route Metrics
    from apps.api_endpoints.awx_endpoints import awx_api_metrics

    router.include_router(awx_api_metrics.router, prefix="/awx", tags=["Metrics"])

    # Include route Workflow Approval Templates
    from apps.api_endpoints.awx_endpoints import awx_api_workflow_approval_templates

    router.include_router(awx_api_workflow_approval_templates.router, prefix="/awx",
                              tags=["Workflow Approval Templates"])

    # Include route Workflow Approvals
    from apps.api_endpoints.awx_endpoints import awx_api_workflow_approvals

    router.include_router(awx_api_workflow_approvals.router, prefix="/awx", tags=["Workflow Approvals"])

elif settings.api_ansible_backend == 'SEMAPHORE':

    # Semaphore: Include route Instance Project
    from apps.api_endpoints.semaphore_endpoints import semaphore_project
    router.include_router(semaphore_project.router, prefix="/semaphore", tags=["Project"])

    # Semaphore: Include route Instance template
    from apps.api_endpoints.semaphore_endpoints import semaphore_project_templates
    router.include_router(semaphore_project_templates.router, prefix="/semaphore", tags=["Project-Template"])

    # Semaphore: Include route Instance Views
    from apps.api_endpoints.semaphore_endpoints import semaphore_project_views
    router.include_router(semaphore_project_views.router, prefix="/semaphore", tags=["Project-View"])

    # Semaphore: Include route Instance Tasks
    from apps.api_endpoints.semaphore_endpoints import semaphore_project_tasks
    router.include_router(semaphore_project_tasks.router, prefix="/semaphore", tags=["Project-Task"])

    # Semaphore: Include route Instance Users
    from apps.api_endpoints.semaphore_endpoints import semaphore_users
    router.include_router(semaphore_users.router, prefix="/semaphore", tags=["User"])

    # Semaphore: Include route Instance Defaults
    from apps.api_endpoints.semaphore_endpoints import semaphore_default
    router.include_router(semaphore_default.router, prefix="/semaphore", tags=["Default"])

    # Semaphore: Include route Instance Projects
    from apps.api_endpoints.semaphore_endpoints import semaphore_projects
    router.include_router(semaphore_projects.router, prefix="/semaphore", tags=["Projects"])

    # Semaphore: Include route Instance Schedules
    from apps.api_endpoints.semaphore_endpoints import semaphore_project_schedules
    router.include_router(semaphore_project_schedules.router, prefix="/semaphore", tags=["Schedule"])
else:
    pass

