# Original source:
# https://github.com/corpnewt/SSDTTime/blob/7b3fb78112bf320a1bc6a7e50dddb2b375cb70b0/SSDTTime.py

from Scripts.datasets import chipset_data
from Scripts.datasets import cpu_data
from Scripts.datasets import pci_data
from Scripts import smbios
from Scripts import dsdt
from Scripts import utils
import os
import binascii
import re
import tempfile
import shutil
import sys
import subprocess

class ACPIGuru:
    def __init__(self):
        self.acpi = dsdt.DSDT()
        self.smbios = smbios.SMBIOS()
        self.utils = utils.Utils()
        self.dsdt = None
        self.lpc_bus_device = None
        self.osi_strings = {
            "Windows 2000": "Windows 2000",
            "Windows XP": "Windows 2001",
            "Windows XP SP1": "Windows 2001 SP1",
            "Windows Server 2003": "Windows 2001.1",
            "Windows XP SP2": "Windows 2001 SP2",
            "Windows Server 2003 SP1": "Windows 2001.1 SP1",
            "Windows Vista": "Windows 2006",
            "Windows Vista SP1": "Windows 2006 SP1",
            "Windows Server 2008": "Windows 2006.1",
            "Windows 7, Win Server 2008 R2": "Windows 2009",
            "Windows 8, Win Server 2012": "Windows 2012",
            "Windows 8.1": "Windows 2013",
            "Windows 10": "Windows 2015",
            "Windows 10, version 1607": "Windows 2016",
            "Windows 10, version 1703": "Windows 2017",
            "Windows 10, version 1709": "Windows 2017.2",
            "Windows 10, version 1803": "Windows 2018",
            "Windows 10, version 1809": "Windows 2018.2",
            "Windows 10, version 1903": "Windows 2019",
            "Windows 10, version 2004": "Windows 2020",
            "Windows 11": "Windows 2021",
            "Windows 11, version 22H2": "Windows 2022"
        }
        self.pre_patches = (
            {
                "PrePatch":"GPP7 duplicate _PRW methods",
                "Comment" :"GPP7._PRW to XPRW to fix Gigabyte's Mistake",
                "Find"    :"3708584847500A021406535245470214065350525701085F505257",
                "Replace" :"3708584847500A0214065352454702140653505257010858505257"
            },
            {
                "PrePatch":"GPP7 duplicate UP00 devices",
                "Comment" :"GPP7.UP00 to UPXX to fix Gigabyte's Mistake",
                "Find"    :"1047052F035F53425F50434930475050375B82450455503030",
                "Replace" :"1047052F035F53425F50434930475050375B82450455505858"
            },
            {
                "PrePatch":"GPP6 duplicate _PRW methods",
                "Comment" :"GPP6._PRW to XPRW to fix ASRock's Mistake",
                "Find"    :"47505036085F4144520C04000200140F5F505257",
                "Replace" :"47505036085F4144520C04000200140F58505257"
            },
            {
                "PrePatch":"GPP1 duplicate PTXH devices",
                "Comment" :"GPP1.PTXH to XTXH to fix MSI's Mistake",
                "Find"    :"50545848085F41445200140F",
                "Replace" :"58545848085F41445200140F"
            }
        )
        self.target_irqs = [0, 2, 8, 11]
        self.illegal_names = ("XHC1", "EHC1", "EHC2", "PXSX")
        self.result = {
            "Add": [],
            "Delete": [],
            "Patch": []
        }

    def get_unique_name(self,name,target_folder,name_append="-Patched"):
        # Get a new file name in the Results folder so we don't override the original
        name = os.path.basename(name)
        ext  = "" if not "." in name else name.split(".")[-1]
        if ext: name = name[:-len(ext)-1]
        if name_append: name = name+str(name_append)
        check_name = ".".join((name,ext)) if ext else name
        if not os.path.exists(os.path.join(target_folder,check_name)):
            return check_name
        # We need a unique name
        num = 1
        while True:
            check_name = "{}-{}".format(name,num)
            if ext: check_name += "."+ext
            if not os.path.exists(os.path.join(target_folder,check_name)):
                return check_name
            num += 1 # Increment our counter

    def get_unique_device(self, path, base_name, starting_number=0, used_names = []):
        # Appends a hex number until a unique device is found
        while True:
            hex_num = hex(starting_number).replace("0x","").upper()
            name = base_name[:-1*len(hex_num)]+hex_num
            if not len(self.acpi.get_device_paths("."+name)) and not name in used_names:
                return (name,starting_number)
            starting_number += 1

    def sorted_nicely(self, l): 
        convert = lambda text: int(text) if text.isdigit() else text 
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key.lower()) ] 
        return sorted(l, key = alphanum_key)
    
    def read_dsdt(self, path):
        if not path:
            return
        tables = []
        trouble_dsdt = None
        fixed = False
        temp = None
        prior_tables = self.acpi.acpi_tables # Retain in case of failure
        # Clear any existing tables so we load anew
        self.acpi.acpi_tables = {}
        if os.path.isdir(path):
            print("Gathering valid tables from {}...\n".format(os.path.basename(path)))
            for t in self.sorted_nicely(os.listdir(path)):
                if self.acpi.table_is_valid(path,t):
                    print(" - {}".format(t))
                    tables.append(t)
            if not tables:
                # Check if there's an ACPI directory within the passed
                # directory - this may indicate SysReport was dropped
                if os.path.isdir(os.path.join(path,"ACPI")):
                    # Rerun this function with that updated path
                    return self.read_dsdt(os.path.join(path,"ACPI"))
                print(" - No valid .aml files were found!")
                print("")
                self.utils.request_input()
                # Restore any prior tables
                self.acpi.acpi_tables = prior_tables
                return
            print("")
            # We got at least one file - let's look for the DSDT specifically
            # and try to load that as-is.  If it doesn't load, we'll have to
            # manage everything with temp folders
            dsdt_list = [x for x in tables if self.acpi._table_signature(path,x) == "DSDT"]
            if len(dsdt_list) > 1:
                print("Multiple files with DSDT signature passed:")
                for d in self.sorted_nicely(dsdt_list):
                    print(" - {}".format(d))
                print("\nOnly one is allowed at a time.  Please remove one of the above and try again.")
                print("")
                self.utils.request_input()
                # Restore any prior tables
                self.acpi.acpi_tables = prior_tables
                return
            # Get the DSDT, if any
            dsdt = dsdt_list[0] if len(dsdt_list) else None
            if dsdt: # Try to load it and see if it causes problems
                print("Disassembling {} to verify if pre-patches are needed...".format(dsdt))
                if not self.acpi.load(os.path.join(path,dsdt))[0]:
                    trouble_dsdt = dsdt
                else:
                    print("\nDisassembled successfully!\n")
        elif os.path.isfile(path):
            #print("Loading {}...".format(os.path.basename(path)))
            if self.acpi.load(path)[0]:
                #print("\nDone.")
                # If it loads fine - just return the path
                # to the parent directory
                return os.path.dirname(path)
            if not self.acpi._table_signature(path) == "DSDT":
                # Not a DSDT, we aren't applying pre-patches
                print("\n{} could not be disassembled!".format(os.path.basename(path)))
                print("")
                self.utils.request_input()
                # Restore any prior tables
                self.acpi.acpi_tables = prior_tables
                return
            # It didn't load - set it as the trouble file
            trouble_dsdt = os.path.basename(path)
            # Put the table in the tables list, and adjust
            # the path to represent the parent dir
            tables.append(os.path.basename(path))
            path = os.path.dirname(path)
        else:
            print("Passed file/folder does not exist!")
            print("")
            self.utils.request_input()
            # Restore any prior tables
            self.acpi.acpi_tables = prior_tables
            return
        # If we got here - check if we have a trouble_dsdt.
        if trouble_dsdt:
            # We need to move our ACPI files to a temp folder
            # then try patching the DSDT there
            temp = tempfile.mkdtemp()
            for table in tables:
                shutil.copy(
                    os.path.join(path,table),
                    temp
                )
            # Get a reference to the new trouble file
            trouble_path = os.path.join(temp,trouble_dsdt)
            # Now we try patching it
            print("Checking available pre-patches...")
            print("Loading {} into memory...".format(trouble_dsdt))
            with open(trouble_path,"rb") as f:
                d = f.read()
            res = self.acpi.check_output(self.output)
            target_name = self.get_unique_name(trouble_dsdt,res,name_append="-Patched")
            patches = []
            print("Iterating patches...\n")
            for p in self.pre_patches:
                if not all(x in p for x in ("PrePatch","Comment","Find","Replace")): continue
                print(" - {}".format(p["PrePatch"]))
                find = binascii.unhexlify(p["Find"])
                if d.count(find) == 1:
                    self.result.get("Patch").append(p) # Retain the patch
                    repl = binascii.unhexlify(p["Replace"])
                    print(" --> Located - applying...")
                    d = d.replace(find,repl) # Replace it in memory
                    with open(trouble_path,"wb") as f:
                        f.write(d) # Write the updated file
                    # Attempt to load again
                    if self.acpi.load(trouble_path)[0]:
                        fixed = True
                        # We got it to load - let's write the patches
                        print("\nDisassembled successfully!\n")
                        #self.make_plist(None, None, patches)
                        # Save to the local file
                        with open(os.path.join(res,target_name),"wb") as f:
                            f.write(d)
                        #print("\n!! Patches applied to modified file in Results folder:\n   {}".format(target_name))
                        #self.patch_warn()
                        break
            if not fixed:
                print("\n{} could not be disassembled!".format(trouble_dsdt))
                print("")
                self.utils.request_input()
                if temp:
                    shutil.rmtree(temp,ignore_errors=True)
                # Restore any prior tables
                self.acpi.acpi_tables = prior_tables
                return
        # Let's load the rest of the tables
        if len(tables) > 1:
            print("Loading valid tables in {}...".format(path))
        loaded_tables,failed = self.acpi.load(temp or path)
        if not loaded_tables or failed:
            print("\nFailed to load tables in {}{}\n".format(
                os.path.dirname(path) if os.path.isfile(path) else path,
                ":" if failed else ""
            ))
            for t in self.sorted_nicely(failed):
                print(" - {}".format(t))
            # Restore any prior tables
            if not loaded_tables:
                self.acpi.acpi_tables = prior_tables
        else:
            if len(tables) > 1:
                print("") # Newline for readability
            print("Done.")
        # If we had to patch the DSDT, or if not all tables loaded,
        # make sure we get interaction from the user to continue
        if trouble_dsdt or not loaded_tables or failed:
            print("")
            self.utils.request_input()
        if temp:
            shutil.rmtree(temp,ignore_errors=True)
        return path

    def get_sta_var(self,var="STAS",device=None,dev_hid="ACPI000E",dev_name="AWAC",log_locate=True,table=None):
        # Helper to check for a device, check for (and qualify) an _STA method,
        # and look for a specific variable in the _STA scope
        #
        # Returns a dict with device info - only "valid" parameter is
        # guaranteed.
        has_var = False
        patches = []
        root = None
        if device:
            dev_list = self.acpi.get_device_paths(device,table=table)
            if not len(dev_list):
                #if log_locate: print(" - Could not locate {}".format(device))
                return {"value":False}
        else:
            #if log_locate: print("Locating {} ({}) devices...".format(dev_hid,dev_name))
            dev_list = self.acpi.get_device_paths_with_hid(dev_hid,table=table)
            if not len(dev_list):
                #if log_locate: print(" - Could not locate any {} devices".format(dev_hid))
                return {"valid":False}
        dev = dev_list[0]
        #if log_locate: print(" - Found {}".format(dev[0]))
        root = dev[0].split(".")[0]
        #print(" --> Verifying _STA...")
        # Check Method first - then Name
        sta_type = "MethodObj"
        sta  = self.acpi.get_method_paths(dev[0]+"._STA",table=table)
        xsta = self.acpi.get_method_paths(dev[0]+".XSTA",table=table)
        if not sta and not xsta:
            # Check for names
            sta_type = "IntObj"
            sta = self.acpi.get_name_paths(dev[0]+"._STA",table=table)
            xsta = self.acpi.get_name_paths(dev[0]+".XSTA",table=table)
        if xsta and not sta:
            #print(" --> _STA already renamed to XSTA!  Skipping other checks...")
            #print("     Please disable _STA to XSTA renames for this device, reboot, and try again.")
            #print("")
            return {"valid":False,"break":True,"device":dev,"dev_name":dev_name,"dev_hid":dev_hid,"sta_type":sta_type}
        if sta:
            if var:
                scope = "\n".join(self.acpi.get_scope(sta[0][1],strip_comments=True,table=table))
                has_var = var in scope
                #print(" --> {} {} variable".format("Has" if has_var else "Does NOT have",var))
        else:
            pass
            #print(" --> No _STA method/name found")
        # Let's find out of we need a unique patch for _STA -> XSTA
        if sta and not has_var:
            #print(" --> Generating _STA to XSTA rename")
            sta_index = self.acpi.find_next_hex(sta[0][1],table=table)[1]
            #print(" ----> Found at index {}".format(sta_index))
            sta_hex  = "5F535441" # _STA
            xsta_hex = "58535441" # XSTA
            padl,padr = self.acpi.get_shortest_unique_pad(sta_hex,sta_index,table=table)
            patches.append({"Comment":"{} _STA to XSTA Rename".format(dev_name),"Find":padl+sta_hex+padr,"Replace":padl+xsta_hex+padr})
        return {"valid":True,"has_var":has_var,"sta":sta,"patches":patches,"device":dev,"dev_name":dev_name,"dev_hid":dev_hid,"root":root,"sta_type":sta_type}

    def get_address_from_line(self, line, split_by="_ADR, ", table=None):
        if table is None:
            table = self.acpi.get_dsdt_or_only()
        try:
            return int(table["lines"][line].split(split_by)[1].split(")")[0].replace("Zero","0x0").replace("One","0x1"),16)
        except:
            return None
      
    def check_acpi_directory(self, acpi_directory):
        if acpi_directory:
            if not os.path.isdir(acpi_directory):
                self.utils.mkdirs(acpi_directory)
                return acpi_directory
            else:
                return acpi_directory
        return None

    def write_ssdt(self, ssdt_name, ssdt_content, compile=True):
        dsl_path = os.path.join(self.acpi_directory, ssdt_name + ".dsl")
        aml_path = os.path.join(self.acpi_directory, ssdt_name + ".aml")

        with open(dsl_path,"w") as f:
            f.write(ssdt_content)

        if not compile:
            return False
        
        compile = subprocess.run(
            [self.acpi.iasl, dsl_path],
            capture_output=True,
            check=True,  # Raises CalledProcessError for non-zero return code
        )
        if "Compilation successful" not in compile.stdout.decode().strip():
            return False
        else:
            os.remove(dsl_path)
        
        return os.path.exists(aml_path)

    def apply_acpi_patches(self):
        for acpi_patch in self.result.get("Patch"):
            acpi_patch["Base"] = acpi_patch.get("Base", "")
            acpi_patch["BaseSkip"] = acpi_patch.get("BaseSkip", 0)
            acpi_patch["Count"] = acpi_patch.get("Count", 0)
            acpi_patch["Enabled"] = True
            acpi_patch["Find"] = self.utils.hex_to_bytes(acpi_patch["Find"])
            acpi_patch["Limit"] = acpi_patch.get("Limit", 0)
            acpi_patch["Mask"] = self.utils.hex_to_bytes(acpi_patch.get("Mask", ""))
            acpi_patch["OemTableId"] = self.utils.hex_to_bytes(acpi_patch.get("OemTableId", ""))
            acpi_patch["Replace"] = self.utils.hex_to_bytes(acpi_patch["Replace"])
            acpi_patch["ReplaceMask"] = self.utils.hex_to_bytes(acpi_patch.get("ReplaceMask", ""))
            acpi_patch["Skip"] = acpi_patch.get("Skip", 0)
            acpi_patch["TableLength"] = acpi_patch.get("TableLength", 0)
            acpi_patch["TableSignature"] = self.utils.hex_to_bytes(acpi_patch.get("TableSignature", ""))

        self.result["Patch"] = sorted(self.result["Patch"], key=lambda x: x["Comment"])

    def get_low_pin_count_bus_device(self):
        for lpc_bus_name in ("LPCB", "LPC0", "LPC", "SBRG", "PX40"):
            try:
                self.lpc_bus_device = self.acpi.get_device_paths(lpc_bus_name)[0][0]
                break
            except: 
                pass

    def add_intel_management_engine(self, cpu_codename, intel_mei):
        comment = "Creates a fake IMEI device to ensure Intel iGPUs acceleration functions properly"
        ssdt_name = "SSDT-IMEI"
        ssdt_content = """
DefinitionBlock ("", "SSDT", 2, "ZPSS", "IMEI", 0x00000000)
{
    External (_SB_.PCI0, DeviceObj)

    Scope (_SB.PCI0)
    {
        Device (IMEI)
        {
            Name (_ADR, 0x00160000)  // _ADR: Address
            Method (_STA, 0, NotSerialized)  // _STA: Status
            {
                If (_OSI ("Darwin"))
                {
                    Return (0x0F)
                }
                Else
                {
                    Return (Zero)
                }
            }
        }
    }
}"""

        if intel_mei:
            if "Sandy Bridge" in cpu_codename and intel_mei.get("Device ID") in "8086-1E3A" or  "Ivy Bridge" in cpu_codename and intel_mei.get("Device ID") in "8086-1C3A":
                imei_device = self.acpi.get_device_paths_with_hid("0x00160000", self.dsdt)

                if not imei_device:
                    self.result["Add"].append({
                        "Comment": comment,
                        "Enabled": self.write_ssdt(ssdt_name, ssdt_content),
                        "Path": ssdt_name + ".aml"
                    })

    def add_memory_controller_device(self, cpu_manufacturer, cpu_codename, smbios):
        if "Intel" not in cpu_manufacturer or "MacPro" in smbios and self.is_intel_hedt_cpu(cpu_codename):
            return
        
        comment = "Add a Memory Controller Hub Controller device to fix AppleSMBus"
        ssdt_name = "SSDT-MCHC"
        ssdt_content = """
DefinitionBlock ("", "SSDT", 2, "ZPSS", "MCHC", 0)
{
    External ([[PCIName]], DeviceObj)

    Scope ([[PCIName]])
    {
        Device (MCHC)
        {
            Name (_ADR, Zero)
            Method (_STA, 0, NotSerialized)
            {
                If (_OSI ("Darwin"))
                {
                    Return (0x0F)
                }
                Else
                {
                    Return (Zero)
                }
            }
        }
    }
}"""

        mchc_device = self.acpi.get_device_paths("MCHC", self.dsdt)

        if mchc_device:
            return
        
        pci_bus_device = ".".join(self.lpc_bus_device.split(".")[:2])
        ssdt_content = ssdt_content.replace("[[PCIName]]", pci_bus_device)

        self.result["Add"].append({
            "Comment": comment,
            "Enabled": self.write_ssdt(ssdt_name, ssdt_content),
            "Path": ssdt_name + ".aml"
        })

    def add_system_management_bus_device(self, cpu_manufacturer, cpu_codename):
        if "Intel" not in cpu_manufacturer:
            return
        
        try:
            smbus_device_name = self.acpi.get_device_paths_with_hid("0x001F0003" if self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, end=4) else "0x001F0004", self.dsdt)[0][0].split(".")[-1]
        except:
            smbus_device_name = "SBUS"
            
        pci_bus_device = ".".join(self.lpc_bus_device.split(".")[:2])
        smbus_device_path = "{}.{}".format(pci_bus_device, smbus_device_name)

        comment = "Add a System Management Bus device to fix AppleSMBus issues"
        ssdt_name = "SSDT-{}".format(smbus_device_name)
        ssdt_content = """
DefinitionBlock ("", "SSDT", 2, "ZPSS", "[[SMBUSName]]", 0)
{
    External ([[SMBUSDevice]], DeviceObj)

    Scope ([[SMBUSDevice]])
    {
        Device (BUS0)
        {
            Name (_CID, "smbus")
            Name (_ADR, Zero)
            Method (_STA, 0, NotSerialized)
            {
                If (_OSI ("Darwin"))
                {
                    Return (0x0F)
                }
                Else
                {
                    Return (Zero)
                }
            }
        }
    }
}""".replace("[[SMBUSName]]", smbus_device_name).replace("[[SMBUSDevice]]", smbus_device_path)

        self.result["Add"].append({
            "Comment": comment,
            "Enabled": self.write_ssdt(ssdt_name, ssdt_content),
            "Path": ssdt_name + ".aml"
        })

    def add_usb_power_properties(self, smbios):
        comment = "Creates an USBX device to inject USB power properties"
        ssdt_name = "SSDT-USBX"
        ssdt_content = """
DefinitionBlock ("", "SSDT", 2, "ZPSS", "USBX", 0x00001000)
{
    Scope (\\_SB)
    {
        Device (USBX)
        {
            Name (_ADR, Zero)  // _ADR: Address
            Method (_DSM, 4, NotSerialized)  // _DSM: Device-Specific Method
            {
                If (LNot (Arg2))
                {
                    Return (Buffer ()
                    {
                        0x03
                    })
                }
                Return (Package ()
                {[[USBX_PROPS]]
                })
            }
            Method (_STA, 0, NotSerialized)  // _STA: Status
            {
                If (_OSI ("Darwin"))
                {
                    Return (0x0F)
                }
                Else
                {
                    Return (Zero)
                }
            }
        }
    }
}"""
        
        usb_power_properties = None
        if self.utils.contains_any(["MacPro7,1", "iMacPro1,1", "iMac20,", "iMac19,", "iMac18,", "iMac17,", "iMac16,"], smbios):
            usb_power_properties = {
                "kUSBSleepPowerSupply":"0x13EC",
                "kUSBSleepPortCurrentLimit":"0x0834",
                "kUSBWakePowerSupply":"0x13EC",
                "kUSBWakePortCurrentLimit":"0x0834"
            }
        elif "MacMini8,1" in smbios:
            usb_power_properties = {
                "kUSBSleepPowerSupply":"0x0C80",
                "kUSBSleepPortCurrentLimit":"0x0834",
                "kUSBWakePowerSupply":"0x0C80",
                "kUSBWakePortCurrentLimit":"0x0834"
            }
        elif self.utils.contains_any(["MacBookPro16,", "MacBookPro15,", "MacBookPro14,", "MacBookPro13,", "MacBookAir9,1"], smbios):
            usb_power_properties = {
                "kUSBSleepPortCurrentLimit":"0x0BB8",
                "kUSBWakePortCurrentLimit":"0x0BB8"
            }
        elif "MacBook9,1" in smbios:
            usb_power_properties = {
                "kUSBSleepPowerSupply":"0x05DC",
                "kUSBSleepPortCurrentLimit":"0x05DC",
                "kUSBWakePowerSupply":"0x05DC",
                "kUSBWakePortCurrentLimit":"0x05DC"
            }

        if usb_power_properties:
            ssdt_content = ssdt_content.replace("[[USBX_PROPS]]",
                "".join("\n                    \"{}\",\n                    {}{}".format(key, usb_power_properties[key], "," if index < len(usb_power_properties) else "")
                for index, key in enumerate(usb_power_properties, start=1))
            )
            self.result["Add"].append({
                "Comment": comment,
                "Enabled": self.write_ssdt(ssdt_name, ssdt_content),
                "Path": ssdt_name + ".aml"
            })

    def ambient_light_sensor(self, motherboard_name, platform, integrated_gpu):
        if "Laptop" not in platform or not integrated_gpu or "SURFACE" in motherboard_name:
            return
        
        ssdt_name = "SSDT-ALS0"
        ssdt_content = """
// Resource: https://github.com/acidanthera/OpenCorePkg/blob/master/Docs/AcpiSamples/Source/SSDT-ALS0.dsl

/*
 * Starting with macOS 10.15 Ambient Light Sensor presence is required for backlight functioning.
 * Here we create an Ambient Light Sensor ACPI Device, which can be used by SMCLightSensor kext
 * to report either dummy (when no device is present) or valid values through SMC interface.
 */
DefinitionBlock ("", "SSDT", 2, "ZPSS", "ALS0", 0x00000000)
{
    Scope (_SB)
    {
        Device (ALS0)
        {
            Name (_HID, "ACPI0008" /* Ambient Light Sensor Device */)  // _HID: Hardware ID
            Name (_CID, "smc-als")  // _CID: Compatible ID
            Name (_ALI, 0x012C)  // _ALI: Ambient Light Illuminance
            Name (_ALR, Package (0x01)  // _ALR: Ambient Light Response
            {
                Package (0x02)
                {
                    0x64, 
                    0x012C
                }
            })
            Method (_STA, 0, NotSerialized)  // _STA: Status
            {
                If (_OSI ("Darwin"))
                {
                    Return (0x0F)
                }
                Else
                {
                    Return (Zero)
                }
            }
        }
    }
}"""
        try:
            als_device = self.acpi.get_device_paths_with_hid("ACPI0008", self.dsdt)[0][0]
        except:
            als_device = None

        if als_device:
            als_device_name = als_device.split(".")[-1]
            if "." not in als_device:
                als_device_name = als_device_name[1:]

            sta = self.get_sta_var(var=None, device=None, dev_hid="ACPI0008", dev_name=als_device_name, table=self.dsdt)

            if sta.get("patches"):
                self.result["Patch"].extend(sta.get("patches", []))
            
            ssdt_name = "SSDT-{}".format(als_device_name)
            ssdt_content = """
DefinitionBlock ("", "SSDT", 2, "ZPSS", "[[ALSName]]", 0x00000000)
{
    External ([[ALSDevice]], DeviceObj)
    External ([[ALSDevice]].XSTA, [[STAType]])

    Scope ([[ALSDevice]])
    {
        Method (_STA, 0, NotSerialized)  // _STA: Status
        {
            If (_OSI ("Darwin"))
            {
                Return (0)
            }
            Else
            {
                Return ([[XSTA]])
            }
        }
    }
}""".replace("[[ALSName]]", als_device_name) \
    .replace("[[ALSDevice]]", als_device) \
    .replace("[[STAType]]", sta.get("sta_type","MethodObj")) \
    .replace("[[XSTA]]", "{}.XSTA{}".format(als_device," ()" if sta.get("sta_type","MethodObj") == "MethodObj" else "") if sta else "0x0F")

        comment = "{} Ambient Light Sensor device for storing the current brightness/auto-brightness level".format("Fake" if not als_device else "Enable")
        self.result["Add"].append({
            "Comment": comment,
            "Enabled": self.write_ssdt(ssdt_name, ssdt_content),
            "Path": ssdt_name + ".aml"
        })

    def disable_rhub_devices(self):
        comment = "Disable RHUB/HUBN/URTH devices and rename PXSX, XHC1, EHC1, and EHC2 devices"
        ssdt_name = "SSDT-USB-Reset"
        ssdt_content = """
DefinitionBlock ("", "SSDT", 2, "ZPSS", "UsbReset", 0x00001000)
{
"""
        rhub_devices = self.acpi.get_device_paths("RHUB", self.dsdt)
        rhub_devices.extend(self.acpi.get_device_paths("HUBN", self.dsdt))
        rhub_devices.extend(self.acpi.get_device_paths("URTH", self.dsdt))
        if not len(rhub_devices):
            return
        
        tasks = []
        used_names = []
        xhc_num = 2
        ehc_num = 1
        for rhub_device in rhub_devices:
            task = {
                "device": rhub_device[0]
            }
            name = rhub_device[0].split(".")[-2]

            if name in self.illegal_names or name in used_names:
                task["device"] = ".".join(task["device"].split(".")[:-1])
                task["parent"] = ".".join(task["device"].split(".")[:-1])

                if name.startswith("EHC"):
                    task["rename"],ehc_num = self.get_unique_device(task["parent"],"EH01",ehc_num,used_names)
                    ehc_num += 1 # Increment the name number
                else:
                    task["rename"],xhc_num = self.get_unique_device(task["parent"],"XHCI",xhc_num,used_names)
                    xhc_num += 1 # Increment the name number
                used_names.append(task["rename"])
            else:
                used_names.append(name)
            sta_method = self.acpi.get_method_paths(task["device"]+"._STA", self.dsdt)
            if len(sta_method):
                sta_index = self.acpi.find_next_hex(sta_method[0][1], self.dsdt)[1]
                sta_hex  = "5F535441"
                xsta_hex = "58535441"
                padl,padr = self.acpi.get_shortest_unique_pad(sta_hex, sta_index, self.dsdt)
                self.result.get("Patch").append({
                    "Comment": "{} _STA to XSTA Rename".format(task["device"].split(".")[-1]),
                    "Find": padl+sta_hex+padr,
                    "Replace": padl+xsta_hex+padr
                })
            scope_adr = self.acpi.get_name_paths(task["device"]+"._ADR", self.dsdt)
            task["address"] = self.dsdt.get("lines")[scope_adr[0][1]].strip() if len(scope_adr) else "Name (_ADR, Zero)  // _ADR: Address"
            tasks.append(task)

        parents = sorted(list(set([task["parent"] for task in tasks if task.get("parent", None)])))
        for parent in parents:
            ssdt_content += "    External ({}, DeviceObj)\n".format(parent)
        for task in tasks:
            ssdt_content += "    External ({}, DeviceObj)\n".format(task["device"])
        for task in tasks:
            if task.get("rename", None):
                ssdt_content += """
    Scope ([[device]])
    {
        Method (_STA, 0, NotSerialized)  // _STA: Status
        {
            If (_OSI ("Darwin"))
            {
                Return (Zero)
            }
            Else
            {
                Return (0x0F)
            }
        }
    }

    Scope ([[parent]])
    {
        Device ([[new_device]])
        {
            [[address]]
            Method (_STA, 0, NotSerialized)  // _STA: Status
            {
                If (_OSI ("Darwin"))
                {
                    Return (0x0F)
                }
                Else
                {
                    Return (Zero)
                }
            }
        }
    }
""".replace("[[device]]", task["device"]) \
    .replace("[[parent]]", task["parent"]) \
    .replace("[[address]]", task.get("address", "Name (_ADR, Zero)  // _ADR: Address")) \
    .replace("[[new_device]]", task["rename"])
            else:
                ssdt_content += """
    Scope ([[device]])
    {
        Method (_STA, 0, NotSerialized)  // _STA: Status
        {
            If (_OSI ("Darwin"))
            {
                Return (Zero)
            }
            Else
            {
                Return (0x0F)
            }
        }
    }
    """.replace("[[device]]", task["device"])
        ssdt_content += "\n}"

        self.result["Add"].append({
            "Comment": comment,
            "Enabled": self.write_ssdt(ssdt_name, ssdt_content),
            "Path": ssdt_name + ".aml"
        })

    def disable_unsupported_device(self, unsupported_devices):
        for device_name, device_props in unsupported_devices.items():
            if device_props.get("Bus Type").startswith("USB"):
                continue

            comment = "Disable {}".format(device_name.split(": ")[-1])
            ssdt_name = None
            if "Storage" in device_name:
                ssdt_name = "SSDT-Disable_NVMe"
                ssdt_content = """
// Replace all "_SB.PCI0.RP09.PXSX" with the ACPI path of your SSD NVMe

DefinitionBlock ("", "SSDT", 2, "ZPSS", "DNVMe", 0x00000000)
{
    External (_SB.PCI0.RP09.PXSX, DeviceObj)

    Method (_SB.PCI0.RP09.PXSX._DSM, 4, NotSerialized)  // _DSM: Device-Specific Method
    {
        If (_OSI ("Darwin"))
        {
            If (!Arg2)
            {
                Return (Buffer (One)
                {
                     0x03                                             // .
                })
            }

            Return (Package (0x02)
            {
                "class-code", 
                Buffer (0x04)
                {
                     0xFF, 0x08, 0x01, 0x00                           // ....
                }
            })
        }
    }
}
"""
            elif "WiFi" in device_name or "SD Controller" in device_name:
                ssdt_name = "SSDT-Disable_{}".format("WiFi" if "WiFi" in device_name else "SD_Card_Reader")
                ssdt_content = """
// Replace all "_SB.PCI0.RP01" with the ACPI path of your [[DeviceType]]

DefinitionBlock ("", "SSDT", 2, "ZPSS", "[[DeviceType]]", 0)
{
    External (_SB.PCI0.RP01, DeviceObj)

    Scope (_SB.PCI0.RP01)
    {
        OperationRegion (DE01, PCI_Config, 0x50, 1)
        Field (DE01, AnyAcc, NoLock, Preserve)
        {
                ,   4, 
            DDDD,   1
        }
        Method (_STA, 0, Serialized)
        {
            If (_OSI ("Darwin"))
            {
                Return (0)
            }
            Else
            {
                Return (0x0F)
            }
        }
    }
    
    Scope (\\)
    {
        If (_OSI ("Darwin"))
        {
            \\_SB.PCI0.RP01.DDDD = One
        }
    }
}""".replace("[[DeviceType]]", "DWiFi" if "WiFi" in device_name else "DSDC")

            if ssdt_name:
                self.result["Add"].append({
                    "Comment": comment,
                    "Enabled": self.write_ssdt(ssdt_name, ssdt_content, compile=False),
                    "Path": ssdt_name + ".aml"
                })
  
    def enable_backlight_controls(self, platform, cpu_codename, integrated_gpu):
        if "Laptop" not in platform or not integrated_gpu:
            return
        
        uid_value = 19
        if self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, end=2):
            uid_value = 14
        elif self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, start=2, end=4):
            uid_value = 15
        elif self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, start=4, end=7):
            uid_value = 16
        
        igpu = ""
        if uid_value == 14:
            # Try to gather our iGPU device
            paths = self.acpi.get_path_of_type(obj_type="Name", obj="_ADR", table=self.dsdt)
            for path in paths:
                adr = self.get_address_from_line(path[1], self.dsdt)
                if adr == 0x00020000:
                    igpu = path[0][:-5]
                    break
            if not igpu: # Try matching by name
                pci_roots = self.acpi.get_device_paths_with_hid("PNP0A08", self.dsdt)
                pci_roots += self.acpi.get_device_paths_with_hid("PNP0A03", self.dsdt)
                pci_roots += self.acpi.get_device_paths_with_hid("ACPI0016", self.dsdt)
                external = []
                for line in self.dsdt.get("lines"):
                    if not line.strip().startswith("External ("): continue # We don't need it
                    try:
                        path = line.split("(")[1].split(", ")[0]
                        # Prepend the backslash and ensure trailing underscores are stripped.
                        path = "\\"+".".join([x.rstrip("_").replace("\\","") for x in path.split(".")])
                        external.append(path)
                    except: pass
                for root in pci_roots:
                    for name in ("IGPU","_VID","VID0","VID1","GFX0","VGA","_VGA"):
                        test_path = "{}.{}".format(root[0],name)
                        device = self.acpi.get_device_paths(test_path, self.dsdt)
                        if device: device = device[0][0] # Unpack to the path
                        else:
                            # Walk the external paths and see if it's declared elsewhere?
                            # We're not patching anything directly - just getting a pathing
                            # reference, so it's fine to not have the surrounding code.
                            device = next((x for x in external if test_path == x),None)
                        if not device: continue # Not found :(
                        # Got a device - see if it has an _ADR, and skip if so - as it was wrong in the prior loop
                        if self.acpi.get_path_of_type(obj_type="Name",obj=device+"._ADR", table=self.dsdt): continue
                        # At this point - we got a hit
                        igpu = device
                        
        if "PNLF" in self.dsdt.get("table"):
            self.result.get("Patch").append({
                "Comment": "PNLF to XNLF Rename",
                "Find": "504E4C46",
                "Replace": "584E4C46"
            })

        nbcf = binascii.unhexlify("084E42434600")
        if nbcf in self.dsdt.get("raw"):
            self.result.get("Patch").append({
                "Comment": "NBCF Zero to One for BrightnessKeys.kext",
                "Find": "084E42434600",
                "Replace": "084E42434601"
            })

        comment = "Defines a PNLF device to enable backlight controls on laptops"
        ssdt_name = "SSDT-PNLF"
        ssdt_content = """
DefinitionBlock ("", "SSDT", 2, "ZPSS", "PNLF", 0x00000000)
{"""
        if igpu:
            ssdt_content += """\n    External ([[igpu_path]], DeviceObj)\n"""
        ssdt_content += """
    Device (PNLF)
    {
        Name (_HID, EisaId ("APP0002"))  // _HID: Hardware ID
        Name (_CID, "backlight")  // _CID: Compatible ID
        Name (_UID, [[uid_value]])  // _UID: Unique ID
        
        Method (_STA, 0, NotSerialized)  // _STA: Status
        {
            If (_OSI ("Darwin"))
            {
                Return (0x0B)
            }
            Else
            {
                Return (Zero)
            }
        }"""
        if igpu:
            ssdt_content += """
        Method (_INI, 0, Serialized)
        {
            If (LAnd (_OSI ("Darwin"), CondRefOf ([[igpu_path]])))
            {
                OperationRegion ([[igpu_path]].RMP3, PCI_Config, Zero, 0x14)
                Field ([[igpu_path]].RMP3, AnyAcc, NoLock, Preserve)
                {
                    Offset (0x02), GDID,16,
                    Offset (0x10), BAR1,32,
                }
                // IGPU PWM backlight register descriptions:
                //   LEV2 not currently used
                //   LEVL level of backlight in Sandy/Ivy
                //   P0BL counter, when zero is vertical blank
                //   GRAN see description below in INI1 method
                //   LEVW should be initialized to 0xC0000000
                //   LEVX PWMMax except FBTYPE_HSWPLUS combo of max/level (Sandy/Ivy stored in MSW)
                //   LEVD level of backlight for Coffeelake
                //   PCHL not currently used
                OperationRegion (RMB1, SystemMemory, BAR1 & ~0xF, 0xe1184)
                Field(RMB1, AnyAcc, Lock, Preserve)
                {
                    Offset (0x48250),
                    LEV2, 32,
                    LEVL, 32,
                    Offset (0x70040),
                    P0BL, 32,
                    Offset (0xc2000),
                    GRAN, 32,
                    Offset (0xc8250),
                    LEVW, 32,
                    LEVX, 32,
                    LEVD, 32,
                    Offset (0xe1180),
                    PCHL, 32,
                }
                // Now fixup the backlight PWM depending on the framebuffer type
                // At this point:
                //   Local4 is RMCF.BLKT value (unused here), if specified (default is 1)
                //   Local0 is device-id for IGPU
                //   Local2 is LMAX, if specified (Ones means based on device-id)
                //   Local3 is framebuffer type

                // Adjustment required when using WhateverGreen.kext
                Local0 = GDID
                Local2 = Ones
                Local3 = 0

                // check Sandy/Ivy
                // #define FBTYPE_SANDYIVY 1
                If (LOr (LEqual (1, Local3), LNotEqual (Match (Package()
                {
                    // Sandy HD3000
                    0x010b, 0x0102,
                    0x0106, 0x1106, 0x1601, 0x0116, 0x0126,
                    0x0112, 0x0122,
                    // Ivy
                    0x0152, 0x0156, 0x0162, 0x0166,
                    0x016a,
                    // Arrandale
                    0x0046, 0x0042,
                }, MEQ, Local0, MTR, 0, 0), Ones)))
                {
                    if (LEqual (Local2, Ones))
                    {
                        // #define SANDYIVY_PWMMAX 0x710
                        Store (0x710, Local2)
                    }
                    // change/scale only if different than current...
                    Store (LEVX >> 16, Local1)
                    If (LNot (Local1))
                    {
                        Store (Local2, Local1)
                    }
                    If (LNotEqual (Local2, Local1))
                    {
                        // set new backlight PWMMax but retain current backlight level by scaling
                        Store ((LEVL * Local2) / Local1, Local0)
                        Store (Local2 << 16, Local3)
                        If (LGreater (Local2, Local1))
                        {
                            // PWMMax is getting larger... store new PWMMax first
                            Store (Local3, LEVX)
                            Store (Local0, LEVL)
                        }
                        Else
                        {
                            // otherwise, store new brightness level, followed by new PWMMax
                            Store (Local0, LEVL)
                            Store (Local3, LEVX)
                        }
                    }
                }
            }
        }"""
        ssdt_content += """
    }
}"""
        # Perform the replacements
        ssdt_content = ssdt_content.replace("[[uid_value]]", str(uid_value)).replace("[[igpu_path]]",igpu)        
        
        self.result["Add"].append({
            "Comment": comment,
            "Enabled": self.write_ssdt(ssdt_name, ssdt_content),
            "Path": ssdt_name + ".aml"
        })

    def enable_cpu_power_management(self, cpu_codename):
        if self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, end=2):
            return
        
        comment = "Sets plugin-type to 1 on the first Processor object to enable CPU power management"
        ssdt_name = "SSDT-PLUG"

        try: 
            cpu_name = self.acpi.get_processor_paths()[0][0]
        except: 
            cpu_name = None

        if cpu_name:
            ssdt_content = """
// Resource: https://github.com/acidanthera/OpenCorePkg/blob/master/Docs/AcpiSamples/SSDT-PLUG.dsl

DefinitionBlock ("", "SSDT", 2, "ZPSS", "CpuPlug", 0x00003000)
{
    External ([[CPUName]], ProcessorObj)
    Scope ([[CPUName]])
    {
        If (_OSI ("Darwin")) {
            Method (_DSM, 4, NotSerialized)  // _DSM: Device-Specific Method
            {
                If (LNot (Arg2))
                {
                    Return (Buffer (One)
                    {
                        0x03
                    })
                }
                Return (Package (0x02)
                {
                    "plugin-type", 
                    One
                })
            }
        }
    }
}""".replace("[[CPUName]]", cpu_name)
        else:
            comment = "Redefines modern CPU Devices as legacy Processor objects and sets plugin-type to 1 on the first to enable CPU power management"
            ssdt_name += "-ALT"
            procs = self.acpi.get_device_paths_with_hid("ACPI0007", self.dsdt)
            if not procs:
                return
            parent = procs[0][0].split(".")[0]
            proc_list = []
            for proc in procs:
                uid = self.acpi.get_path_of_type(obj_type="Name", obj=proc[0]+"._UID", table=self.dsdt)
                if not uid:
                    continue
                # Let's get the actual _UID value
                try:
                    _uid = self.dsdt.get("lines")[uid[0][1]].split("_UID, ")[1].split(")")[0]
                    proc_list.append((proc[0],_uid))
                except:
                    pass
            if not proc_list:
                return
            ssdt_content = """
// Resource:  https://github.com/acidanthera/OpenCorePkg/blob/master/Docs/AcpiSamples/Source/SSDT-PLUG-ALT.dsl

DefinitionBlock ("", "SSDT", 2, "ZPSS", "CpuPlugA", 0x00003000)
{
    External ([[parent]], DeviceObj)

    Scope ([[parent]])
    {""".replace("[[parent]]",parent)
            # Walk the processor objects, and add them to the SSDT
            for i,proc_uid in enumerate(proc_list):
                proc,uid = proc_uid
                adr = hex(i)[2:].upper()
                name = "CP00"[:-len(adr)]+adr
                ssdt_content += """
        Processor ([[name]], [[uid]], 0x00000510, 0x06)
        {
            // [[proc]]
            Name (_HID, "ACPI0007" /* Processor Device */)  // _HID: Hardware ID
            Name (_UID, [[uid]])
            Method (_STA, 0, NotSerialized)  // _STA: Status
            {
                If (_OSI ("Darwin"))
                {
                    Return (0x0F)
                }
                Else
                {
                    Return (Zero)
                }
            }""".replace("[[name]]",name).replace("[[uid]]",uid).replace("[[proc]]",proc)
                if i == 0: # Got the first, add plugin-type as well
                    ssdt_content += """
            Method (_DSM, 4, NotSerialized)
            {
                If (LNot (Arg2)) {
                    Return (Buffer (One) { 0x03 })
                }

                Return (Package (0x02)
                {
                    "plugin-type",
                    One
                })
            }"""
                # Close up the SSDT
                ssdt_content += """
        }"""
            ssdt_content += """
    }
}"""

        self.result["Add"].append({
            "Comment": comment,
            "Enabled": self.write_ssdt(ssdt_name, ssdt_content),
            "Path": ssdt_name + ".aml"
        })

    def enable_gpio_device(self, platform, cpu_manufacturer, touchpad_communication):
        if "Laptop" not in platform or "Intel" not in cpu_manufacturer or not "I2C" in touchpad_communication:
            return

        try:
            gpio_device = self.acpi.get_device_paths("GPI0", self.dsdt)[0][0] or self.acpi.get_device_paths("GPIO", self.dsdt)[0][0]
        except:
            gpio_device = None

        if not gpio_device:
            return
        
        sta = self.get_sta_var(var=None, device=gpio_device, dev_hid=None, dev_name=gpio_device.split(".")[-1], table=self.dsdt)

        if sta.get("patches"):
            self.result["Patch"].extend(sta.get("patches", []))
        
        comment = "Enable GPIO device for a I2C TouchPads to function properly"
        ssdt_name = "SSDT-GPI0"
        ssdt_content = """
DefinitionBlock ("", "SSDT", 2, "ZPSS", "GPI0", 0x00000000)
{
    External ([[GPI0Path]], DeviceObj)
    External ([[GPI0Path]].XSTA, [[STAType]])

    Scope ([[GPI0Path]])
    {
        Method (_STA, 0, NotSerialized)  // _STA: Status
        {
            If (_OSI ("Darwin"))
            {
                Return (0x0F)
            }
            Else
            {
                Return ([[XSTA]])
            }
        }
    }
}""".replace("[[GPI0Path]]", gpio_device) \
    .replace("[[STAType]]", sta.get("sta_type","MethodObj")) \
    .replace("[[XSTA]]", "{}.XSTA{}".format(gpio_device," ()" if sta.get("sta_type","MethodObj") == "MethodObj" else "") if sta else "0x0F")

        self.result["Add"].append({
            "Comment": comment,
            "Enabled": self.write_ssdt(ssdt_name, ssdt_content),
            "Path": ssdt_name + ".aml"
        })
    
    def enable_nvram_support(self, motherboard_chipset):
        if not self.utils.contains_any(["H310", "H370", "B360", "B365", "Z390"], motherboard_chipset) or not self.lpc_bus_device:
            return
        
        comment = "Add a PMCR device to enable NVRAM support for 300-series mainboards"
        ssdt_name = "SSDT-PMC"
        ssdt_content = """
// Resource: https://github.com/acidanthera/OpenCorePkg/blob/master/Docs/AcpiSamples/Source/SSDT-PMC.dsl

/*
 * Intel 300-series PMC support for macOS
 *
 * Starting from Z390 chipsets PMC (D31:F2) is only available through MMIO.
 * Since there is no standard device for PMC in ACPI, Apple introduced its
 * own naming "APP9876" to access this device from AppleIntelPCHPMC driver.
 * To avoid confusion we disable this device for all other operating systems,
 * as they normally use another non-standard device with "PNP0C02" HID and
 * "PCHRESV" UID.
 *
 * On certain implementations, including APTIO V, PMC initialisation is
 * required for NVRAM access. Otherwise it will freeze in SMM mode.
 * The reason for this is rather unclear. Note, that PMC and SPI are
 * located in separate memory regions and PCHRESV maps both, yet only
 * PMC region is used by AppleIntelPCHPMC:
 * 0xFE000000~0xFE00FFFF - PMC MBAR
 * 0xFE010000~0xFE010FFF - SPI BAR0
 * 0xFE020000~0xFE035FFF - SerialIo BAR in ACPI mode
 *
 * PMC device has nothing to do to LPC bus, but is added to its scope for
 * faster initialisation. If we add it to PCI0, where it normally exists,
 * it will start in the end of PCI configuration, which is too late for
 * NVRAM support.
 */
DefinitionBlock ("", "SSDT", 2, "ACDT", "PMCR", 0x00001000)
{
    External ([[LPCPath]], DeviceObj)

    Scope ([[LPCPath]])
    {
        Device (PMCR)
        {
            Name (_HID, EisaId ("APP9876"))  // _HID: Hardware ID
            Method (_STA, 0, NotSerialized)  // _STA: Status
            {
                If (_OSI ("Darwin"))
                {
                    Return (0x0B)
                }
                Else
                {
                    Return (Zero)
                }
            }
            Name (_CRS, ResourceTemplate ()  // _CRS: Current Resource Settings
            {
                Memory32Fixed (ReadWrite,
                    0xFE000000,         // Address Base
                    0x00010000,         // Address Length
                    )
            })
        }
    }
}""".replace("[[LPCPath]]", self.lpc_bus_device)

        self.result["Add"].append({
            "Comment": comment,
            "Enabled": self.write_ssdt(ssdt_name, ssdt_content),
            "Path": ssdt_name + ".aml"
        })

    def fake_embedded_controller(self, platform):
        comment = "Add a fake EC to ensure macOS compatibility"
        ssdt_name = "SSDT-EC"

        laptop = "Laptop" in platform
        
        def sta_needs_patching(sta):
            if not isinstance(sta,dict) or not sta.get("sta"):
                return False
            # Check if we have an IntObj or MethodObj
            # _STA, and scrape for values if possible.
            if sta.get("sta_type") == "IntObj":
                # We got an int - see if it's force-enabled
                try:
                    sta_scope = self.dsdt.get("lines")[sta["sta"][0][1]]
                    if not "Name (_STA, 0x0F)" in sta_scope:
                        return True
                except Exception as e:
                    print(e)
                    return True
            elif sta.get("sta_type") == "MethodObj":
                # We got a method - if we have more than one
                # "Return (", or not a single "Return (0x0F)",
                # then we need to patch this out and replace
                try:
                    sta_scope = "\n".join(self.acpi.get_scope(sta["sta"][0][1],strip_comments=True,table=self.dsdt))
                    if sta_scope.count("Return (") > 1 or not "Return (0x0F)" in sta_scope:
                        # More than one return, or our return isn't force-enabled
                        return True
                except Exception as e:
                    return True
            # If we got here - it's not a recognized type, or
            # it was fullly qualified and doesn't need patching
            return False
        rename = False
        named_ec = False
        ec_to_patch = []
        ec_to_enable = []
        ec_sta = {}
        ec_enable_sta = {}
        patches = []
        ec_located = False
        
        ec_list = self.acpi.get_device_paths_with_hid("PNP0C09",table=self.dsdt)
        if len(ec_list):
            self.lpc_bus_device = ".".join(ec_list[0][0].split(".")[:-1])
            for x in ec_list:
                device = orig_device = x[0]
                #print(" --> {}".format(device))
                if device.split(".")[-1] == "EC":
                    named_ec = True
                    if not laptop:
                        # Only rename if we're trying to replace it
                        #print(" ----> PNP0C09 (EC) called EC. Renaming")
                        device = ".".join(device.split(".")[:-1]+["EC0"])
                        rename = True
                scope = "\n".join(self.acpi.get_scope(x[1],strip_comments=True,table=self.dsdt))
                # We need to check for _HID, _CRS, and _GPE
                if all(y in scope for y in ["_HID","_CRS","_GPE"]):
                    #print(" ----> Valid PNP0C09 (EC) Device")
                    ec_located = True
                    sta = self.get_sta_var(
                        var=None,
                        device=orig_device,
                        dev_hid="PNP0C09",
                        dev_name=orig_device.split(".")[-1],
                        log_locate=False,
                        table=self.dsdt
                    )
                    if not laptop:
                        ec_to_patch.append(device)
                        # Only unconditionally override _STA methods
                        # if not building for a laptop
                        if sta.get("patches"):
                            patches.extend(sta.get("patches",[]))
                            ec_sta[device] = sta
                    elif sta.get("patches"):
                        if sta_needs_patching(sta):
                            # Retain the info as we need to override it
                            ec_to_enable.append(device)
                            ec_enable_sta[device] = sta
                            # Disable the patches by default and add to the list
                            for patch in sta.get("patches",[]):
                                patch["Enabled"] = False
                                patch["Disabled"] = True
                                patches.append(patch)
        if not ec_located:
            pass
            #print(" - No valid PNP0C09 (EC) devices found - only needs a Fake EC device")
        if laptop and named_ec and not patches:
            #print(" ----> Named EC device located - no fake needed.")
            #print("")
            #self.utils.request_input("Press [enter] to return to main menu...")
            return
        if not self.lpc_bus_device:
            #self.utils.request_input("Press [enter] to return to main menu...")
            return
        if rename == True:
            patches.insert(0,{
                "Comment":"EC to EC0{}".format("" if not ec_sta else " - must come before any EC _STA to XSTA renames!"),
                "Find":"45435f5f",
                "Replace":"4543305f"
            })
            comment += " - Needs EC to EC0 {}".format(
                "and EC _STA to XSTA renames" if ec_sta else "rename"
            )
        elif ec_sta:
            comment += " - Needs EC _STA to XSTA renames"
        #oc = {"Comment":comment,"Enabled":True,"Path":"SSDT-EC.aml"}
        #self.make_plist(oc, "SSDT-EC.aml", patches, replace=True)
        #print("Creating SSDT-EC...")
        ssdt_content = """
DefinitionBlock ("", "SSDT", 2, "CORP ", "SsdtEC", 0x00001000)
{
    External ([[LPCName]], DeviceObj)
""".replace("[[LPCName]]",self.lpc_bus_device)
        for x in ec_to_patch:
            ssdt_content += "    External ({}, DeviceObj)\n".format(x)
            if x in ec_sta:
                ssdt_content += "    External ({}.XSTA, {})\n".format(x,ec_sta[x].get("sta_type","MethodObj"))
        # Walk the ECs to enable
        for x in ec_to_enable:
            ssdt_content += "    External ({}, DeviceObj)\n".format(x)
            if x in ec_enable_sta:
                # Add the _STA and XSTA refs as the patch may not be enabled
                ssdt_content += "    External ({0}._STA, {1})\n    External ({0}.XSTA, {1})\n".format(x,ec_enable_sta[x].get("sta_type","MethodObj"))
        # Walk them again and add the _STAs
        for x in ec_to_patch:
            ssdt_content += """
    Scope ([[ECName]])
    {
        Method (_STA, 0, NotSerialized)  // _STA: Status
        {
            If (_OSI ("Darwin"))
            {
                Return (0)
            }
            Else
            {
                Return ([[XSTA]])
            }
        }
    }
""".replace("[[LPCName]]",self.lpc_bus_device).replace("[[ECName]]",x) \
    .replace("[[XSTA]]","{}.XSTA{}".format(x," ()" if ec_sta[x].get("sta_type","MethodObj")=="MethodObj" else "") if x in ec_sta else "0x0F")
        # Walk them yet again - and force enable as needed
        for x in ec_to_enable:
            ssdt_content += """
    If (LAnd (CondRefOf ([[ECName]].XSTA), LNot (CondRefOf ([[ECName]]._STA))))
    {
        Scope ([[ECName]])
        {
            Method (_STA, 0, NotSerialized)  // _STA: Status
            {
                If (_OSI ("Darwin"))
                {
                    Return (0x0F)
                }
                Else
                {
                    Return ([[XSTA]])
                }
            }
        }
    }
""".replace("[[LPCName]]", self.lpc_bus_device).replace("[[ECName]]",x) \
    .replace("[[XSTA]]","{}.XSTA{}".format(x," ()" if ec_enable_sta[x].get("sta_type","MethodObj")=="MethodObj" else "") if x in ec_enable_sta else "Zero")
        # Create the faked EC
        if not laptop or not named_ec:
            ssdt_content += """
    Scope ([[LPCName]])
    {
        Device (EC)
        {
            Name (_HID, "ACID0001")  // _HID: Hardware ID
            Method (_STA, 0, NotSerialized)  // _STA: Status
            {
                If (_OSI ("Darwin"))
                {
                    Return (0x0F)
                }
                Else
                {
                    Return (Zero)
                }
            }
        }
    }""".replace("[[LPCName]]", self.lpc_bus_device)
        # Close the SSDT scope
        ssdt_content += """
}"""
        
        if self.write_ssdt(ssdt_name, ssdt_content):
            self.result.get("Patch").extend(patches)
            self.result["Add"].append({
                "Comment": comment,
                "Enabled": True,
                "Path": ssdt_name + ".aml"
            })

    def fix_hp_005_post_error(self, motherboard_name):
        if "HP" not in motherboard_name:
            return
        
        if binascii.unhexlify("4701700070000108") in self.dsdt.get("raw"):
            self.result.get("Patch").append({
                "Comment": "Fix HP Real-Time Clock Power Loss (005) Post Error",
                "Find": "4701700070000108",
                "Replace": "4701700070000102"
            })

    def add_null_ethernet_device(self, ethernet_pci):
        if ethernet_pci:
            return
        
        random_mac_address = self.smbios.generate_random_mac()
        mac_address_byte = ", ".join([f'0x{random_mac_address[i:i+2]}' for i in range(0, len(random_mac_address), 2)])
        
        comment = "Creates a Null Ethernet to allow macOS system access to iServices"
        ssdt_name = "SSDT-RMNE"
        ssdt_content = """
// Resource: https://github.com/RehabMan/OS-X-Null-Ethernet/blob/master/SSDT-RMNE.dsl

/* ssdt.dsl -- SSDT injector for NullEthernet
 *
 * Copyright (c) 2014 RehabMan <racerrehabman@gmail.com>
 * All rights reserved.
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the Free
 * Software Foundation; either version 2 of the License, or (at your option)
 * any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
 * more details.
 *
 */

// Use this SSDT as an alternative to patching your DSDT...

DefinitionBlock("", "SSDT", 2, "ZPSS", "RMNE", 0x00001000)
{
    Device (RMNE)
    {
        Name (_ADR, Zero)
        // The NullEthernet kext matches on this HID
        Name (_HID, "NULE0000")
        // This is the MAC address returned by the kext. Modify if necessary.
        Name (MAC, Buffer() { [[MACAddress]] })
        Method (_DSM, 4, NotSerialized)
        {
            If (LEqual (Arg2, Zero)) { Return (Buffer() { 0x03 } ) }
            Return (Package()
            {
                "built-in", Buffer() { 0x00 },
                "IOName", "ethernet",
                "name", Buffer() { "ethernet" },
                "model", Buffer() { "RM-NullEthernet-1001" },
                "device_type", Buffer() { "ethernet" },
            })
        }

        Method (_STA, 0, NotSerialized)  // _STA: Status
        {
            If (_OSI ("Darwin"))
            {
                Return (0x0F)
            }
            Else
            {
                Return (Zero)
            }
        }
    }
}""".replace("[[MACAddress]]", mac_address_byte)

        self.result["Add"].append({
            "Comment": comment,
            "Enabled": self.write_ssdt(ssdt_name, ssdt_content),
            "Path": ssdt_name + ".aml"
        })

    def is_intel_hedt_cpu(self, cpu_codename):
        return "-E" in cpu_codename and not self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, end=4) is None or \
            ("-X" in cpu_codename or "-W" in cpu_codename) and not self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, start=4, end=6) is None

    def list_irqs(self):
        # Walks the DSDT keeping track of the current device and
        # saving the IRQNoFlags if found
        devices = {}
        current_device = None
        current_hid = None
        irq = False
        last_irq = False
        irq_index = 0
        for index,line in enumerate(self.acpi.get_dsdt_or_only()["lines"]):
            if self.acpi.is_hex(line):
                # Skip all hex lines
                continue
            if irq:
                # Get the values
                num = line.split("{")[1].split("}")[0].replace(" ","")
                num = "#" if not len(num) else num
                if current_device in devices:
                    if last_irq: # In a row
                        devices[current_device]["irq"] += ":"+num
                    else: # Skipped at least one line
                        irq_index = self.acpi.find_next_hex(index)[1]
                        devices[current_device]["irq"] += "-"+str(irq_index)+"|"+num
                else:
                    irq_index = self.acpi.find_next_hex(index)[1]
                    devices[current_device] = {"irq":str(irq_index)+"|"+num}
                irq = False
                last_irq = True
            elif "Device (" in line:
                # Check if we retain the _HID here
                if current_device and current_device in devices and current_hid:
                    # Save it
                    devices[current_device]["hid"] = current_hid
                last_irq = False
                current_hid = None
                try: current_device = line.split("(")[1].split(")")[0]
                except:
                    current_device = None
                    continue
            elif "_HID, " in line and current_device:
                try: current_hid = line.split('"')[1]
                except: pass
            elif "IRQNoFlags" in line and current_device:
                # Next line has our interrupts
                irq = True
            # Check if just a filler line
            elif len(line.replace("{","").replace("}","").replace("(","").replace(")","").replace(" ","").split("//")[0]):
                # Reset last IRQ as it's not in a row
                last_irq = False
        # Retain the final _HID if needed
        if current_device and current_device in devices and current_hid:
            devices[current_device]["hid"] = current_hid
        return devices

    def get_irq_choice(self, irqs):
        names_and_hids = [
            "PIC",
            "IPIC",
            "TMR",
            "TIMR",
            "RTC",
            "RTC0",
            "RTC1",
            "PNPC0000",
            "PNP0100",
            "PNP0B00"
        ]
        defaults = [x for x in irqs if x.upper() in names_and_hids or irqs[x].get("hid","").upper() in names_and_hids]
        d = {}

        for x in defaults:
            d[x] = self.target_irqs
        return d

    def get_hex_from_irqs(self, irq, rem_irq = None):
        # We need to search for a few different types:
        #
        # 22 XX XX 22 XX XX 22 XX XX (multiples on different lines)
        # 22 XX XX (summed multiples in the same bracket - {0,8,11})
        # 22 XX XX (single IRQNoFlags entry)
        # 
        # Can end with 79 [00] (end of method), 86 09 (middle of method) or 47 01 (unknown)
        lines = []
        remd  = []
        for a in irq.split("-"):
            index,i = a.split("|") # Get the index
            index = int(index)
            find = self.get_int_for_line(i)
            repl = [0]*len(find)
            # Now we need to verify if we're patching *all* IRQs, or just some specifics
            if rem_irq:
                repl = [x for x in find]
                matched = []
                for x in rem_irq:
                    # Get the int
                    rem = self.convert_irq_to_int(x)
                    repl1 = [y&(rem^0xFFFF) if y >= rem else y for y in repl]
                    if repl1 != repl:
                        # Changes were made
                        remd.append(x)
                    repl = [y for y in repl1]
            # Get the hex
            d = {
                "irq":i,
                "find": "".join(["22"+self.acpi.get_hex_from_int(x) for x in find]),
                "repl": "".join(["22"+self.acpi.get_hex_from_int(x) for x in repl]),
                "remd": remd,
                "index": index
                }
            d["changed"] = not (d["find"]==d["repl"])
            lines.append(d)
        return lines
    
    def get_int_for_line(self, irq):
        irq_list = []
        for i in irq.split(":"):
            irq_list.append(self.same_line_irq(i))
        return irq_list

    def convert_irq_to_int(self, irq):
        b = "0"*(16-irq)+"1"+"0"*(irq)
        return int(b,2)

    def same_line_irq(self, irq):
        # We sum the IRQ values and return the int
        total = 0
        for i in irq.split(","):
            if i == "#":
                continue # Null value
            try: i=int(i)
            except: continue # Not an int
            if i > 15 or i < 0:
                continue # Out of range
            total = total | self.convert_irq_to_int(i)
        return total
    
    def fix_irq_conflicts(self, platform, cpu_codename):
        if "Laptop" not in platform or self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, end=4) is None:
            return
        
        hpets = self.acpi.get_device_paths_with_hid("PNP0103")
        hpet_fake = not hpets
        hpet_sta = False
        sta = None
        if hpets:
            name = hpets[0][0]
            
            sta = self.get_sta_var(var=None,dev_hid="PNP0103",dev_name="HPET",log_locate=False)
            if sta.get("patches"):
                hpet_sta = True
                self.result.get("Patch").extend(sta.get("patches",[]))

            hpet = self.acpi.get_method_paths(name+"._CRS") or self.acpi.get_name_paths(name+"._CRS")
            if not hpet:
                return

            crs_index = self.acpi.find_next_hex(hpet[0][1])[1]

            mem_base = mem_length = primed = None
            for line in self.acpi.get_scope(hpets[0][1],strip_comments=True):
                if "Memory32Fixed (" in line:
                    primed = True
                    continue
                if not primed:
                    continue
                elif ")" in line: # Reached the end of the scope
                    break
                # We're primed, and not at the end - let's try to get the base and length
                try:
                    val = line.strip().split(",")[0].replace("Zero","0x0").replace("One","0x1")
                    check = int(val,16)
                except:
                    break
                # Set them in order
                if mem_base is None:
                    mem_base = val
                else:
                    mem_length = val
                    break # Leave after we get both values
            # Check if we found the values
            got_mem = mem_base and mem_length
            if not got_mem:
                mem_base = "0xFED00000"
                mem_length = "0x00000400"
            crs  = "5F435253"
            xcrs = "58435253"
            padl,padr = self.acpi.get_shortest_unique_pad(crs, crs_index)
            self.result.get("Patch").append({"Comment":"{} _CRS to XCRS Rename".format(name.split(".")[-1].lstrip("\\")),"Find":padl+crs+padr,"Replace":padl+xcrs+padr})
        else:
            ec_list = self.acpi.get_device_paths_with_hid("PNP0C09")
            name = None
            if len(ec_list):
                name = ".".join(ec_list[0][0].split(".")[:-1])
            if name == None:
                for x in ("LPCB", "LPC0", "LPC", "SBRG", "PX40"):
                    try:
                        name = self.acpi.get_device_paths(x)[0][0]
                        break
                    except: pass
            if not name:
                return
            
        devs = self.list_irqs()
        target_irqs = self.get_irq_choice(devs)
        if target_irqs is None: return # Bailed, going to the main menu
        # Let's apply patches as we go
        saved_dsdt = self.dsdt.get("raw")
        unique_patches  = {}
        generic_patches = []
        for dev in devs:
            if not dev in target_irqs:
                continue
            irq_patches = self.get_hex_from_irqs(devs[dev]["irq"],target_irqs[dev])
            i = [x for x in irq_patches if x["changed"]]
            for a,t in enumerate(i):
                if not t["changed"]:
                    # Nothing patched - skip
                    continue
                # Try our endings here - 7900, 8609, and 4701 - also allow for up to 8 chars of pad (thanks MSI)
                matches = re.findall("("+t["find"]+"(.{0,8})(7900|4701|8609))",self.acpi.get_hex_starting_at(t["index"])[0])
                if not len(matches):
                    continue
                if len(matches) > 1:
                    # Found too many matches!
                    # Add them all as find/replace entries
                    for x in matches:
                        generic_patches.append({
                            "remd":",".join([str(y) for y in set(t["remd"])]),
                            "orig":t["find"],
                            "find":t["find"]+"".join(x[1:]),
                            "repl":t["repl"]+"".join(x[1:])
                        })
                    continue
                ending = "".join(matches[0][1:])
                padl,padr = self.acpi.get_shortest_unique_pad(t["find"]+ending, t["index"])
                t_patch = padl+t["find"]+ending+padr
                r_patch = padl+t["repl"]+ending+padr
                if not dev in unique_patches:
                    unique_patches[dev] = []
                unique_patches[dev].append({
                    "dev":dev,
                    "remd":",".join([str(y) for y in set(t["remd"])]),
                    "orig":t["find"],
                    "find":t_patch,
                    "repl":r_patch
                })
        # Walk the unique patches if any
        if len(unique_patches):
            for x in unique_patches:
                for i,p in enumerate(unique_patches[x]):
                    patch_name = "{} IRQ {} Patch".format(x, p["remd"])
                    if len(unique_patches[x]) > 1:
                        patch_name += " - {} of {}".format(i+1, len(unique_patches[x]))
                    self.result.get("Patch").append({
                        "Comment": patch_name,
                        "Find": p["find"],
                        "Replace": p["repl"]
                    })
        # Walk the generic patches if any
        if len(generic_patches):
            generic_set = [] # Make sure we don't repeat find values
            for x in generic_patches:
                if x in generic_set:
                    continue
                generic_set.append(x)

            for i,x in enumerate(generic_set):
                patch_name = "Generic IRQ Patch {} of {} - {} - {}".format(i+1,len(generic_set),x["remd"],x["orig"])
                self.result.get("Patch").append({
                    "Comment": patch_name,
                    "Find": x["find"],
                    "Replace": x["repl"],
                    "Enabled": False
                })
        # Restore the original DSDT in memory
        self.dsdt["raw"] = saved_dsdt

        comment = "HPET Device Fake" if hpet_fake else "{} _CRS (Needs _CRS to XCRS Rename)".format(name.split(".")[-1].lstrip("\\"))
        ssdt_name = "SSDT-HPET"

        if hpet_fake:
            ssdt_content = """// Fake HPET device
//
DefinitionBlock ("", "SSDT", 2, "CORP", "HPET", 0x00000000)
{
    External ([[name]], DeviceObj)

    Scope ([[name]])
    {
        Device (HPET)
        {
            Name (_HID, EisaId ("PNP0103") /* HPET System Timer */)  // _HID: Hardware ID
            Name (_CID, EisaId ("PNP0C01") /* System Board */)  // _CID: Compatible ID
            Method (_STA, 0, NotSerialized)  // _STA: Status
            {
                If (_OSI ("Darwin"))
                {
                    Return (0x0F)
                }
                Else
                {
                    Return (Zero)
                }
            }
            Name (_CRS, ResourceTemplate ()  // _CRS: Current Resource Settings
            {
                IRQNoFlags ()
                    {0,8,11}
                Memory32Fixed (ReadWrite,
                    0xFED00000,         // Address Base
                    0x00000400,         // Address Length
                    )
            })
        }
    }
}""".replace("[[name]]",name)
        else:
            ssdt_content = """//
// Supplementary HPET _CRS from Goldfish64
// Requires the HPET's _CRS to XCRS rename
//
DefinitionBlock ("", "SSDT", 2, "CORP", "HPET", 0x00000000)
{
    External ([[name]], DeviceObj)
    External ([[name]].XCRS, [[type]])

    Scope ([[name]])
    {
        Name (BUFX, ResourceTemplate ()
        {
            IRQNoFlags ()
                {0,8,11}
            Memory32Fixed (ReadWrite,
                // [[mem]]
                [[mem_base]],         // Address Base
                [[mem_length]],         // Address Length
            )
        })
        Method (_CRS, 0, Serialized)  // _CRS: Current Resource Settings
        {
            // Return our buffer if booting macOS or the XCRS method
            // no longer exists for some reason
            If (LOr (_OSI ("Darwin"), LNot(CondRefOf ([[name]].XCRS))))
            {
                Return (BUFX)
            }
            // Not macOS and XCRS exists - return its result
            Return ([[name]].XCRS[[method]])
        }""" \
    .replace("[[name]]",name) \
    .replace("[[type]]","MethodObj" if hpet[0][-1] == "Method" else "BuffObj") \
    .replace("[[mem]]","Base/Length pulled from DSDT" if got_mem else "Default Base/Length - verify with your DSDT!") \
    .replace("[[mem_base]]",mem_base) \
    .replace("[[mem_length]]",mem_length) \
    .replace("[[method]]"," ()" if hpet[0][-1]=="Method" else "")
            if hpet_sta:
                # Inject our external reference to the renamed XSTA method
                ssdt_parts = []
                external = False
                for line in ssdt_content.split("\n"):
                    if "External (" in line: external = True
                    elif external:
                        ssdt_parts.append("    External ({}.XSTA, {})".format(name,sta["sta_type"]))
                        external = False
                    ssdt_parts.append(line)
                ssdt_content = "\n".join(ssdt_parts)
                # Add our method
                ssdt_content += """
        Method (_STA, 0, NotSerialized)  // _STA: Status
        {
            // Return 0x0F if booting macOS or the XSTA method
            // no longer exists for some reason
            If (LOr (_OSI ("Darwin"), LNot (CondRefOf ([[name]].XSTA))))
            {
                Return (0x0F)
            }
            // Not macOS and XSTA exists - return its result
            Return ([[name]].XSTA[[called]])
        }""".replace("[[name]]",name).replace("[[called]]"," ()" if sta["sta_type"]=="MethodObj" else "")
            ssdt_content += """
    }
}"""

        self.result["Add"].append({
            "Comment": comment,
            "Enabled": self.write_ssdt(ssdt_name, ssdt_content),
            "Path": ssdt_name + ".aml"
        })

    def fix_system_clock_awac(self, motherboard_chipset):
        if not self.utils.contains_any(chipset_data.IntelChipsets, motherboard_chipset, start=85):
            return
        
        rtc_range_needed = False
        rtc_crs_type = None
        crs_lines = []
        lpc_name = None
        awac_dict = self.get_sta_var(var="STAS",dev_hid="ACPI000E",dev_name="AWAC")
        rtc_dict = self.get_sta_var(var="STAS",dev_hid="PNP0B00",dev_name="RTC")
        # At this point - we should have any info about our AWAC and RTC devices
        # we need.  Let's see if we need an RTC fake - then build the SSDT.
        if not rtc_dict.get("valid"):
            #print(" - Fake needed!")
            lpc_name = self.get_lpc_name()
            if lpc_name is None:
                self.utils.request_input("Press [enter] to return to main menu...")
                return
        else:
            # Let's check if our RTC device has a _CRS variable - and if so, let's look for any skipped ranges
            #print(" --> Checking for _CRS...")
            rtc_crs = self.acpi.get_method_paths(rtc_dict["device"][0]+"._CRS") or self.acpi.get_name_paths(rtc_dict["device"][0]+"._CRS")
            if rtc_crs:
                #print(" ----> {}".format(rtc_crs[0][0]))
                rtc_crs_type = "MethodObj" if rtc_crs[0][-1] == "Method" else "BuffObj"
                # Only check for the range if it's a buffobj
                if rtc_crs_type.lower() == "buffobj":
                    last_adr = last_len = last_ind = None
                    crs_scope = self.acpi.get_scope(rtc_crs[0][1])
                    # Let's try and clean up the scope - it's often a jumbled mess
                    pad_len = len(crs_scope[0])-len(crs_scope[0].lstrip())
                    pad = crs_scope[0][:pad_len]
                    fixed_scope = []
                    for line in crs_scope:
                        if line.startswith(pad): # Got a full line - strip the pad, and save it
                            fixed_scope.append(line[pad_len:])
                        else: # Likely a part of the prior line
                            fixed_scope[-1] = fixed_scope[-1]+line
                    for i,line in enumerate(fixed_scope):
                        if "Name (_CRS, " in line:
                            # Rename _CRS to BUFX for later - and strip any comments to avoid confusion
                            line = line.replace("Name (_CRS, ","Name (BUFX, ").split("  //")[0]
                        if "IO (Decode16," in line:
                            # We have our start - get the the next line, and 4th line
                            try:
                                curr_adr = int(fixed_scope[i+1].strip().split(",")[0],16)
                                curr_len = int(fixed_scope[i+4].strip().split(",")[0],16)
                                curr_ind = i+4 # Save the value we may pad
                            except: # Bad values? Bail...
                                #print(" ----> Failed to gather values - could not verify RTC range.")
                                rtc_range_needed = False
                                break
                            if last_adr is not None: # Compare our range values
                                adjust = curr_adr - (last_adr + last_len)
                                if adjust: # We need to increment the previous length by our adjust value
                                    rtc_range_needed = True
                                    #print(" ----> Adjusting IO range {} length to {}".format(self.hexy(last_adr,pad_to=4),self.hexy(last_len+adjust,pad_to=2)))
                                    try:
                                        hex_find,hex_repl = self.hexy(last_len,pad_to=2),self.hexy(last_len+adjust,pad_to=2)
                                        crs_lines[last_ind] = crs_lines[last_ind].replace(hex_find,hex_repl)
                                    except:
                                        #print(" ----> Failed to adjust values - could not verify RTC range.")
                                        rtc_range_needed = False
                                        break
                            # Save our last values
                            last_adr,last_len,last_ind = curr_adr,curr_len,curr_ind
                        crs_lines.append(line)
                if rtc_range_needed: # We need to generate a rename for _CRS -> XCRS
                   # print(" --> Generating _CRS to XCRS rename...")
                    crs_index = self.acpi.find_next_hex(rtc_crs[0][1])[1]
                    #print(" ----> Found at index {}".format(crs_index))
                    crs_hex  = "5F435253" # _CRS
                    xcrs_hex = "58435253" # XCRS
                    padl,padr = self.acpi.get_shortest_unique_pad(crs_hex, crs_index)
                    patches = rtc_dict.get("patches",[])
                    patches.append({"Comment":"{} _CRS to XCRS Rename".format(rtc_dict["dev_name"]),"Find":padl+crs_hex+padr,"Replace":padl+xcrs_hex+padr})
                    rtc_dict["patches"] = patches
                    rtc_dict["crs"] = True
            else:
                pass
                #print(" ----> Not found")
        # Let's see if we even need an SSDT
        # Not required if AWAC is not present; RTC is present, doesn't have an STAS var, and doesn't have an _STA method, and no range fixes are needed
        if not awac_dict.get("valid") and rtc_dict.get("valid") and not rtc_dict.get("has_var") and not rtc_dict.get("sta") and not rtc_range_needed:
            #print("")
            #print("Valid PNP0B00 (RTC) device located and qualified, and no ACPI000E (AWAC) devices found.")
            #print("No patching or SSDT needed.")
            #print("")
            #self.utils.request_input("Press [enter] to return to main menu...")
            return
        comment = "Incompatible AWAC Fix" if awac_dict.get("valid") else "RTC Fake" if not rtc_dict.get("valid") else "RTC Range Fix" if rtc_range_needed else "RTC Enable Fix"
        suffix  = []
        for x in (awac_dict,rtc_dict):
            if not x.get("valid"): continue
            val = ""
            if x.get("sta") and not x.get("has_var"):
                val = "{} _STA to XSTA".format(x["dev_name"])
            if x.get("crs"):
                val += "{} _CRS to XCRS".format(" and " if val else x["dev_name"])
            if val: suffix.append(val)
        if suffix:
            comment += " - Requires {} Rename".format(", ".join(suffix))
        # At this point - we need to do the following:
        # 1. Change STAS if needed
        # 2. Setup _STA with _OSI and call XSTA if needed
        # 3. Fake RTC if needed

        ssdt_name = "SSDT-RTCAWAC"
        ssdt_content = """//
// Original sources from Acidanthera:
//  - https://github.com/acidanthera/OpenCorePkg/blob/master/Docs/AcpiSamples/SSDT-AWAC.dsl
//  - https://github.com/acidanthera/OpenCorePkg/blob/master/Docs/AcpiSamples/SSDT-RTC0.dsl
//
//
DefinitionBlock ("", "SSDT", 2, "ZPSS", "RTCAWAC", 0x00000000)
{
"""
        if any(x.get("has_var") for x in (awac_dict,rtc_dict)):
            ssdt_content += """    External (STAS, IntObj)
    Scope (\\)
    {
        Method (_INI, 0, NotSerialized)  // _INI: Initialize
        {
            If (_OSI ("Darwin"))
            {
                Store (One, STAS)
            }
        }
    }
"""
        for x in (awac_dict,rtc_dict):
            if not x.get("valid") or x.get("has_var") or not x.get("device"): continue
            # Device was found, and it doesn't have the STAS var - check if we
            # have an _STA (which would be renamed)
            macos,original = ("Zero","0x0F") if x.get("dev_hid") == "ACPI000E" else ("0x0F","Zero")
            if x.get("sta"):
                ssdt_content += """    External ([[DevPath]], DeviceObj)
    External ([[DevPath]].XSTA, [[sta_type]])
    Scope ([[DevPath]])
    {
        Name (ZSTA, [[Original]])
        Method (_STA, 0, NotSerialized)  // _STA: Status
        {
            If (_OSI ("Darwin"))
            {
                Return ([[macOS]])
            }
            // Default to [[Original]] - but return the result of the renamed XSTA if possible
            If (CondRefOf ([[DevPath]].XSTA))
            {
                Store ([[DevPath]].XSTA[[called]], ZSTA)
            }
            Return (ZSTA)
        }
    }
""".replace("[[DevPath]]",x["device"][0]).replace("[[Original]]",original).replace("[[macOS]]",macos).replace("[[sta_type]]",x["sta_type"]).replace("[[called]]"," ()" if x["sta_type"]=="MethodObj" else "")
            elif x.get("dev_hid") == "ACPI000E":
                # AWAC device with no STAS, and no _STA - let's just add one
                ssdt_content += """    External ([[DevPath]], DeviceObj)
    Scope ([[DevPath]])
    {
        Method (_STA, 0, NotSerialized)  // _STA: Status
        {
            If (_OSI ("Darwin"))
            {
                Return (Zero)
            }
            Else
            {
                Return (0x0F)
            }
        }
    }
""".replace("[[DevPath]]",x["device"][0])
        # Check if we need to setup an RTC range correction
        if rtc_range_needed and rtc_crs_type.lower() == "buffobj" and crs_lines and rtc_dict.get("valid"):
            ssdt_content += """    External ([[DevPath]], DeviceObj)
    External ([[DevPath]].XCRS, [[type]])
    Scope ([[DevPath]])
    {
        // Adjusted and renamed _CRS buffer ripped from DSDT with corrected range
[[NewCRS]]
        // End of adjusted _CRS and renamed buffer

        // Create a new _CRS method that returns the result of the renamed XCRS
        Method (_CRS, 0, Serialized)  // _CRS: Current Resource Settings
        {
            If (LOr (_OSI ("Darwin"), LNot (CondRefOf ([[DevPath]].XCRS))))
            {
                // Return our buffer if booting macOS or the XCRS method
                // no longer exists for some reason
                Return (BUFX)
            }
            // Not macOS and XCRS exists - return its result
            Return ([[DevPath]].XCRS[[method]])
        }
    }
""".replace("[[DevPath]]",rtc_dict["device"][0]) \
    .replace("[[type]]",rtc_crs_type) \
    .replace("[[method]]"," ()" if rtc_crs_type == "Method" else "") \
    .replace("[[NewCRS]]","\n".join([(" "*8)+x for x in crs_lines]))
        # Check if we do not have an RTC device at all
        if not rtc_dict.get("valid") and lpc_name:
            ssdt_content += """    External ([[LPCName]], DeviceObj)    // (from opcode)
    Scope ([[LPCName]])
    {
        Device (RTC0)
        {
            Name (_HID, EisaId ("PNP0B00"))  // _HID: Hardware ID
            Name (_CRS, ResourceTemplate ()  // _CRS: Current Resource Settings
            {
                IO (Decode16,
                    0x0070,             // Range Minimum
                    0x0070,             // Range Maximum
                    0x01,               // Alignment
                    0x08,               // Length
                    )
                IRQNoFlags ()
                    {8}
            })
            Method (_STA, 0, NotSerialized)  // _STA: Status
            {
                If (_OSI ("Darwin"))
                {
                    Return (0x0F)
                }
                Else
                {
                    Return (0)
                }
            }
        }
    }
""".replace("[[LPCName]]",lpc_name)
        ssdt_content += "}"
        
        if self.write_ssdt(ssdt_name, ssdt_content):
            self.result.get("Patch").extend(rtc_dict["patches"])
            self.result["Add"].append({
                "Comment": comment,
                "Enabled": True,
                "Path": ssdt_name + ".aml"
            })

    def fix_system_clock_hedt(self, motherboard_chipset, macos_version):
        if macos_version < 20 or not self.utils.contains_any(["X99", "X299"], motherboard_chipset):
            return
        
        if not self.lpc_bus_device:
            return

        awac_device = self.acpi.get_device_paths_with_hid("ACPI000E")
        rtc_device_name = self.acpi.get_device_paths_with_hid("PNP0B00")[0][0].split(".")[-1]

        comment = "Creates a new RTC device to resolve PCI Configuration issues in macOS Big Sur 11+"
        ssdt_name = "SSDT-RTC0-RANGE"
        ssdt_content = """
// Resource: https://github.com/acidanthera/OpenCorePkg/blob/master/Docs/AcpiSamples/Source/SSDT-RTC0-RANGE.dsl

/*
 * On certain motherboards(mainly Asus X299 boards), not all ports are
 * mapped in the RTC device. For the majority of the time, users will not notice 
 * this issue though in extreme circumstances macOS may halt in early booting.
 * Most prominently seen around the PCI Configuration stage with macOS 11 Big Sur.
 * 
 * To resolve this, we'll want to create a new RTC device(PNP0B00) with the correct
 * range.
 * 
 * Note that due to AWAC systems having an _STA method already defined, attempting
 * to set another _STA method in your RTC device will conflict. To resolve this,
 * SSDT-AWAC should be removed and instead opt for this SSDT instead.
 */
DefinitionBlock ("", "SSDT", 2, "ZPSS", "RtcRange", 0x00000000)
{
    External ([[LPCPath]], DeviceObj)"""
        if not awac_device:
            ssdt_content += """
    External ([[LPCPath]].[[RTCName]], DeviceObj)"""
            ssdt_content += """
    Scope ([[LPCPath]])
    {"""
        if not awac_device:
            ssdt_content += """
            Scope ([[RTCName]])
            {
                Method (_STA, 0, NotSerialized)  // _STA: Status
                {
                    If (_OSI ("Darwin"))
                    {
                        Return (Zero)
                    }
                    Else
                    {
                        Return (0x0F)
                    }
                }
            }""".replace("[[RTCName]]", rtc_device_name) 

        ssdt_content += """
        Device (RTC0)
        {
           /*
            * Change the below _CSR range to match your hardware.
            *
            * For this example, we'll use the Asus Strix X299-E Gaming's ACPI, and show how to correct it.
            * Within the original RTC device, we see that sections 0x70 through 0x77 are mapped:
            *
            *    Name (_CRS, ResourceTemplate ()  // _CRS: Current Resource Settings
            *    {
            *        IO (Decode16,
            *            0x0070,             // Range Minimum 1
            *            0x0070,             // Range Maximum 1
            *            0x01,               // Alignment 1
            *            0x02,               // Length 1
            *           )
            *        IO (Decode16,
            *            0x0074,             // Range Minimum 2
            *            0x0074,             // Range Maximum 2
            *            0x01,               // Alignment 2
            *            0x04,               // Length 2
            *           )
            *        IRQNoFlags ()
            *            {8}
            *    })
            *
            * Though Asus seems to have forgotten to map sections 0x72 and 0x73 in the first bank, so
            * we'll want to expand the range to include them under Length 1.
            * Note that not all boards will be the same, verify with your ACPI tables for both the range and 
            * missing regions.
            */
            
            Name (_HID, EisaId ("PNP0B00"))  // _HID: Hardware ID
            Name (_CRS, ResourceTemplate ()  // _CRS: Current Resource Settings
            {
                IO (Decode16,
                    0x0070,             // Range Minimum 1
                    0x0070,             // Range Maximum 1
                    0x01,               // Alignment 1
                    0x04,               // Length 1      (Expanded to include 0x72 and 0x73)
                    )
                IO (Decode16,
                    0x0074,             // Range Minimum 2
                    0x0074,             // Range Maximum 2
                    0x01,               // Alignment 2
                    0x04,               // Length 2
                    )
                IRQNoFlags ()
                    {8}
            })
            Method (_STA, 0, NotSerialized)  // _STA: Status
            {
                If (_OSI ("Darwin"))
                {
                    Return (0x0F)
                }
                Else
                {
                    Return (Zero)
                }
            }
        }
    }
}"""
        
        ssdt_content = ssdt_content.replace("[[LPCPath]]", self.lpc_bus_device).replace("[[RTCName]]", rtc_device_name)
        self.result["Add"].append({
            "Comment": comment,
            "Enabled": self.write_ssdt(ssdt_name, ssdt_content),
            "Path": ssdt_name + ".aml"
        })

    def instant_wake_fix(self):        
        comment = "Fix sleep state values in _PRW methods to prevent immediate wake in macOS"
        ssdt_name = "SSDT-PRW"

        uswe_object = "9355535745"
        wole_object = "93574F4C45"
        gprw_method = "4750525702"
        uprw_method = "5550525702"
        xprw_method = "5850525702"

        if binascii.unhexlify(gprw_method) in self.dsdt.get("raw"):
            self.result.get("Patch").append({
                "Comment": "GPRW to XPRW Rename",
                "Find": gprw_method,
                "Replace": xprw_method
            })
        if binascii.unhexlify(uprw_method) in self.dsdt.get("raw"):
            self.result.get("Patch").append({
                "Comment": "UPRW to XPRW Rename",
                "Find": uprw_method,
                "Replace": xprw_method
            })
        if not binascii.unhexlify(uswe_object) in self.dsdt.get("raw"):
            uswe_object = None
        if not binascii.unhexlify(wole_object) in self.dsdt.get("raw"):
            wole_object = None
        
        ssdt_content = """
// Resource: https://github.com/5T33Z0/OC-Little-Translated/blob/main/04_Fixing_Sleep_and_Wake_Issues/060D_Instant_Wake_Fix/README.md

DefinitionBlock ("", "SSDT", 2, "ZPSS", "_PRW", 0x00000000)
{"""
        if binascii.unhexlify(gprw_method[2:]) in self.dsdt.get("raw"):
            ssdt_content += """\n    External(XPRW, MethodObj)"""
        if uswe_object:
            ssdt_content += "\n    External (USWE, FieldUnitObj)"
        if wole_object:
            ssdt_content += "\n    External (WOLE, FieldUnitObj)"
        if uswe_object or wole_object:
            ssdt_content += """\n
    Scope (\\)
    {
        If (_OSI ("Darwin"))
        {"""
            if uswe_object:
                ssdt_content += "\n            USWE = Zero"
            if wole_object:
                ssdt_content += "\n            WOLE = Zero"
            ssdt_content += """        }
    }"""
        if binascii.unhexlify(gprw_method) in self.dsdt.get("raw"):
            ssdt_content += """
    Method (GPRW, 2, NotSerialized)
    {
        If (_OSI ("Darwin"))
        {
            If ((0x6D == Arg0))
            {
                Return (Package ()
                {
                    0x6D, 
                    Zero
                })
            }

            If ((0x0D == Arg0))
            {
                Return (Package ()
                {
                    0x0D, 
                    Zero
                })
            }
        }
        Return (XPRW (Arg0, Arg1))
    }"""
        if binascii.unhexlify(uprw_method) in self.dsdt.get("raw"):
            ssdt_content += """
    Method (UPRW, 2, NotSerialized)
    {
        If (_OSI ("Darwin"))
        {
            If ((0x6D == Arg0))
            {
                Return (Package ()
                {
                    0x6D, 
                    Zero
                })
            }

            If ((0x0D == Arg0))
            {
                Return (Package ()
                {
                    0x0D, 
                    Zero
                })
            }
        }
        Return (XPRW (Arg0, Arg1))
    }"""
        ssdt_content += "\n}"
        self.result["Add"].append({
            "Comment": comment,
            "Enabled": self.write_ssdt(ssdt_name, ssdt_content),
            "Path": ssdt_name + ".aml"
        })

    def fix_uncore_bridge(self, motherboard_chipset, macos_version):
        if macos_version < 20 or not self.utils.contains_any(["X79", "C602", "Patsburg", "C612", "X99", "Wellsburg"], motherboard_chipset):
            return
        
        unc0_device = self.acpi.get_device_paths("UNC0")

        if not unc0_device:
            return
        
        comment = "Disables unused uncore bridges to prevent kenel panic in macOS Big Sur 11+"
        ssdt_name = "SSDT-UNC"
        ssdt_content = """
// Resource: https://github.com/acidanthera/OpenCorePkg/blob/master/Docs/AcpiSamples/Source/SSDT-UNC.dsl

/*
 * Discovered on X99-series.
 * These platforms have uncore PCI bridges for 4 CPU sockets
 * present in ACPI despite having none physically.
 *
 * Under normal conditions these are disabled depending on
 * CPU presence in the socket via Processor Bit Mask (PRBM),
 * but on X99 this code is unused or broken as such bridges
 * simply do not exist. We fix that by writing 0 to PRBM.
 *
 * Doing so is important as starting with macOS 11 IOPCIFamily
 * will crash as soon as it sees non-existent PCI bridges.
 */

DefinitionBlock ("", "SSDT", 2, "ZPSS", "UNC", 0x00000000)
{
    External (_SB.UNC0, DeviceObj)
    External (PRBM, IntObj)

    Scope (_SB.UNC0)
    {
        Method (_INI, 0, NotSerialized)
        {
            // In most cases this patch does benefit all operating systems,
            // yet on select pre-Windows 10 it may cause issues.
            // Remove If (_OSI ("Darwin")) in case you have none.
            If (_OSI ("Darwin")) {
                PRBM = 0
            }
        }
    }
}"""

        self.result["Add"].append({
            "Comment": comment,
            "Enabled": self.write_ssdt(ssdt_name, ssdt_content),
            "Path": ssdt_name + ".aml"
        })

    def operating_system_patch(self, platform):
        if not "Laptop" in platform:
            return
        
        comment = "Spoofs the operating system to Windows, enabling devices locked behind non-Windows systems on macOS"
        ssdt_name = "SSDT-XOSI"
        ssdt_content = """
// Resource: https://github.com/dortania/Getting-Started-With-ACPI/blob/master/extra-files/decompiled/SSDT-XOSI.dsl

DefinitionBlock ("", "SSDT", 2, "ZPSS", "XOSI", 0x00001000)
{
    Method (XOSI, 1, NotSerialized)
    {
        // Based off of: 
        // https://docs.microsoft.com/en-us/windows-hardware/drivers/acpi/winacpi-osi#_osi-strings-for-windows-operating-systems
        // Add OSes from the below list as needed, most only check up to Windows 2015
        // but check what your DSDT looks for
        Store (Package ()
        {
[[OSIStrings]]
        }, Local0)
        If (_OSI ("Darwin"))
        {
            Return (LNotEqual (Match (Local0, MEQ, Arg0, MTR, Zero, Zero), Ones))
        }
        Else
        {
            Return (_OSI (Arg0))
        }
    }
}""".replace("[[OSIStrings]]", "\n,".join(["            \"{}\"".format(osi_string) for target_os, osi_string in self.osi_strings.items() if osi_string in self.dsdt.get("table")]))

        osid = self.acpi.get_method_paths("OSID")
        if osid:
            self.result.get("Patch").append({
                "Comment": "OSID to XSID rename - must come before _OSI to XOSI rename!",
                "Find": "4F534944",
                "Replace": "58534944"
            })

        osif = self.acpi.get_method_paths("OSIF")
        if osif:
            self.result.get("Patch").append({
                "Comment": "OSIF to XSIF rename - must come before _OSI to XOSI rename!",
                "Find": "4F534946",
                "Replace": "58534946"
            })

        self.result.get("Patch").append({
            "Comment": "_OSI to XOSI rename - requires SSDT-XOSI.aml",
            "Find": "5F4F5349",
            "Replace": "584F5349"
        })
        
        self.result["Add"].append({
            "Comment": comment,
            "Enabled": self.write_ssdt(ssdt_name, ssdt_content),
            "Path": ssdt_name + ".aml"
        })

    def surface_laptop_special_patch(self, motherboard_name, platform):
        if "Surface".upper() not in motherboard_name or "Laptop" not in platform:
            return

        comment = "Special Patch for all Surface Pro / Book / Laptop hardwares"
        ssdt_name = "SSDT-SURFACE"
        ssdt_content = """
DefinitionBlock ("", "SSDT", 2, "ZPSS", "Surface", 0x00001000)
{
    External (_SB_.PCI0, DeviceObj)
    External (GPRW, MethodObj)    // 2 Arguments

    If (_OSI ("Darwin"))
    {
        Scope (_SB)
        {
            Device (ALS0)
            {
                Name (_HID, "ACPI0008" /* Ambient Light Sensor Device */)  // _HID: Hardware ID
                Name (_CID, "smc-als")  // _CID: Compatible ID
                Name (_ALI, 0x012C)  // _ALI: Ambient Light Illuminance
                Name (_ALR, Package (0x05)  // _ALR: Ambient Light Response
                {
                    Package (0x02)
                    {
                        0x46, 
                        Zero
                    }, 

                    Package (0x02)
                    {
                        0x49, 
                        0x0A
                    }, 

                    Package (0x02)
                    {
                        0x55, 
                        0x50
                    }, 

                    Package (0x02)
                    {
                        0x64, 
                        0x012C
                    }, 

                    Package (0x02)
                    {
                        0x96, 
                        0x03E8
                    }
                })
                Method (XALI, 1, Serialized)
                {
                    _ALI = Arg0
                }
            }

            Device (ADP0)
            {
                Name (_HID, "ACPI0003" /* Power Source Device */)  // _HID: Hardware ID
                Name (SPSR, Zero)
                Method (_PRW, 0, NotSerialized)  // _PRW: Power Resources for Wake
                {
                    Return (GPRW (0x6D, 0x04))
                }

                Method (_STA, 0, NotSerialized)  // _STA: Status
                {
                    Return (0x0F)
                }

                Method (XPSR, 1, Serialized)
                {
                    If ((Arg0 == Zero))
                    {
                        SPSR = Zero
                    }
                    ElseIf ((Arg0 == One))
                    {
                        SPSR = One
                    }

                    Notify (ADP0, 0x80) // Status Change
                }

                Method (_PSR, 0, Serialized)  // _PSR: Power Source
                {
                    Return (SPSR) /* \\_SB_.ADP0.SPSR */
                }

                Method (_PCL, 0, NotSerialized)  // _PCL: Power Consumer List
                {
                    Return (\\_SB)
                }
            }

            Device (BAT0)
            {
                Name (_HID, EisaId ("PNP0C0A") /* Control Method Battery */)  // _HID: Hardware ID
                Name (_UID, Zero)  // _UID: Unique ID
                Name (_PCL, Package (0x01)  // _PCL: Power Consumer List
                {
                    _SB
                })
                Method (_STA, 0, NotSerialized)  // _STA: Status
                {
                    Return (0x1F)
                }
            }
        }

        Scope (_SB.PCI0)
        {
            Device (IPTS)
            {
                Name (_ADR, 0x00160004)  // _ADR: Address
            }
        }
    }
}""" 

        self.result["Add"].append({
            "Comment": comment,
            "Enabled": self.write_ssdt(ssdt_name, ssdt_content),
            "Path": ssdt_name + ".aml"
        })

    def battery_status_check(self, platform):
        if "Laptop" not in platform:
            return
        
        if not self.dsdt:
            self.result["Battery Status Patch Needed"] = True
            return

        search_start_idx = 0

        while "EmbeddedControl" in self.dsdt.get("table")[search_start_idx:]:
            emb_ctrl_start_idx = self.dsdt.get("table").index("EmbeddedControl", search_start_idx)
            emb_ctrl_end_idx = emb_ctrl_start_idx + self.dsdt.get("table")[emb_ctrl_start_idx:].index("}")
            emb_ctrl_block = self.dsdt.get("table")[emb_ctrl_start_idx:emb_ctrl_end_idx]

            for line in emb_ctrl_block.splitlines():
                if ",   " in line and ",   8" not in line:
                    self.result["Battery Status Patch Needed"] = True
                    return 

            search_start_idx = emb_ctrl_end_idx

        return

    def select_dsdt(self):
        results_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "Results")
        apcidump_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "acpidump.exe")
        while True:
            self.utils.head("Select ACPI Tables")
            print("")
            if sys.platform == "win32":
                print("To manually dump ACPI tables, open Command Prompt and enter the following commands in sequence:")
                print("")
                print("  > cd \"{}\"".format(results_path.replace("/", "\\")))
                print("  > mkdir ACPITables")
                print("  > cd ACPITables")
                print("  > \"{}\" -b".format(apcidump_path.replace("/", "\\")))
                print("  > rename *.dat *.aml")
                print("")
                print("The ACPI tables will now be available in\n  \"{}\\ACPITables\"".format(results_path.replace("/", "\\")))
                print("")
            if sys.platform.startswith("linux") or sys.platform == "win32":
                print("P. Dump ACPI Tables")
            print("Q. Quit")
            print(" ")
            menu = self.utils.request_input("Please drag and drop ACPI Tables folder here: ")
            if menu.lower() == "p" and (sys.platform.startswith("linux") or sys.platform == "win32"):
                return self.read_dsdt(
                    self.acpi.dump_tables(os.path.join(results_path, "ACPITables"))
                )
            elif menu.lower() == "q":
                self.utils.exit_program()
            path = self.utils.normalize_path(menu)
            if not path: 
                continue
            return self.read_dsdt(path)
        
    def add_dtgp_method(self):
        comment = "Enables macOS to read and merge device properties from ACPI and determine if a specific device should temporarily receive power"
        ssdt_name = "SSDT-DTGP"
        ssdt_content = """
// Resource: https://github.com/5T33Z0/OC-Little-Translated/blob/main/01_Adding_missing_Devices_and_enabling_Features/Method_DTGP/SSDT-DTGP.dsl

DefinitionBlock ("", "SSDT", 2, "ZPSS", "DTGP", 0x00001000)
{
    Method (DTGP, 5, NotSerialized)
    {
        If ((Arg0 == ToUUID ("a0b5b7c6-1318-441c-b0c9-fe695eaf949b") /* Unknown UUID */))
        {
            If ((Arg1 == One))
            {
                If ((Arg2 == Zero))
                {
                    Arg4 = Buffer (One)
                        {
                             0x03                                             // .
                        }
                    Return (One)
                }

                If ((Arg2 == One))
                {
                    Return (One)
                }
            }
        }

        Arg4 = Buffer (One)
            {
                 0x00                                             // .
            }
        Return (Zero)
    }
}
"""

        self.result["Add"].append({
            "Comment": comment,
            "Enabled": self.write_ssdt(ssdt_name, ssdt_content),
            "Path": ssdt_name + ".aml"
        })

    def spoof_discrete_gpu(self, discrete_gpu):
        device_id = discrete_gpu.get("Device ID")

        if not device_id in pci_data.SpoofGPUIDs:
            return
        
        self.add_dtgp_method()
        new_device_id_le = self.utils.to_little_endian_hex(pci_data.SpoofGPUIDs.get(device_id).split("-")[-1])
        device_id_byte = ", ".join([f'0x{new_device_id_le[i:i+2]}' for i in range(0, len(new_device_id_le), 2)])
        comment = "Spoof GPU ID to enable graphics acceleration in macOS"
        ssdt_name = "SSDT-GPU-SPOOF"
        ssdt_content = """
// Resource: https://github.com/dortania/Getting-Started-With-ACPI/blob/master/extra-files/decompiled/SSDT-GPU-SPOOF.dsl

// Replace all "_SB.PCI0.PEG0.PEGP" with the ACPI path of your discrete GPU

DefinitionBlock ("", "SSDT", 2, "ZPSS", "GPUSPOOF", 0x00001000)
{
    External (_SB.PCI0.PEG0.PEGP, DeviceObj)
    External (DTGP, MethodObj)

    Scope (_SB.PCI0.PEG0.PEGP)
    {
        if (_OSI ("Darwin"))
        {
            Method (_DSM, 4, NotSerialized)  // _DSM: Device-Specific Method
            {
                Local0 = Package (0x04)
                {
                    "device-id",
                    Buffer (0x04)
                    {
                        [[DeviceID]]
                    },

                    "model",
                    Buffer ()
                    {
                        "[[model]]"
                    }
                }
                DTGP (Arg0, Arg1, Arg2, Arg3, RefOf (Local0))
                Return (Local0)
            }
        }
    }
}""".replace("[[DeviceID]]", device_id_byte).replace("[[model]]", discrete_gpu.get("GPU Name"))

        self.result["Add"].append({
            "Comment": comment,
            "Enabled": self.write_ssdt(ssdt_name, ssdt_content, compile=False),
            "Path": ssdt_name + ".aml"
        })

    def dropping_the_table(self, signature=None, oemtableid=None):
        table_data = self.acpi.get_table_with_signature(signature) or self.acpi.get_table_with_id(oemtableid)

        if not table_data:
            return
                
        self.result["Delete"].append({
            "All": True,
            "Comment": "Delete {}".format(signature or oemtableid),
            "Enabled": True,
            "OemTableId": self.utils.hex_to_bytes(self.utils.string_to_hex(table_data.get("id"))),
            "TableLength": 0,
            "TableSignature": self.utils.hex_to_bytes(self.utils.string_to_hex(table_data.get("signature")))
        })

    def fix_apic_processor_id(self, cpu_codename):
        self.apic = self.acpi.get_table_with_signature("APIC")
        processors = [line for line in self.dsdt.get("lines") if line.strip().startswith("Processor")]

        if not self.is_intel_hedt_cpu(cpu_codename) or not self.apic or not processors:
            return

        processor_index = -1
        for index, line in enumerate(self.apic.get("lines")):
            if "Subtable Type" in line and "[Processor Local APIC]" in line:
                processor_index += 1
                apic_processor_id = self.apic["lines"][index + 2][-2:]
                try:
                    dsdt_processor_id = processors[processor_index].split("0x")[1].split(",")[0]
                except:
                    return
                if processor_index == 0 and apic_processor_id == dsdt_processor_id:
                    break
                self.apic["lines"][index + 2] = self.apic["lines"][index + 2][:-2] + dsdt_processor_id

        if processor_index != -1:
            if self.write_ssdt("APIC", "\n".join(self.apic.get("lines"))):
                self.result["Add"].append({
                    "Comment": "Avoid kernel panic by pointing the first CPU entry to an active CPU on HEDT systems",
                    "Enabled": True,
                    "Path": "APIC.aml"
                })
                self.dropping_the_table("APIC")

    def initialize_patches(self, motherboard_name, motherboard_chipset, platform, cpu_manufacturer, cpu_codename, integrated_gpu, discrete_gpu, ethernet_pci, touchpad_communication, smbios, intel_mei, unsupported_devices, macos_version, acpi_directory):
        self.acpi_directory = self.check_acpi_directory(acpi_directory)

        if self.select_dsdt():
            self.dsdt = self.acpi.get_dsdt_or_only()
            self.get_low_pin_count_bus_device()
            self.add_intel_management_engine(cpu_codename, intel_mei)
            self.add_memory_controller_device(cpu_manufacturer, cpu_codename, smbios)
            self.add_null_ethernet_device(ethernet_pci)
            self.add_system_management_bus_device(cpu_manufacturer, cpu_codename)
            self.add_usb_power_properties(smbios)
            self.ambient_light_sensor(motherboard_name, platform, integrated_gpu)
            self.battery_status_check(platform)
            self.disable_rhub_devices()
            self.disable_unsupported_device(unsupported_devices)
            if not self.is_intel_hedt_cpu(cpu_codename) and self.utils.contains_any(cpu_data.IntelCPUGenerations, cpu_codename, end=2):
                self.dropping_the_table(oemtableid="CpuPm")
                self.dropping_the_table(oemtableid="Cpu0Ist")
            self.enable_backlight_controls(platform, cpu_codename, integrated_gpu)
            self.enable_cpu_power_management(cpu_codename)
            self.enable_gpio_device(platform, cpu_manufacturer, touchpad_communication)
            self.enable_nvram_support(motherboard_chipset)
            self.fake_embedded_controller(platform)
            self.fix_apic_processor_id(cpu_codename)
            self.fix_hp_005_post_error(motherboard_name)
            self.fix_irq_conflicts(platform, cpu_codename)
            self.fix_system_clock_awac(motherboard_chipset)
            self.fix_system_clock_hedt(motherboard_chipset, macos_version)
            self.fix_uncore_bridge(motherboard_chipset, macos_version)
            self.instant_wake_fix()
            self.operating_system_patch(platform)
            self.spoof_discrete_gpu(discrete_gpu)
            self.surface_laptop_special_patch(motherboard_name, platform)

        self.result["Add"] = sorted(self.result["Add"], key=lambda x: x["Path"])
        self.apply_acpi_patches()
        return self.result
