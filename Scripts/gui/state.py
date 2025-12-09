from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any


@dataclass
class HardwareReportState:
    report_path: str = "Not selected"
    acpi_dir: str = "Not selected"
    hardware_report: Optional[Dict[str, Any]] = None
    compatibility_error: Optional[str] = None
    customized_hardware: Optional[Dict[str, Any]] = None
    disabled_devices: Optional[Dict[str, str]] = None
    disabled_devices_text: str = "None"
    
    
@dataclass
class MacOSVersionState:
    version_text: str = "Not selected"
    version_darwin: str = ""
    native_version: Optional[tuple] = None
    ocl_patched_version: Optional[tuple] = None
    needs_oclp: bool = False


@dataclass
class SMBIOSState:
    model_text: str = "Not selected"


@dataclass
class BuildState:
    in_progress: bool = False
    successful: bool = False
    log_messages: List[str] = field(default_factory=list)