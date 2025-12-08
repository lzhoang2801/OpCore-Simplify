"""
Data models for OpCore Simplify GUI.
Provides structured data containers for better type safety and code clarity.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any


@dataclass
class HardwareReportState:
    """State management for hardware report data."""
    path: str = "Not selected"
    data: Optional[Dict[str, Any]] = None
    hardware_report: Optional[Dict[str, Any]] = None
    customized_hardware: Optional[Dict[str, Any]] = None
    disabled_devices: Optional[Dict[str, str]] = None
    disabled_devices_text: str = "None"
    
    
@dataclass
class MacOSVersionState:
    """State management for macOS version selection."""
    version_text: str = "Not selected"
    version_darwin: str = ""  # Darwin version format (e.g., "22.0.0")
    native_version: Optional[tuple] = None
    ocl_patched_version: Optional[tuple] = None
    needs_oclp: bool = False


@dataclass
class SMBIOSState:
    """State management for SMBIOS configuration."""
    model_text: str = "Not selected"


@dataclass
class BuildState:
    """State management for build process."""
    in_progress: bool = False
    successful: bool = False
    log_messages: List[str] = field(default_factory=list)


@dataclass
class GUICallbacks:
    """Container for GUI callback functions."""
    prompt_handler: Any  # Callable
    progress_handler: Any  # Callable
    gathering_progress_handler: Any  # Callable
    log_handler: Any  # Callable
    folder_selector: Any  # Callable
