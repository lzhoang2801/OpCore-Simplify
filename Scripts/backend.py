import os
import sys
import logging
from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal

from Scripts import acpi_guru
from Scripts import compatibility_checker
from Scripts import config_prodigy
from Scripts import gathering_files
from Scripts import hardware_customizer
from Scripts import kext_maestro
from Scripts import report_validator
from Scripts import run
from Scripts import smbios
from Scripts import settings
from Scripts import utils
from Scripts import integrity_checker
from Scripts import resource_fetcher
from Scripts import github
from Scripts import wifi_profile_extractor
from Scripts import dsdt

class LogSignalHandler(logging.Handler):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def emit(self, record):
        msg = self.format(record)
        to_build_log = getattr(record, "to_build_log", False)
        self.signal.emit(msg, record.levelname, to_build_log)

class Backend(QObject):
    log_message_signal = pyqtSignal(str, str, bool)
    update_status_signal = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        
        self.u = utils.Utils()
        self.settings = settings.Settings(utils_instance=self.u)
        self.log_file_path = None
        
        self._setup_logging()
        self.u.clean_temporary_dir()
        
        self.integrity_checker = integrity_checker.IntegrityChecker(utils_instance=self.u)
        
        self.resource_fetcher = resource_fetcher.ResourceFetcher(
            utils_instance=self.u,
            integrity_checker_instance=self.integrity_checker
        )
        self.github = github.Github(
            utils_instance=self.u,
            resource_fetcher_instance=self.resource_fetcher
        )
        
        self.r = run.Run()
        self.wifi_extractor = wifi_profile_extractor.WifiProfileExtractor(
            run_instance=self.r,
            utils_instance=self.u
        )
        self.k = kext_maestro.KextMaestro(utils_instance=self.u)
        self.c = compatibility_checker.CompatibilityChecker(
            utils_instance=self.u,
            settings_instance=self.settings
        )
        self.h = hardware_customizer.HardwareCustomizer(utils_instance=self.u)
        self.v = report_validator.ReportValidator(utils_instance=self.u)
        self.dsdt = dsdt.DSDT(
            utils_instance=self.u,
            github_instance=self.github,
            resource_fetcher_instance=self.resource_fetcher,
            run_instance=self.r
        )
        
        self.o = gathering_files.gatheringFiles(
            utils_instance=self.u,
            github_instance=self.github,
            kext_maestro_instance=self.k,
            integrity_checker_instance=self.integrity_checker,
            resource_fetcher_instance=self.resource_fetcher
        )
        
        self.s = smbios.SMBIOS(
            gathering_files_instance=self.o,
            run_instance=self.r,
            utils_instance=self.u,
            settings_instance=self.settings
        )
        
        self.ac = acpi_guru.ACPIGuru(
            dsdt_instance=self.dsdt,
            smbios_instance=self.s,
            run_instance=self.r,
            utils_instance=self.u
        )
        
        self.co = config_prodigy.ConfigProdigy(
            gathering_files_instance=self.o,
            smbios_instance=self.s,
            utils_instance=self.u
        )
        
        custom_output_dir = self.settings.get_build_output_directory()
        if custom_output_dir:
            self.result_dir = self.u.create_folder(custom_output_dir, remove_content=True)
        else:
            self.result_dir = self.u.get_temporary_dir()

    def _setup_logging(self):
        logger = logging.getLogger("OpCoreSimplify")
        logger.setLevel(logging.DEBUG)
        
        logger.handlers = []

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(stream_handler)

        signal_handler = LogSignalHandler(self.log_message_signal)
        signal_handler.setLevel(logging.DEBUG)
        signal_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(signal_handler)

        if self.settings.get_enable_debug_logging():
            try:
                log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logs")
                os.makedirs(log_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
                self.log_file_path = os.path.join(log_dir, "ocs-{}.txt".format(timestamp))
                file_handler = logging.FileHandler(self.log_file_path, encoding="utf-8")
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"))
                logger.addHandler(file_handler)
            except Exception as e:
                print("Failed to setup file logging: {}".format(e))