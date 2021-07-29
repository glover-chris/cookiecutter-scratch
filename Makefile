## Set Calm GSO LAB environment variables.  Default to PHX.
## To override, pass in variables as part of the make call, e.g.,make launch-linux-bps CALM_ENVIRONMENT=calm-ams.
CALM_ENVIRONMENT ?=
export CALM_ENVIRONMENT

CALM_PROJECT := pracdev-cap
export

## Requires .calm/.local files for credentials - script to populate will come in the future.
PC_USER ?= $$(cat .local/${CALM_ENVIRONMENT}/calm_dsl_user)
PC_PASS ?= $$(cat .local/${CALM_ENVIRONMENT}/calm_dsl_pass)
export

DSL_INIT_PARAMS ?= --ip ${PC_IP_ADDRESS} --port ${PC_PORT} --username ${PC_USER} --password ${PC_PASS}

## Getting local git repository details.
GIT_COMMIT_ID     := $(shell git rev-parse --short HEAD)
GIT_BRANCH_NAME   := $(shell git rev-parse --abbrev-ref HEAD | head -c14)

## Blueprint naming variables.
BLUEPRINT_SUFFIX_NAME := ${GIT_BRANCH_NAME}-${GIT_COMMIT_ID}

LINUX_BP_NAME_DHCP := "cita-starter-lin-dhcp-${BLUEPRINT_SUFFIX_NAME}"
LINUX_BP_NAME_STATIC_IP := "cita-starter-lin-static-ip-${BLUEPRINT_SUFFIX_NAME}"
LINUX_BP_NAME_PHPIPAM := "cita-starter-lin-phpipam-${BLUEPRINT_SUFFIX_NAME}"
LINUX_BP_NAME_INFOBLOX := "cita-starter-lin-infoblox-${BLUEPRINT_SUFFIX_NAME}"
LINUX_BP_NAME_SOLARWINDS := "cita-starter-lin-solarwinds-${BLUEPRINT_SUFFIX_NAME}"
WINDOWS_BP_NAME_DHCP := "cita-starter-win-dhcp-${BLUEPRINT_SUFFIX_NAME}"
WINDOWS_BP_NAME_STATIC_IP := "cita-starter-win-static-ip-${BLUEPRINT_SUFFIX_NAME}"
WINDOWS_BP_NAME_PHPIPAM := "cita-starter-win-phpipam-${BLUEPRINT_SUFFIX_NAME}"
WINDOWS_BP_NAME_INFOBLOX := "cita-starter-win-infoblox-${BLUEPRINT_SUFFIX_NAME}"
WINDOWS_BP_NAME_SOLARWINDS := "cita-starter-win-solarwinds-${BLUEPRINT_SUFFIX_NAME}"

# Export all variables.
export

# Print environment specific values.
print-env:
	@echo CALM_ENVIRONMENT=${CALM_ENVIRONMENT}
	@echo CALM_PROJECT=$(CALM_PROJECT)
	@echo $(shell calm --version)
	@echo $(shell make --version | head -n1)
	@echo $(shell python --version | head -n1)
	@echo $(shell pip --version | awk '{print $1 " " $2}')

direnv-init:
	# load global vars first, then environment specific. Override global in environment specific
	cd ./configs/${CALM_ENVIRONMENT}
	direnv allow
	-mv .envrc .envrc.bkup
	echo dotenv configs/defaults/.env >> .envrc
	echo source_env configs/${CALM_ENVIRONMENT} >> .envrc
	direnv allow

print-vars: ## Print environment variables. i.e., make print-vars KALM_ENVIRONMENT=kalm-{environment}
	@make direnv-init CALM_ENVIRONMENT=${CALM_ENVIRONMENT}
	@ `echo env` | sort | xargs -n 1

## Initialize calm config and do some quick validations.
## CALM_PROJECT Default is pracdev-cap.  If you wish to override, pass in appropriate calm project. i.e., make init-dsl-config CALM_PROJECT=some-other-project.
init-dsl-config: print-vars
	@calm init dsl $(DSL_INIT_PARAMS) --project $(CALM_PROJECT)
	calm get projects -n ${CALM_PROJECT}
	calm get server status

####################################################################
### COOKIECUTTER TASKS - Commands to create various cookiecutter projects.
### PURPOSE: Create local Calm blueprints with cookiecutter.

cookiecutter-phx-bps-user-input:
	git submodule update --init
	cookiecutter -v ./ --config-file ./site_configuration_files/phx_config.yaml

cookiecutter-phx-bps-pipeline:
	git submodule update --init
	cookiecutter -v ./ --config-file ./site_configuration_files/phx_config.yaml --no-input

cookiecutter-phx-dhcp_bps:
	git submodule update --init
	cookiecutter -v ./ --config-file ./site_configuration_files/phx_config.yaml ipam_solution=dhcp -o ./blueprints_phx_dhcp -f --no-input

cookiecutter-phx-static_ip_bps:
	git submodule update --init
	cookiecutter -v ./ --config-file ./site_configuration_files/phx_config.yaml ipam_solution=static_ip -o ./blueprints_phx_staticip -f --no-input

cookiecutter-phx-phpipam_bps:
	git submodule update --init
	cookiecutter -v ./ --config-file ./site_configuration_files/phx_config.yaml ipam_solution=phpipam -o ./blueprints_phx_phpipam -f --no-input

cookiecutter-phx-infoblox_bps:
	git submodule update --init
	cookiecutter -v ./ --config-file ./site_configuration_files/phx_config.yaml ipam_solution=infoblox -o ./blueprints_phx_infoblox -f --no-input

cookiecutter-phx-solarwinds_bps:
	git submodule update --init
	cookiecutter -v ./ --config-file ./site_configuration_files/phx_config.yaml ipam_solution=solarwinds -o ./blueprints_phx_solarwinds -f --no-input

cookiecutter-ams-bps-user-input:
	git submodule update --init
	cookiecutter -v ./ --config-file ./site_configuration_files/ams_config.yaml

cookiecutter-ams-bps-pipeline:
	git submodule update --init
	cookiecutter -v ./ --config-file ./site_configuration_files/ams_config.yaml --no-input

cookiecutter-ams-dhcp_bps:
	git submodule update --init
	cookiecutter -v ./ --config-file ./site_configuration_files/ams_config.yaml ipam_solution=dhcp -o ./blueprints_ams_dhcp -f --no-input

cookiecutter-ams-static_ip_bps:
	git submodule update --init
	cookiecutter -v ./ --config-file ./site_configuration_files/ams_config.yaml ipam_solution=static_ip -o ./blueprints_ams_staticip -f --no-input

cookiecutter-ams-phpipam_bps:
	git submodule update --init
	cookiecutter -v ./ --config-file ./site_configuration_files/ams_config.yaml ipam_solution=phpipam -o ./blueprints_ams_phpipam -f --no-input

cookiecutter-ams-infoblox_bps:
	git submodule update --init
	cookiecutter -v ./ --config-file ./site_configuration_files/ams_config.yaml ipam_solution=infoblox -o ./blueprints_ams_infoblox -f --no-input

cookiecutter-ams-solarwinds_bps:
	git submodule update --init
	cookiecutter -v ./ --config-file ./site_configuration_files/ams_config.yaml ipam_solution=solarwinds -o ./blueprints_ams_solarwinds -f --no-input

############################################################################################################
### DEVELOPMENT TESTING - COOKIECUTTER AND CALM DSL CREATE BLUEPRINT TASKS
### PURPOSE: Create local cookiecutter projects and have calm dsl create the corresdponding blueprints in the respective sites, i.e., PHX and AMS

create-all-bps: create-phx-all_bps create-ams-all_bps

    ## PHOENIX SPECIFIC COMMANDS

create-phx-all_bps: create-phx-dhcp_bps create-phx-static_ip_bps create-phx-phpipam_bps create-phx-infoblox_bps create-phx-solarwinds_bps

create-phx-dhcp_bps:
	make cookiecutter-phx-dhcp_bps
	make init-dsl-config CALM_ENVIRONMENT=calm-phx
	calm compile bp -f ./blueprints_phx_dhcp/blueprints_phx/linux/linux_phx_blueprint.py
	calm create bp -f ./blueprints_phx_dhcp/blueprints_phx/linux/linux_phx_blueprint.py --name ${LINUX_BP_NAME_DHCP} --force
	calm compile bp -f ./blueprints_phx_dhcp/blueprints_phx/windows/windows_phx_blueprint.py
	calm create bp -f ./blueprints_phx_dhcp/blueprints_phx/windows/windows_phx_blueprint.py --name ${WINDOWS_BP_NAME_DHCP} --force

create-phx-static_ip_bps:
	make cookiecutter-phx-static_ip_bps
	make init-dsl-config CALM_ENVIRONMENT=calm-phx
	calm compile bp -f ./blueprints_phx_staticip/blueprints_phx/linux/linux_phx_blueprint.py
	calm create bp -f ./blueprints_phx_staticip/blueprints_phx/linux/linux_phx_blueprint.py --name ${LINUX_BP_NAME_STATIC_IP} --force
	calm compile bp -f ./blueprints_phx_staticip/blueprints_phx/windows/windows_phx_blueprint.py
	calm create bp -f ./blueprints_phx_staticip/blueprints_phx/windows/windows_phx_blueprint.py --name ${WINDOWS_BP_NAME_STATIC_IP} --force

create-phx-phpipam_bps:
	make cookiecutter-phx-phpipam_bps
	make init-dsl-config CALM_ENVIRONMENT=calm-phx
	calm compile bp -f ./blueprints_phx_phpipam/blueprints_phx/linux/linux_phx_blueprint.py
	calm create bp -f ./blueprints_phx_phpipam/blueprints_phx/linux/linux_phx_blueprint.py --name ${LINUX_BP_NAME_PHPIPAM} --force
	calm compile bp -f ./blueprints_phx_phpipam/blueprints_phx/windows/windows_phx_blueprint.py
	calm create bp -f ./blueprints_phx_phpipam/blueprints_phx/windows/windows_phx_blueprint.py --name ${WINDOWS_BP_NAME_PHPIPAM} --force

create-phx-infoblox_bps:
	make cookiecutter-phx-infoblox_bps
	make init-dsl-config CALM_ENVIRONMENT=calm-phx
	calm compile bp -f ./blueprints_phx_infoblox/blueprints_phx/linux/linux_phx_blueprint.py
	calm create bp -f ./blueprints_phx_infoblox/blueprints_phx/linux/linux_phx_blueprint.py --name ${LINUX_BP_NAME_INFOBLOX} --force
	calm compile bp -f ./blueprints_phx_infoblox/blueprints_phx/windows/windows_phx_blueprint.py
	calm create bp -f ./blueprints_phx_infoblox/blueprints_phx/windows/windows_phx_blueprint.py --name ${WINDOWS_BP_NAME_INFOBLOX} --force

create-phx-solarwinds_bps:
	make cookiecutter-phx-solarwinds_bps
	make init-dsl-config CALM_ENVIRONMENT=calm-phx
	calm compile bp -f ./blueprints_phx_solarwinds/blueprints_phx/linux/linux_phx_blueprint.py
	calm create bp -f ./blueprints_phx_solarwinds/blueprints_phx/linux/linux_phx_blueprint.py --name ${LINUX_BP_NAME_SOLARWINDS} --force
	calm compile bp -f ./blueprints_phx_solarwinds/blueprints_phx/windows/windows_phx_blueprint.py
	calm create bp -f ./blueprints_phx_solarwinds/blueprints_phx/windows/windows_phx_blueprint.py --name ${WINDOWS_BP_NAME_SOLARWINDS} --force

    ## AMSTERDAM SPECIFIC COMMANDS

create-ams-all_bps: create-ams-dhcp_bps create-ams-static_ip_bps create-ams-phpipam_bps create-ams-infoblox_bps create-ams-solarwinds_bps

create-ams-dhcp_bps:
	make cookiecutter-ams-dhcp_bps
	make init-dsl-config CALM_ENVIRONMENT=calm-ams
	calm compile bp -f ./blueprints_ams_dhcp/blueprints_ams/linux/linux_ams_blueprint.py
	calm create bp -f ./blueprints_ams_dhcp/blueprints_ams/linux/linux_ams_blueprint.py --name ${LINUX_BP_NAME_DHCP} --force
	calm compile bp -f ./blueprints_ams_dhcp/blueprints_ams/windows/windows_ams_blueprint.py
	calm create bp -f ./blueprints_ams_dhcp/blueprints_ams/windows/windows_ams_blueprint.py --name ${WINDOWS_BP_NAME_DHCP} --force

create-ams-static_ip_bps:
	make cookiecutter-ams-static_ip_bps
	make init-dsl-config CALM_ENVIRONMENT=calm-ams
	calm compile bp -f ./blueprints_ams_staticip/blueprints_ams/linux/linux_ams_blueprint.py
	calm create bp -f ./blueprints_ams_staticip/blueprints_ams/linux/linux_ams_blueprint.py --name ${LINUX_BP_NAME_STATIC_IP} --force
	calm compile bp -f ./blueprints_ams_staticip/blueprints_ams/windows/windows_ams_blueprint.py
	calm create bp -f ./blueprints_ams_staticip/blueprints_ams/windows/windows_ams_blueprint.py --name ${WINDOWS_BP_NAME_STATIC_IP} --force

create-ams-phpipam_bps:
	make cookiecutter-ams-phpipam_bps
	make init-dsl-config CALM_ENVIRONMENT=calm-ams
	calm compile bp -f ./blueprints_ams_phpipam/blueprints_ams/linux/linux_ams_blueprint.py
	calm create bp -f ./blueprints_ams_phpipam/blueprints_ams/linux/linux_ams_blueprint.py --name ${LINUX_BP_NAME_PHPIPAM} --force
	calm compile bp -f ./blueprints_ams_phpipam/blueprints_ams/windows/windows_ams_blueprint.py
	calm create bp -f ./blueprints_ams_phpipam/blueprints_ams/windows/windows_ams_blueprint.py --name ${WINDOWS_BP_NAME_PHPIPAM} --force

create-ams-infoblox_bps:
	make cookiecutter-ams-infoblox_bps
	make init-dsl-config CALM_ENVIRONMENT=calm-ams
	calm compile bp -f ./blueprints_ams_infoblox/blueprints_ams/linux/linux_ams_blueprint.py
	calm create bp -f ./blueprints_ams_infoblox/blueprints_ams/linux/linux_ams_blueprint.py --name ${LINUX_BP_NAME_INFOBLOX} --force
	calm compile bp -f ./blueprints_ams_infoblox/blueprints_ams/windows/windows_ams_blueprint.py
	calm create bp -f ./blueprints_ams_infoblox/blueprints_ams/windows/windows_ams_blueprint.py --name ${WINDOWS_BP_NAME_INFOBLOX} --force

create-ams-solarwinds_bps:
	make cookiecutter-ams-solarwinds_bps
	make init-dsl-config CALM_ENVIRONMENT=calm-ams
	calm compile bp -f ./blueprints_ams_solarwinds/blueprints_ams/linux/linux_ams_blueprint.py
	calm create bp -f ./blueprints_ams_solarwinds/blueprints_ams/linux/linux_ams_blueprint.py --name ${LINUX_BP_NAME_SOLARWINDS} --force
	calm compile bp -f ./blueprints_ams_solarwinds/blueprints_ams/windows/windows_ams_blueprint.py
	calm create bp -f ./blueprints_ams_solarwinds/blueprints_ams/windows/windows_ams_blueprint.py --name ${WINDOWS_BP_NAME_SOLARWINDS} --force


NAME    := nutanixservices/cita-starter

blueprints:
	if [ ! -d "./blueprints" ]; then cookiecutter ./ --no-input -v; fi
	#source ${CALMDSL}/venv/bin/activate
	calm create bp --file ./blueprints/linux/blueprint_f1_dhcp.py --name cita-starter-linux-f1-dhcp
	calm create bp --file ./blueprints/linux/blueprint_f2_static.py --name cita-starter-linux-f2-static
	calm create bp --file ./blueprints/linux/blueprint_f3_phpipam.py --name cita-starter-linux-f3-phpipam
	calm create bp --file ./blueprints/linux/blueprint_f4_infoblox.py --name cita-starter-linux-f4-infoblox
	calm create bp --file ./blueprints/linux/blueprint_f5_solarwinds.py --name cita-starter-linux-f5-solarwinds
	calm create bp --file ./blueprints/windows/blueprint_f1_dhcp.py --name cita-starter-windows-f1-dhcp
	calm create bp --file ./blueprints/windows/blueprint_f2_static.py --name cita-starter-windows-f2-static
	calm create bp --file ./blueprints/windows/blueprint_f3_phpipam.py --name cita-starter-windows-f3-phpipam
	calm create bp --file ./blueprints/windows/blueprint_f4_infoblox.py --name cita-starter-windows-f4-infoblox
	calm create bp --file ./blueprints/windows/blueprint_f5_solarwinds.py --name cita-starter-windows-f5-solarwinds
