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
    
    
@dataclass
class MacOSVersionState:
    macos_version_name: str = "Not selected"
    darwin_version: str = ""
    native_version: Optional[tuple] = None
    ocl_patched_version: Optional[tuple] = None
    needs_oclp: bool = False


@dataclass
class SMBIOSState:
    model_name: str = "Not selected"


@dataclass
class BuildState:
    in_progress: bool = False
    successful: bool = False
    log_messages: List[str] = field(default_factory=list)