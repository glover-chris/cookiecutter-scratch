#####
## This script will populate the .local creds and underlying environment configs for target cluster

SSH_PRIVATE_KEY_PATH=$1

LINUX_LOCAL_ADMIN_USER="root"
LINUX_LOCAL_ADMIN_KEY=$SSH_PRIVATE_KEY_PATH
INFOBLOX_USER="testuser"
INFOBLOX_PASSWORD="test"
PRISM_CENTRAL_USER="admin"
PRISM_CENTRAL_PASS="nutanix/4u"
WINDOWS_DOMAIN_ADMIN="Administrator@ntnxlab.local"
WINDOWS_DOMAIN_PASS="nutanix/4u"

ARGS_LIST=($@)

if [ ${#ARGS_LIST[@]} -lt 1 ]; then
	echo 'Usage: ./dsl_init_calm_config.sh [~/.ssh/ssh-private-key]'
	echo 'Example: ./dsl_init_calm_config.sh ~/.ssh/nutanix'
	exit
fi

#if [ ! -d .local/$CALM_ENVIRONMENT ]; then
#	mkdir .local/$CALM_ENVIRONMENT
#fi

echo "Initialize Local Configs"
touch ~/.calm/.local/dsl.db
touch ~/.calm/.local/config.ini

echo "Updating Local Secrets"
echo $LINUX_LOCAL_ADMIN_USER >| ~/.calm/.local/linux_local_admin_user
echo $LINUX_LOCAL_ADMIN_KEY >| ~/.calm/.local/linux_local_admin_key
echo $INFOBLOX_USER >| ~/.calm/.local/infoblox_user
echo $INFOBLOX_PASSWORD >| ~/.calm/.local/infoblox_password
echo $PRISM_CENTRAL_USER >| ~/.calm/.local/prism_central_user
echo $PRISM_CENTRAL_PASS >| ~/.calm/.local/prism_central_password
echo $WINDOWS_DOMAIN_ADMIN >| ~/.calm/.local/active_directory_user
echo $WINDOWS_DOMAIN_PASS >| ~/.calm/.local/active_directory_password

#echo "Updating Environment Configs"
#[ -d configs/${CALM_ENVIRONMENT} ] || cp -R configs/templates/kalm-{env}-{hpoc_id} configs/${CALM_ENVIRONMENT}
