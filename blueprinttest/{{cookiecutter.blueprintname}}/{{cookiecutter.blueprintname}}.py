import json  # no_qa
import os  # no_qa

from calm.dsl.builtins import *  # no_qa
{% if cookiecutter.use_solarwinds == 'yes' -%}
from calm.dsl.runbooks import CalmEndpoint as Endpoint

SOLARWINDS_ENDPOINT="solarwinds"
{%- endif %}

#region credentials
# Secret Variables
BP_CRED_windows_PASSWORD = read_local_file("BP_CRED_guest_os_PASSWORD")
BP_CRED_active_directory_PASSWORD = read_local_file("BP_CRED_active_directory_PASSWORD")
BP_CRED_prism_central_PASSWORD = read_local_file("BP_CRED_prism_central_PASSWORD")
{% if cookiecutter.use_phpipam == 'yes' -%}
BP_CRED_phpipam_PASSWORD = read_local_file("BP_CRED_phpipam_PASSWORD")
{% elif cookiecutter.use_infoblox == 'yes' -%}
BP_CRED_infoblox_PASSWORD = read_local_file("BP_CRED_infoblox_PASSWORD")
{% elif cookiecutter.use_solarwinds == 'yes' -%}
BP_CRED_solarwinds_PASSWORD = read_local_file("BP_CRED_solarwinds_PASSWORD")
{% endif %}

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
{% if cookiecutter.use_phpipam == 'yes' -%}
BP_CRED_phpipam = basic_cred(
    "sbourdeaud",
    BP_CRED_phpipam_PASSWORD,
    name="phpipam",
    type="PASSWORD",
)
{% elif cookiecutter.use_infoblox == 'yes' -%}
BP_CRED_infoblox = basic_cred(
    "calm",
    BP_CRED_infoblox_PASSWORD,
    name="infoblox",
    type="PASSWORD",
)
{% elif cookiecutter.use_solarwinds == 'yes' -%}
BP_CRED_solarwinds = basic_cred(
    "admin",
    BP_CRED_solarwinds_PASSWORD,
    name="solarwinds",
    type="PASSWORD",
)
{% endif -%}
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

    {% if cookiecutter.use_static_ip == 'yes' -%}
    vm_ip = CalmVariable.Simple(
        "{{cookiecutter.vm_ip}}",
        label="",
        regex="^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
        validate_regex=True,
        is_mandatory=True,
        is_hidden=False,
        runtime=True,
        description="Please enter the IPv4 address for this virtual machine",
    )

    gateway = CalmVariable.Simple(
        "{{cookiecutter.gateway}}",
        label="",
        regex="^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
        validate_regex=True,
        is_mandatory=True,
        is_hidden=False,
        runtime=True,
        description="Please enter the IPv4 address of the gateway",
    )

    dns1 = CalmVariable.Simple(
        "{{cookiecutter.dns1}}",
        label="",
        regex="^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
        validate_regex=True,
        is_mandatory=True,
        is_hidden=False,
        runtime=True,
        description="Please enter the IPv4 address of the primary DNS server",
    )

    dns2 = CalmVariable.Simple(
        "{{cookiecutter.dns2}}",
        label="",
        regex="^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
        validate_regex=True,
        is_mandatory=True,
        is_hidden=False,
        runtime=True,
        description="Please enter the IPv4 address of the secondary DNS server",
    )
    {% elif cookiecutter.use_phpipam == 'yes' -%}
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
    {% elif cookiecutter.use_infoblox == 'yes' -%}
    infoblox_ip = CalmVariable.Simple(
        "{{cookiecutter.infoblox_ip}}",
        label="",
        regex="^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
        validate_regex=False,
        is_mandatory=False,
        is_hidden=True,
        runtime=False,
        description="",
    )

    network = CalmVariable.WithOptions.FromTask(
        CalmTask.HTTP.get(
            "https://@@{infoblox_ip}@@/wapi/v2.7/network?_return_as_object=1",
            headers={},
            secret_headers={},
            content_type="application/json",
            verify=False,
            status_mapping={201: True, 404: False},
            response_paths={"network": "$.result.network"},
            name="",
            cred=ref(BP_CRED_infoblox),
        ),
        label="",
        regex="^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/(3[0-2]|[1-2][0-9]|[0-9]))$",
        validate_regex=True,
        is_mandatory=True,
        is_hidden=False,
        description="Infoblox network from which to get an IPv4 address. Scope options on this network will also define your subnet mask, DNS server and default gateway.",
    )
    {% elif cookiecutter.use_solarwinds == 'yes' -%}
    solarwinds_ip = CalmVariable.Simple(
        "{{cookiecutter.solarwinds_ip}}",
        label="",
        regex="^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
        validate_regex=False,
        is_mandatory=False,
        is_hidden=True,
        runtime=False,
        description="",
    )

    network = CalmVariable.Simple(
        "{{cookiecutter.network}}",
        label="",
        regex="",
        validate_regex=False,
        is_mandatory=True,
        is_hidden=False,
        description="Solarwinds managed subnet from which to get an IPv4 address.",
    )

    def_net1 = CalmVariable.Simple(
        "{{cookiecutter.def_net1}}",
        label="",
        regex="",
        validate_regex=False,
        is_mandatory=True,
        is_hidden=True,
        description="Name of Solarwinds managed subnet 1 in cidr notation.",
    )

    def_net1_gw = CalmVariable.Simple(
        "{{cookiecutter.def_net1_gw}}",
        label="",
        regex="",
        validate_regex=False,
        is_mandatory=True,
        is_hidden=True,
        description="Gateway for Solarwinds managed subnet 1.",
    )

    def_net1_mask = CalmVariable.Simple(
        "{{cookiecutter.def_net1_mask}}",
        label="",
        regex="",
        validate_regex=False,
        is_mandatory=True,
        is_hidden=True,
        description="Subnet mask for Solarwinds managed subnet 1.",
    )

    def_net2 = CalmVariable.Simple(
        "{{cookiecutter.def_net2}}",
        label="",
        regex="",
        validate_regex=False,
        is_mandatory=False,
        is_hidden=True,
        description="Name of Solarwinds managed subnet 1 in cidr notation.",
    )

    def_net2_gw = CalmVariable.Simple(
        "{{cookiecutter.def_net2_gw}}",
        label="",
        regex="",
        validate_regex=False,
        is_mandatory=False,
        is_hidden=True,
        description="Gateway for Solarwinds managed subnet 1.",
    )

    def_net2_mask = CalmVariable.Simple(
        "{{cookiecutter.def_net2_mask}}",
        label="",
        regex="",
        validate_regex=False,
        is_mandatory=False,
        is_hidden=True,
        description="Subnet mask for Solarwinds managed subnet 1.",
    )

    dns1 = CalmVariable.Simple(
        "{{cookiecutter.dns1}}",
        label="",
        regex="^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
        validate_regex=True,
        is_mandatory=True,
        is_hidden=False,
        runtime=False,
        description="Please enter the IPv4 address of the primary DNS server",
    )

    dns2 = CalmVariable.Simple(
        "{{cookiecutter.dns2}}",
        label="",
        regex="^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
        validate_regex=True,
        is_mandatory=True,
        is_hidden=False,
        runtime=False,
        description="Please enter the IPv4 address of the secondary DNS server",
    )
    {% endif -%}

{% if cookiecutter.use_phpipam == 'yes' %}
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
{% elif cookiecutter.use_infoblox == 'yes' %}
class ipam_actions(Substrate):
    @action
    def __pre_create__():

        CalmTask.SetVariable.escript(#InfobloxReserveIp
            name="InfobloxReserveIp",
            filename=shared_scripts_path + "infoblox/InfobloxReserveIp.py",
            variables=["ip_ref","vm_ip"],
        )
        CalmTask.SetVariable.escript(#InfobloxSetMask
            name="InfobloxSetMask",
            filename=shared_scripts_path + "infoblox/InfobloxSetMask.py",
            variables=["subnet_mask", "subnet_mask_bits"],
        )
        CalmTask.SetVariable.escript(#InfobloxGetOptions
            name="InfobloxGetOptions",
            filename=shared_scripts_path + "infoblox/InfobloxGetOptions.py",
            variables=["dns1", "dns2", "gateway"],
        )

    @action
    def __post_delete__():

        CalmTask.Exec.escript(#InfobloxReleaseIp
            name="InfobloxReleaseIp",
            filename=shared_scripts_path + "infoblox/InfobloxReleaseIp.py",
        )
{% elif cookiecutter.use_solarwinds == 'yes' %}
class ipam_actions(Substrate):
    @action
    def __pre_create__():

        CalmTask.SetVariable.powershell(#SolarwindsGetIp
            name="SolarWindsGetIp",
            filename=shared_scripts_path + "solarwinds/SolarWindsGetIp.ps1",
            target_endpoint=Endpoint.use_existing(SOLARWINDS_ENDPOINT),
            variables=["vm_ip","subnet_mask","subnet_mask_bits","gateway","cidr"],
        )

    @action
    def __post_delete__():

        CalmTask.Exec.powershell(#solarwindsRemoveIp
            name="SolarWindsRemoveIp",
            filename=shared_scripts_path + "solarwinds/SolarWindsRemoveIp.ps1",
            target_endpoint=Endpoint.use_existing(SOLARWINDS_ENDPOINT),
        )
{% endif %}

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
        {% if cookiecutter.use_static_ip == 'yes' -%}
        filename=os.path.join("specs", "vm_name_sysprep_unattend_xml_f2_static.xml")
        {% elif cookiecutter.use_phpipam == 'yes' -%}
        filename=os.path.join("specs", "vm_name_sysprep_unattend_xml_f3_phpipam.xml")
        {% elif cookiecutter.use_infoblox == 'yes' -%}
        filename=os.path.join("specs", "vm_name_sysprep_unattend_xml_f4_infoblox.xml")
        {% elif cookiecutter.use_solarwinds == 'yes' -%}
        filename=os.path.join("specs", "vm_name_sysprep_unattend_xml_f5_solarwinds.xml")
        {% else %}
        filename=os.path.join("specs", "vm_name_sysprep_unattend_xml_f1_dhcp.xml")
        {% endif -%}
    )


class vm_name(AhvVm):

    name = "@@{vm_name}@@"
    resources = vm_nameResources


class AHVVM({% if cookiecutter.use_phpipam == 'yes' or cookiecutter.use_infoblox == 'yes'or cookiecutter.use_solarwinds == 'yes' -%}ipam_actions{% else %}Substrate{% endif -%}):

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

    {%- if cookiecutter.use_static_ip == 'yes' -%}
    subnet_mask_bits = CalmVariable.Simple(
        "24",
        label="",
        regex="",
        validate_regex=False,
        is_mandatory=True,
        is_hidden=False,
        runtime=True,
        description="Please enter the IPv4 subnet mask for this virtual machine (in bits format; for exp: 24)",
    )
    {%- endif %}

#endregion

#region vSphere
class vSphereVM({% if cookiecutter.use_phpipam == 'yes' or cookiecutter.use_infoblox == 'yes' or cookiecutter.use_solarwinds == 'yes' -%}ipam_actions{% else %}Substrate{% endif -%}):

    os_type = "Windows"
    provider_type = "VMWARE_VM"
    {% if cookiecutter.use_static_ip == 'yes' -%}
    provider_spec = read_vmw_spec(os.path.join("specs", "vSphereVM_provider_spec_f2_static.yaml"))
    {% elif cookiecutter.use_phpipam == 'yes' -%}
    provider_spec = read_vmw_spec(os.path.join("specs", "vSphereVM_provider_spec_f3_phpipam.yaml"))
    {% elif cookiecutter.use_infoblox == 'yes' -%}
    provider_spec = read_vmw_spec(os.path.join("specs", "vSphereVM_provider_spec_f4_infoblox.yaml"))
    {% elif cookiecutter.use_solarwinds == 'yes' -%}
    provider_spec = read_vmw_spec(os.path.join("specs", "vSphereVM_provider_spec_f5_solarwinds.yaml"))
    {% else %}
    provider_spec = read_vmw_spec(os.path.join("specs", "vSphereVM_provider_spec_f1_dhcp.yaml"))
    {% endif -%}
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

    {%- if cookiecutter.use_static_ip == 'yes' -%}
    subnet_mask = CalmVariable.Simple(
        "255.255.252.0",
        label="",
        regex="^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
        validate_regex=True,
        is_mandatory=True,
        is_hidden=False,
        runtime=True,
        description="Please enter the IPv4 subnet mask for this virtual machine",
    )
    {%- endif %}

#endregion


class pracdevcitastarterwindows(Blueprint):
    {% if cookiecutter.use_static_ip == 'yes' or cookiecutter.use_phpipam == 'yes' or cookiecutter.use_infoblox == 'yes' or cookiecutter.use_solarwinds == 'yes' -%}
    """Windows 2019 Blueprint that requests IPv4 from the user, joins domain, has performance optimization and ejects CDROM. Runs Windows Update and initializes data disk. Sends out an email notification on successful creation of VM."""
    {% else %}
    """Windows 2019 Blueprint that assumes DHCP configuration, joins domain, has performance optimization and ejects CDROM. Runs Windows Update and initializes data disk. Sends out an email notification on successful creation of VM."""
    {% endif -%}
    services = [Windows]
    packages = [AHV_Package, vSphere_Package]
    substrates = [AHVVM, vSphereVM]
    profiles = [AHV, vSphere]
    credentials = [
        BP_CRED_windows,
        BP_CRED_active_directory,
        BP_CRED_prism_central,
        {% if cookiecutter.use_phpipam == 'yes' -%}
        BP_CRED_phpipam,
        {% elif cookiecutter.use_infoblox == 'yes' -%}
        BP_CRED_infoblox,
        {% elif cookiecutter.use_solarwinds == 'yes' -%}
        BP_CRED_solarwinds,
        {% endif -%}
    ]
