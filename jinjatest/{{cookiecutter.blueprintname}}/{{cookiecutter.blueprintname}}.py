"""
{{cookiecutter.os}} with GUI Multi-VM Blueprint on {{cookiecutter.hypervisor}}
"""
from calm.dsl.builtins import *
from calm.dsl.store import Secret
from calm.dsl.runbooks import CalmEndpoint as Endpoint

import os, json
from ruamel import yaml

##Loading Calm Environment specific configs
CALM_ENVIRONMENT = os.environ['CALM_ENVIRONMENT'].lower()
CALM_SITE = CALM_ENVIRONMENT.split("-")[0]
CALM_ENV_CONFIG_PATH = os.path.join("../../gsk-environments",CALM_SITE,(CALM_ENVIRONMENT + "-config.yaml"))
CALM_ENV_CONFIG = yaml.safe_load(read_file(CALM_ENV_CONFIG_PATH, depth=3))

# Define Credentials
# run make init-local-store to ensure passwords are in local store
DefaultCreds = basic_cred(CALM_ENV_CONFIG["windows-os"]["global"]["default_creds_user"], Secret.find('windows_default_creds_pass'), name="admin", default=True)
InfobloxGridCreds = basic_cred(CALM_ENV_CONFIG["windows-os"]["global"]["infoblox_creds_user"], Secret.find('infoblox_creds_pass'), name="InfobloxGrid", default=False)
VCenterCreds = basic_cred(CALM_ENV_CONFIG["vmware_project"]["vcenter_creds_user"], Secret.find('vcenter_creds_pass'), name="VCenter_Acct", default=False)

# Define downloadable image configuration
image_spec= read_spec("specs/esx-image-spec.yaml")
image_spec["image"]["name"] = CALM_ENV_CONFIG["windows-os"]["windows2019standard"]["vmware_template"]["name"]
image_spec["image"]["source"] = CALM_ENV_CONFIG["windows-os"]["windows2019standard"]["vmware_template"]["source_uri"]
image_spec["product"]["version"] = CALM_ENV_CONFIG["windows-os"]["windows2019standard"]["vmware_template"]["product_version"]

ESX_WINDOWS_IMAGE = vm_disk_package(name=image_spec["image"]["name"], config=image_spec)

# Define Services
class Win_VM_Provision(Service):

{%- if cookiecutter.add_AD_join_action == 'yes' %}{% import 'base_blueprint_template' as base %}
{{base.joinaddomain_service_task()}}
{%- endif %}

class Package1(Package):

    services = [ref(Win_VM_Provision)]

    @action
    def __install__():
        """Package Installation Tasks"""
{%- if cookiecutter.add_AD_join_action == 'yes' %}{% import 'base_blueprint_template' as base %}
{{base.joinaddomain_package_action()}}
{%- endif %}

    @action
    def __uninstall__():
        """Package uninstallation tasks"""