"""
GUI pages package - qfluentwidgets version
"""

from .home_page import HomePage
from .upload_page import UploadPage
from .compatibility_page import CompatibilityPage
from .configuration_page import ConfigurationPage
from .build_page import BuildPage
from .console_page import ConsolePage
from .settings_page import SettingsPage
from .config_editor_page import ConfigEditorPage

__all__ = [
    'HomePage',
    'UploadPage',
    'CompatibilityPage',
    'ConfigurationPage',
    'BuildPage',
    'ConsolePage',
    'SettingsPage',
    'ConfigEditorPage',
]
