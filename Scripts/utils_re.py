from urllib.parse import urlparse

# Central list of trusted repositories
TRUSTED_REPOS = {
    "https://github.com/acidanthera/Lilu",
    "https://github.com/acidanthera/VirtualSMC",
    "https://github.com/acidanthera/WhateverGreen",
    "https://github.com/acidanthera/AppleALC",
    "https://nightly.link/ChefKissInc/SMCRadeonSensors/workflows/main/master/Artifacts.zip",
    "https://nightly.link/ChefKissInc/NootRX/workflows/main/master/Artifacts.zip",
    "https://nightly.link/ChefKissInc/NootedRed/workflows/main/master/Artifacts.zip",
    "https://github.com/dortania/OpenCore-Legacy-Patcher/raw/refs/heads/main/payloads/Kexts/Wifi/corecaptureElCap-v1.0.2.zip",
    "https://github.com/dortania/OpenCore-Legacy-Patcher",
    "https://github.com/dortania/OpenCore-Legacy-Patcher/raw/refs/heads/main/payloads/Kexts/Wifi/IO80211ElCap-v2.0.1.zip",
    "https://github.com/dortania/OpenCore-Legacy-Patcher",
    "https://github.com/dortania/OpenCore-Legacy-Patcher/raw/main/payloads/Kexts/Wifi/IO80211FamilyLegacy-v1.0.0.zip",
    "https://github.com/dortania/OpenCore-Legacy-Patcher/raw/main/payloads/Kexts/Wifi/IOSkywalkFamily-v1.2.0.zip",
    "https://github.com/lzhoang2801/lzhoang2801.github.io/raw/main/public/extra-files/AppleIGB-v5.11.4.zip",
    "https://github.com/dortania/OpenCore-Legacy-Patcher/raw/refs/heads/main/payloads/Kexts/Ethernet/CatalinaBCM5701Ethernet-v1.0.2.zip",
    "https://github.com/TomHeaven/HoRNDIS/releases/download/rel9.3_2/Release.zip",
    "https://bitbucket.org/RehabMan/os-x-null-ethernet/downloads/RehabMan-NullEthernet-2016-1220.zip",
    "https://github.com/lzhoang2801/lzhoang2801.github.io/raw/main/public/extra-files/RealtekRTL8100-v2.0.1.zip",
    "https://github.com/Mieze/RTL8111_driver_for_OS_X/releases/download/2.4.2/RealtekRTL8111-V2.4.2.zip",
    "https://github.com/daliansky/OS-X-USB-Inject-All/releases/download/v0.8.0/XHCI-unsupported.kext.zip",
    "https://raw.githubusercontent.com/lzhoang2801/lzhoang2801.github.io/refs/heads/main/public/extra-files/CtlnaAHCIPort-v3.4.1.zip",
    "https://raw.githubusercontent.com/lzhoang2801/lzhoang2801.github.io/refs/heads/main/public/extra-files/SATA-unsupported-v0.9.2.zip",
    "https://github.com/lzhoang2801/lzhoang2801.github.io/raw/refs/heads/main/public/extra-files/VoodooTSCSync-v1.1.zip",
    "https://nightly.link/ChefKissInc/ForgedInvariant/workflows/main/master/Artifacts.zip",
    "https://github.com/dortania/OpenCore-Legacy-Patcher/raw/main/payloads/Kexts/Acidanthera/AMFIPass-v1.4.1-RELEASE.zip",
    "https://github.com/dortania/OpenCore-Legacy-Patcher/raw/refs/heads/main/payloads/Kexts/Misc/ASPP-Override-v1.0.1.zip",
    "https://github.com/dortania/OpenCore-Legacy-Patcher/raw/refs/heads/main/payloads/Kexts/Misc/AppleIntelCPUPowerManagement-v1.0.0.zip",
    "https://github.com/dortania/OpenCore-Legacy-Patcher/raw/refs/heads/main/payloads/Kexts/Misc/AppleIntelCPUPowerManagementClient-v1.0.0.zip",
    "https://github.com/acidanthera/bugtracker/files/3703498/AppleMCEReporterDisabler.kext.zip",   
}

class RepoError(Exception):
    pass

def is_trusted_repo(url: str) -> None:
    """Check if a given URL belongs to a trusted GitHub repo."""
    parsed = urlparse(url)
    # Normalize to scheme + netloc + first two path segments
    repo_url = f"https://{parsed.netloc}{'/'.join(parsed.path.split('/')[:3])}"
    if repo_url not in TRUSTED_REPOS:
        raise RepoError(f"Untrusted repository: {url}")
