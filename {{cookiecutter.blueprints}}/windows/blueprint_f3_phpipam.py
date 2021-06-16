import json  # no_qa
import os  # no_qa

from calm.dsl.builtins import *  # no_qa

#region credentials
# Secret Variables
BP_CRED_windows_PASSWORD = read_local_file("BP_CRED_guest_os_PASSWORD")
BP_CRED_active_directory_PASSWORD = read_local_file("BP_CRED_active_directory_PASSWORD")
BP_CRED_prism_central_PASSWORD = read_local_file("BP_CRED_prism_central_PASSWORD")
BP_CRED_phpipam_PASSWORD = read_local_file("BP_CRED_phpipam_PASSWORD")

#!CUSTOMIZE usernames in credentials below
# Credentials
BP_CRED_windows = basic_cred(
    "{{cookiecutter.windows_username}}",
    BP_CRED_windows_PASSWORD,
    name="windows",
    type="PASSWORD",
    default=True,
    editables={"username": False, "secret": True},
)
BP_CRED_active_directory = basic_cred(
    "{{cookiecutter.active_directory_username}}",
    BP_CRED_active_directory_PASSWORD,
    name="active_directory",
    type="PASSWORD",
)
BP_CRED_prism_central = basic_cred(
    "{{cookiecutter.prism_central_username}}",
    BP_CRED_prism_central_PASSWORD,
    name="prism_central",
    type="PASSWORD",
)
BP_CRED_phpipam = basic_cred(
    "sbourdeaud",
    BP_CRED_phpipam_PASSWORD,
    name="phpipam",
    type="PASSWORD",
)
#endregion

shared_scripts_path= "../../tasklib/scripts/"
#set check login delay
delay="300"


class Windows(Service):

    @action
    def __create__():
        """System action for creating an application"""

        CalmTask.Exec.powershell(#JoinDomain
            name="JoinDomain",
            filename=shared_scripts_path + "windows/WindowsJoinDomain.ps1",
            cred=ref(BP_CRED_windows),
            target=ref(Windows),
        )
        Windows.__restart__(name="Restart")
        CalmTask.Delay(name="Wait30", delay_seconds=30, target=ref(Windows))
        with parallel():
            CalmTask.Exec.powershell(#PerfOpt
                name="PerfOpt",
                filename=shared_scripts_path + "windows/WindowsPerfOpt.ps1",
                cred=ref(BP_CRED_windows),
                target=ref(Windows),
            )
            CalmTask.Exec.powershell(#InitDataDisk
                name="InitDataDisk",
                filename=shared_scripts_path + "windows/WindowsInitDataDisk.ps1",
                cred=ref(BP_CRED_windows),
                target=ref(Windows),
            )
        CalmTask.Exec.powershell(#EjectCdrom
            name="EjectCdrom",
            filename=shared_scripts_path + "windows/WindowsEjectCdrom.ps1",
            cred=ref(BP_CRED_windows),
            target=ref(Windows),
        )
        CalmTask.Exec.powershell(#DisableAutoLogon
            name="DisableAutoLogon",
            filename=shared_scripts_path + "windows/WindowsDisableAutoLogon.ps1",
            cred=ref(BP_CRED_windows),
            target=ref(Windows),
        )
        CalmTask.Exec.powershell(#InstallDscModules
            name="InstallDscModules",
            filename=shared_scripts_path + "windows/WindowsInstallDscModules.ps1",
            cred=ref(BP_CRED_windows),
            target=ref(Windows),
        )
        Windows.Update(name="UpdateWindows")
        CalmTask.Exec.powershell(#SendMail
            name="SendMail",
            filename=shared_scripts_path + "windows/WindowsSendMail.ps1",
            cred=ref(BP_CRED_windows),
            target=ref(Windows),
        )

    @action
    def __delete__():
        """System action for deleting an application. Deletes created VMs as well"""

        CalmTask.Exec.powershell(#DomainUnjoin
            name="DomainUnjoin",
            filename=shared_scripts_path + "windows/WindowsDomainUnjoin.ps1",
            cred=ref(BP_CRED_windows),
            target=ref(Windows),
        )

    @action
    def __restart__():
        """System action for restarting an application"""

        CalmTask.Exec.powershell(#Restart
            name="Restart",
            filename=shared_scripts_path + "windows/WindowsRestart.ps1",
            cred=ref(BP_CRED_windows),
            target=ref(Windows),
        )

    @action
    def Update():
        """System action for applying Windows updates"""

        CalmTask.Exec.powershell(#ApplyWindowsUpdates
            name="ApplyWindowsUpdates",
            filename=shared_scripts_path + "windows/WindowsApplyWindowsUpdates.ps1",
            cred=ref(BP_CRED_windows),
            target=ref(Windows),
        )
        Windows.__restart__(name="Restart")
        CalmTask.Delay(name="Wait30", delay_seconds=30, target=ref(Windows))


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

    locale = CalmVariable.WithOptions(
        ["en-US", "en-GB", "fr-FR"],
        label="Locale",
        default="en-US",
        is_mandatory=True,
        is_hidden=False,
        runtime=True,
        description="Select the locale to apply to Windows which will determine the language and keyboard layout.",
    )

    timezone = CalmVariable.WithOptions(
        ["UTC", "Europe/Paris"],
        label="TimeZone",
        default="UTC",
        is_mandatory=True,
        is_hidden=False,
        runtime=True,
        description="Select the timezone to apply in Windows.",
    )

    org = CalmVariable.Simple(
        "{{cookiecutter.org}}",
        label="",
        is_mandatory=False,
        is_hidden=False,
        runtime=False,
        description="",
    )

    product_key = CalmVariable.Simple(
        "{{cookiecutter.product_key}}",
        label="",
        is_mandatory=False,
        is_hidden=True,
        runtime=False,
        description="",
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

    memory = {{cookiecutter.vm_memory_gb}}
    vCPUs = {{cookiecutter.vm_vcpus}}
    cores_per_vCPU = {{cookiecutter.vm_vcpus_core}}
    disks = [
        AhvVmDisk.Disk.Scsi.cloneFromImageService("{{cookiecutter.ahv_windows_image_name}}", bootable=True),
        AhvVmDisk.CdRom.Ide.emptyCdRom(),
        AhvVmDisk.Disk.Scsi.allocateOnStorageContainer(50),
    ]
    nics = [AhvVmNic.NormalNic.ingress("{{cookiecutter.ahv_network_name}}", cluster="{{cookiecutter.ahv_cluster_name}}")]

    guest_customization = AhvVmGC.Sysprep.PreparedScript.withoutDomain(
        filename=os.path.join("specs", "vm_name_sysprep_unattend_xml_f3_phpipam.xml")
    )


class vm_name(AhvVm):

    name = "@@{vm_name}@@"
    resources = vm_nameResources


class AHVVM(ipam_actions):

    os_type = "Windows"
    provider_type = "AHV_VM"
    provider_spec = vm_name
    provider_spec_editables = read_spec(
        os.path.join("specs", "AHVVM_create_spec_editables.yaml")
    )
    readiness_probe = readiness_probe(
        connection_type="POWERSHELL",
        disabled=False,
        retries="5",
        connection_port=5985,
        address="@@{platform.status.resources.nic_list[0].ip_endpoint_list[0].ip}@@",
        delay_secs=delay,
        credential=ref(BP_CRED_windows),
    )

    
class AHV_Package(Package):

    services = [ref(Windows)]

    @action
    def __install__():

        CalmTask.Exec.escript(
            name="PcMountNgt",
            filename=shared_scripts_path + "prism/PcMountNgt.py",
            target=ref(Windows),
        )
        CalmTask.Delay(name="Wait20", delay_seconds=20, target=ref(Windows))
        CalmTask.Exec.powershell(
            name="InstallNgt",
            filename=shared_scripts_path + "windows/WindowsInstallNgt.ps1",
            cred=ref(BP_CRED_windows),
            target=ref(Windows),
        )
        CalmTask.Exec.escript(
            name="PcEnableNewNgt",
            filename=shared_scripts_path + "prism/PcEnableNewNgt.py",
            target=ref(Windows),
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

    os_type = "Windows"
    provider_type = "VMWARE_VM"
    provider_spec = read_vmw_spec(os.path.join("specs", "vSphereVM_provider_spec_f3_phpipam.yaml"))
    provider_spec_editables = read_spec(
        os.path.join("specs", "vSphereVM_create_spec_editables.yaml")
    )
    readiness_probe = readiness_probe(
        connection_type="POWERSHELL",
        disabled=False,
        retries="5",
        connection_port=5985,
        address="@@{platform.ipAddressList[0]}@@",
        delay_secs=delay,
        credential=ref(BP_CRED_windows),
    )


class vSphere_Package(Package):

    services = [ref(Windows)]


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


class pracdevcitastarterwindows(Blueprint):
    """Windows 2019 Blueprint that requests IPv4 from the user, joins domain, has performance optimization and ejects CDROM. Runs Windows Update and initializes data disk. Sends out an email notification on successful creation of VM."""

    services = [Windows]
    packages = [AHV_Package, vSphere_Package]
    substrates = [AHVVM, vSphereVM]
    profiles = [AHV, vSphere]
    credentials = [
        BP_CRED_windows,
        BP_CRED_active_directory,
        BP_CRED_prism_central,
        BP_CRED_phpipam,
    ]
