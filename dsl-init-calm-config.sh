#####
## This script will populate the ./local creds for target PHX (Phoenix) GSO.LAB and AMS (Amsterdam) GSOEMEA.LAB Calm/Prism Central instances.
## CALM_DSL User and PASSWORDS refer to the prism central credentials needed to perform the desired tasks in Calm through DSL.

CALM_DSL_PHX_USER_INPUT=$1
CALM_DSL_PHX_PASS_INPUT=$2
CALM_DSL_AMS_USER_INPUT=$3
CALM_DSL_AMS_PASS_INPUT=$4

CALM_DSL_PHX_USER=$CALM_DSL_PHX_USER_INPUT
CALM_DSL_PHX_PASS=$CALM_DSL_PHX_PASS_INPUT
CALM_DSL_AMS_USER=$CALM_DSL_AMS_USER_INPUT
CALM_DSL_AMS_PASS=$CALM_DSL_AMS_PASS_INPUT

BP_CRED_linux_KEY="test"
BP_CRED_root_PASSWORD="test"
BP_CRED_prism_central_PASSWORD="test"
BP_CRED_windows_PASSWORD="test"
BP_CRED_active_directory_PASSWORD="test"
BP_CRED_phpipam_PASSWORD="test"
BP_CRED_infoblox_PASSWORD="test"
BP_CRED_solarwinds_PASSWORD="test"

ARGS_LIST=($@)

if [ ${#ARGS_LIST[@]} -lt 4 ]; then
	echo 'Usage: ./dsl_init_calm_config.sh [CALM-DSL-PHX-USERNAME] [CALM-DSL-PHX-PASSWORD] [CALM-DSL-AMS-USERNAME] [CALM-DSL-AMS-PASSWORD]'
	echo 'Example: ./dsl_init_calm_config.sh dsl.user@gso.lab dslpassword dsl.user@emeagso.lab dslpassword'
	exit
fi

if [ ! -d .local ]; then
	mkdir .local
fi

echo "Initialize Local Configs"
touch .local/dsl.db
touch .local/config.ini

echo "Updating Local Secrets"
echo $CALM_DSL_PHX_USER > .local/calm_dsl_phx_user
echo $CALM_DSL_PHX_PASS > .local/calm_dsl_phx_pass
echo $CALM_DSL_AMS_USER > .local/calm_dsl_ams_user
echo $CALM_DSL_AMS_PASS > .local/calm_dsl_ams_pass
echo $BP_CRED_linux_KEY > .local/BP_CRED_linux_KEY
echo $BP_CRED_root_PASSWORD > .local/BP_CRED_root_PASSWORD
echo $BP_CRED_prism_central_PASSWORD > .local/BP_CRED_prism_central_PASSWORD
echo $BP_CRED_windows_PASSWORD > .local/BP_CRED_windows_PASSWORD
echo $BP_CRED_active_directory_PASSWORD > .local/BP_CRED_active_directory_PASSWORD
echo $BP_CRED_phpipam_PASSWORD > .local/BP_CRED_phpipam_PASSWORD
echo $BP_CRED_infoblox_PASSWORD > .local/BP_CRED_infoblox_PASSWORD
echo $BP_CRED_solarwinds_PASSWORD > .local/BP_CRED_solarwinds_PASSWORD

#echo "Updating Environment Configs"
#[ -d configs/${CALM_ENVIRONMENT} ] || cp -R configs/templates/calm-{gsosite} configs/${CALM_ENVIRONMENT}
