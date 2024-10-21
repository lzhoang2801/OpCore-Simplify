class PatchInfo:
    def __init__(self, name, description, function_name):
        self.name = name
        self.description = description
        self.function_name = function_name
        self.checked = False

patches = [
    PatchInfo(
        name = "ALS",
        description = "Fake or enable Ambient Light Sensor device for storing the current brightness/auto-brightness level",
        function_name = "ambient_light_sensor"
    ),
    PatchInfo(
        name = "APIC",
        description = "Avoid kernel panic by pointing the first CPU entry to an active CPU on HEDT systems",
        function_name = "fix_apic_processor_id"
    ),
    PatchInfo(
        name = "BATP",
        description = "Enables displaying the battery percentage on laptops",
        function_name = "battery_status_patch"
    ),
    PatchInfo(
        name = "BUS0",
        description = "Add a System Management Bus device to fix AppleSMBus issues",
        function_name = "add_system_management_bus_device"
    ),
    PatchInfo(
        name = "Disable Devices",
        description = "Disable unsupported PCI devices such as the GPU, Wi-Fi card, and SD card reader",
        function_name = "disable_unsupported_device"
    ),
    PatchInfo(
        name = "FakeEC",
        description = "OS-Aware Fake EC (by CorpNewt)",
        function_name = "fake_embedded_controller"
    ),
    PatchInfo(
        name = "CMOS",
        description = "Fix HP Real-Time Clock Power Loss (005) Post Error",
        function_name = "fix_hp_005_post_error"
    ),
    PatchInfo(
        name = "FixHPET",
        description = "Patch Out IRQ Conflicts (by CorpNewt)",
        function_name = "fix_irq_conflicts"
    ),
    PatchInfo(
        name = "GPI0",
        description = "Enable GPIO device for a I2C TouchPads to function properly",
        function_name = "enable_gpio_device"
    ),
    PatchInfo(
        name = "IMEI",
        description = "Creates a fake IMEI device to ensure Intel iGPUs acceleration functions properly",
        function_name = "add_intel_management_engine"
    ),
    PatchInfo(
        name = "MCHC",
        description = "Add a Memory Controller Hub Controller device to fix AppleSMBus",
        function_name = "add_memory_controller_device"
    ),
    PatchInfo(
        name = "PMC",
        description = "Add a PMCR device to enable NVRAM support for 300-series mainboards",
        function_name = "enable_nvram_support"
    ),
    PatchInfo(
        name = "PM (Legacy)",
        description = "Block CpuPm and Cpu0Ist ACPI tables to avoid panics for Intel Ivy Bridge and older CPUs",
        function_name = "drop_cpu_tables"
    ),
    PatchInfo(
        name = "PLUG",
        description = "Redefines CPU Objects as Processor and sets plugin-type = 1 (by CorpNewt)",
        function_name = "enable_cpu_power_management"
    ),
    PatchInfo(
        name = "PNLF",
        description = "Defines a PNLF device to enable backlight controls on laptops",
        function_name = "enable_backlight_controls"
    ),
    PatchInfo(
        name = "RMNE",
        description = "Creates a Null Ethernet to allow macOS system access to iServices",
        function_name = "add_null_ethernet_device"
    ),
    PatchInfo(
        name = "RTC0",
        description = "Creates a new RTC device to resolve PCI Configuration issues on HEDT systems",
        function_name = "fix_system_clock_hedt"
    ),
    PatchInfo(
        name = "RTCAWAC",
        description = "Context-Aware AWAC Disable and RTC Enable/Fake/Range Fix (by CorpNewt)",
        function_name = "fix_system_clock_awac"
    ),
    PatchInfo(
        name = "PRW",
        description = "Fix sleep state values in _PRW methods to prevent immediate wake in macOS",
        function_name = "instant_wake_fix"
    ),
    PatchInfo(
        name = "Surface Patch",
        description = "Special Patch for all Surface Pro / Book / Laptop hardwares",
        function_name = "surface_laptop_special_patch"
    ),
    PatchInfo(
        name = "UNC",
        description = "Disables unused uncore bridges to prevent kenel panic on HEDT systems",
        function_name = "fix_uncore_bridge"
    ),
    PatchInfo(
        name = "USB Reset",
        description = "Disable USB Hub devices to manually rebuild the ports",
        function_name = "disable_usb_hub_devices"
    ),
    PatchInfo(
        name = "USBX",
        description = "Creates an USBX device to inject USB power properties",
        function_name = "add_usb_power_properties"
    ),
    PatchInfo(
        name = "XOSI",
        description = "Spoofs the operating system to Windows, enabling devices locked behind non-Windows systems on macOS",
        function_name = "operating_system_patch"
    ),
]