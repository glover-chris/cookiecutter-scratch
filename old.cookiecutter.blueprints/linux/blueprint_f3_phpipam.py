import json  # no_qa
import os  # no_qa

from calm.dsl.builtins import *  # no_qa

#region credentials
# Secret Variables
BP_CRED_linux_KEY = read_local_file("BP_CRED_linux_KEY")
BP_CRED_root_PASSWORD = read_local_file("BP_CRED_root_PASSWORD")
BP_CRED_prism_central_PASSWORD = read_local_file("BP_CRED_prism_central_PASSWORD")
BP_CRED_phpipam_PASSWORD = read_local_file("BP_CRED_phpipam_PASSWORD")

#!CUSTOMIZE usernames in credentials below
# Credentials
BP_CRED_linux = basic_cred(
    "{{cookiecutter.linux_username}}",
    BP_CRED_linux_KEY,
    name="linux",
    type="KEY",
    default=True,
    editables={"username": True, "secret": True},
)
BP_CRED_root = basic_cred(
    "root",
    BP_CRED_root_PASSWORD,
    name="root",
    type="PASSWORD",
)
BP_CRED_prism_central = basic_cred(
    "{{cookiecutter.prism_central_username}}",
    BP_CRED_prism_central_PASSWORD,
    name="prism_central",
    type="PASSWORD",
)
BP_CRED_phpipam = basic_cred(
    "{{cookiecutter.phpipam_username}}",
    BP_CRED_phpipam_PASSWORD,
    name="phpipam",
    type="PASSWORD",
)
#endregion

shared_scripts_path= "../../tasklib/scripts/"
#set check login delay
delay="180"


class Linux(Service):

    @action
    def __create__():
        """System action for creating an application"""
        CalmTask.Exec.ssh(#eject cdroms
            name="EjectCdrom",
            filename=shared_scripts_path + "linux/Centos7EjectCdrom.sh",
            cred=ref(BP_CRED_linux),
            target=ref(Linux),
        )
        CalmTask.Exec.ssh(#update root password
            name="UpdateRoot",
            filename=shared_scripts_path + "linux/Centos7UpdateRoot.sh",
            cred=ref(BP_CRED_linux),
            target=ref(Linux),
        )
        CalmTask.Exec.ssh(#send mail notification
            name="SendMail",
            filename=shared_scripts_path + "linux/Centos7SendMail.sh",
            cred=ref(BP_CRED_linux),
            target=ref(Linux),
        )

    @action
    def __delete__():
        """System action for deleting an application. Deletes created VMs as well"""

    @action
    def __restart__():
        """System action for restarting an application"""

        CalmTask.Exec.ssh(
            name="Restart",
            filename=shared_scripts_path + "linux/Centos7Restart.sh",
            cred=ref(BP_CRED_linux),
            target=ref(Linux),
        )


class profile_variables(Profile):

    vm_name = CalmVariable.Simple(
        "{{cookiecutter.vm_name}}",
        label="Hostname",
        regex="^\s*(?:\S\s*){3,15}$",
        validate_regex=True,
        is_mandatory=True,
        is_hidden=False,
        runtime=True,
        description="Enter the hostname to give to this Linux virtual machine (max 15 characters). This will also be the VM name in the hypervisor.",
    )

    domain = CalmVariable.Simple(
        "{{cookiecutter.domain}}",
        label="DNS domain name (fqdn)",
        is_mandatory=True,
        is_hidden=False,
        runtime=True,
        description="Fully qualified DNS domain name.",
    )

    email_sender = CalmVariable.Simple(
        "{{cookiecutter.email_sender}}",
        label="",
        regex=" ",
        validate_regex=False,
        is_mandatory=False,
        is_hidden=True,
        runtime=False,
        description="",
    )

    vm_requester_name = CalmVariable.Simple(
        "{{cookiecutter.vm_requester_name}}",
        label="Your full name",
        is_mandatory=True,
        is_hidden=False,
        runtime=True,
        description="This is used in the email notification and will also be part of the application instance definition for future references.",
    )

    requester_email = CalmVariable.Simple(
        "{{cookiecutter.requester_email}}",
        label="Your email address",
        is_mandatory=True,
        is_hidden=False,
        runtime=True,
        description="This will be used to send you a notification with the provisioned VM details, including credentials.",
    )

    smtp_server = CalmVariable.Simple(
        "{{cookiecutter.smtp_server}}",
        label="",
        is_mandatory=False,
        is_hidden=True,
        runtime=False,
        description="",
    )

    prism_central_ip = CalmVariable.Simple(
        "{{cookiecutter.prism_central_ip}}",
        label="",
        regex="^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
        validate_regex=True,
        is_mandatory=False,
        is_hidden=True,
        runtime=False,
        description="",
    )

    org = CalmVariable.Simple(
        "{{cookiecutter.org}}",
        label="",
        is_mandatory=False,
        is_hidden=False,
        runtime=False,
        description="",
    )

    public_key = CalmVariable.Simple(
        "{{cookiecutter.public_key}}",
        label="",
        is_mandatory=True,
        is_hidden=False,
        runtime=True,
        description="Paste here your SSL public key",
    )

    phpipam_ip = CalmVariable.Simple(
        "{{cookiecutter.phpipam_ip}}",
        label="",
        is_mandatory=False,
        is_hidden=True,
        runtime=False,
        description="IP address or FQDN for your phpIPAM server.",
    )

    phpipam_app_id = CalmVariable.Simple(
        "{{cookiecutter.phpipam_app_id}}",
        label="",
        is_mandatory=False,
        is_hidden=True,
        runtime=False,
        description="Name of the API application created in phpIPAM.",
    )

    phpipam_section_id = CalmVariable.Simple(
        "{{cookiecutter.phpipam_section_id}}",
        label="",
        is_mandatory=False,
        is_hidden=True,
        runtime=False,
        description='This is the section id in phpipam where the vlan/subnet exists (1 matches "Customers" by default; you can check the section id by navigating to your subnet in phpIPAM and looking at the url)',
    )

    vlan_id = CalmVariable.Simple(
        "{{cookiecutter.vlan_id}}",
        label="",
        is_mandatory=True,
        is_hidden=False,
        runtime=True,
        description="Id of the VLAN from which to get an IP in phpIPAM.",
    )


class ipam_actions(Substrate):
    @action
    def __pre_create__():

        CalmTask.SetVariable.escript(#PhpIPAMGetSubnetId
            name="PhpIPAMGetSubnetId",
            filename=shared_scripts_path + "phpipam/PhpIPAMGetSubnetId.py",
            variables=["phpipam_subnet_id"],
        )
        CalmTask.SetVariable.escript(#PhpIPAMGetSubnet
            name="PhpIPAMGetSubnet",
            filename=shared_scripts_path + "phpipam/PhpIPAMGetSubnet.py",
            variables=[
                "subnet_mask_bits",
                "subnet_mask",
                "gateway",
                "dns1",
                "dns2",
            ],
        )
        CalmTask.SetVariable.escript(#PhpIPAMGetFreeIp
            name="PhpIPAMGetFreeIp",
            filename=shared_scripts_path + "phpipam/PhpIPAMGetFreeIp.py",
            variables=["vm_ip"],
        )

    @action
    def __post_delete__():

        CalmTask.Exec.escript(
            name="PhpIPAMReleaseIp",
            filename=shared_scripts_path + "phpipam/PhpIPAMReleaseIp.py",
        )


#region AHV
#!CUSTOMIZE VM defaults, image name, network and AHV cluster below
class vm_nameResources(AhvVmResources):

    memory = 2
    vCPUs = 1
    cores_per_vCPU = 2
    disks = [
        AhvVmDisk.Disk.Scsi.cloneFromImageService("pracdev-cita-calm-centos-7", bootable=True),
        AhvVmDisk.CdRom.Ide.emptyCdRom(),
        AhvVmDisk.Disk.Scsi.allocateOnStorageContainer(50),
    ]
    nics = [AhvVmNic.NormalNic.ingress("VLAN568", cluster="GROOT")]

    guest_customization = AhvVmGC.CloudInit(
        filename=os.path.join("specs", "vm_name_cloud_init_data_f3_phpipam.yaml")
    )


class vm_name(AhvVm):

    name = "@@{vm_name}@@"
    resources = vm_nameResources


class AHVVM(ipam_actions):

    os_type = "Linux"
    provider_type = "AHV_VM"
    provider_spec = vm_name
    provider_spec_editables = read_spec(
        os.path.join("specs", "AHVVM_create_spec_editables.yaml")
    )
    readiness_probe = readiness_probe(
        connection_type="SSH",
        disabled=False,
        retries="5",
        connection_port=22,
        address="@@{platform.status.resources.nic_list[0].ip_endpoint_list[0].ip}@@",
        delay_secs=delay,
        credential=ref(BP_CRED_linux),
    )


class AHV_Package(Package):

    services = [ref(Linux)]

    @action
    def __install__():

        CalmTask.Exec.ssh(#disable selinux
            name="DisableSelinux",
            filename=shared_scripts_path + "linux/Centos7DisableSelinux.sh",
            cred=ref(BP_CRED_linux),
            target=ref(Linux),
        )
        CalmTask.Exec.ssh(#InitializeDataDisk
            name="InitializeDataDisk",
            filename=shared_scripts_path + "linux/Centos7InitializeDataDisk.sh",
            cred=ref(BP_CRED_linux),
            target=ref(Linux),
        )
        CalmTask.Exec.ssh(#ApplyLinuxUpdates
            name="ApplyLinuxUpdates",
            filename=shared_scripts_path + "linux/Centos7ApplyLinuxUpdates.sh",
            cred=ref(BP_CRED_linux),
            target=ref(Linux),
        )
        CalmTask.Exec.escript(#PcMountNgt
            name="PcMountNgt",
            filename=shared_scripts_path + "prism/PcMountNgt.py",
            target=ref(Linux),
        )
        CalmTask.Delay(name="Wait20", delay_seconds=20, target=ref(Linux))
        CalmTask.Exec.ssh(#InstallNgt
            name="InstallNgt",
            filename=shared_scripts_path + "linux/Centos7InstallNgt.sh",
            cred=ref(BP_CRED_linux),
            target=ref(Linux),
        )
        CalmTask.Exec.escript(#PcEnableNewNgt
            name="PcEnableNewNgt",
            filename=shared_scripts_path + "prism/PcEnableNewNgt.py",
            target=ref(Linux),
        )


class ahv_vm_deployment(Deployment):
    
    name = "ahv_vm_deployment"
    min_replicas = "1"
    max_replicas = "1"
    default_replicas = "1"

    packages = [ref(AHV_Package)]
    substrate = ref(AHVVM)


#!CUSTOMIZE application profile variables default values below
class AHV(profile_variables):

    deployments = [ahv_vm_deployment]

#endregion

#region vSphere
class vSphereVM(ipam_actions):

    os_type = "Linux"
    provider_type = "VMWARE_VM"
    provider_spec = read_vmw_spec(os.path.join("specs", "vSphereVM_provider_spec_f3_phpipam.yaml"))
    provider_spec_editables = read_spec(
        os.path.join("specs", "vSphereVM_create_spec_editables.yaml")
    )
    readiness_probe = readiness_probe(
        connection_type="SSH",
        disabled=False,
        retries="5",
        connection_port=22,
        address="@@{platform.ipAddressList[0]}@@",
        delay_secs=delay,
        credential=ref(BP_CRED_linux),
    )


class vSphere_Package(Package):

    services = [ref(Linux)]

    @action
    def __install__():

        CalmTask.Exec.ssh(#disable selinux
            name="DisableSelinux",
            filename=shared_scripts_path + "linux/Centos7DisableSelinux.sh",
            cred=ref(BP_CRED_linux),
            target=ref(Linux),
        )
        CalmTask.Exec.ssh(#InitializeDataDisk
            name="InitializeDataDisk",
            filename=shared_scripts_path + "linux/Centos7InitializeDataDisk.sh",
            cred=ref(BP_CRED_linux),
            target=ref(Linux),
        )
        CalmTask.Exec.ssh(#ApplyLinuxUpdates
            name="ApplyLinuxUpdates",
            filename=shared_scripts_path + "linux/Centos7ApplyLinuxUpdates.sh",
            cred=ref(BP_CRED_linux),
            target=ref(Linux),
        )


class esxi_vm_deployment(Deployment):

    name = "esxi_vm_deployment"
    min_replicas = "1"
    max_replicas = "1"
    default_replicas = "1"

    packages = [ref(vSphere_Package)]
    substrate = ref(vSphereVM)


#!CUSTOMIZE application profile variables default values below
class vSphere(profile_variables):

    deployments = [esxi_vm_deployment]

#endregion


class pracdevcitastarterlinux(Blueprint):
    """Centos 7 Blueprint that assumes static IPv4 configuration provided by the user, ejects CDROM, runs yum update, disables SELinux and initializes data disk. Sends out an email notification on successful creation of VM."""

    services = [Linux]
    packages = [AHV_Package, vSphere_Package]
    substrates = [AHVVM, vSphereVM]
    profiles = [AHV, vSphere]
    credentials = [
        BP_CRED_linux,
        BP_CRED_root,
        BP_CRED_prism_central,
        BP_CRED_phpipam,
    ]
