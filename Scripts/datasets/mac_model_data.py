from Scripts.datasets import os_data

class MacDevice:
    def __init__(self, name, cpu, cpu_generation, discrete_gpu, initial_support, last_supported_version = None):
        self.name = name
        self.cpu = cpu
        self.cpu_generation = cpu_generation
        self.discrete_gpu = discrete_gpu
        self.initial_support = initial_support
        self.last_supported_version = last_supported_version or os_data.get_latest_darwin_version()

mac_devices = [
    # iMac Models
    MacDevice("iMac12,1", "i5-2400S", "Sandy Bridge", "AMD Radeon HD 6750M", "10.6.0", "17.99.99"),
    MacDevice("iMac12,2", "i7-2600", "Sandy Bridge", "AMD Radeon HD 6770M", "10.6.0", "17.99.99"),
    MacDevice("iMac13,1", "i7-3770S", "Ivy Bridge", "NVIDIA GeForce GT 640M", "12.2.0", "19.99.99"),
    MacDevice("iMac13,2", "i5-3470S", "Ivy Bridge", "NVIDIA GeForce GTX 660M", "12.2.0", "19.99.99"),
    MacDevice("iMac13,3", "i5-3470S", "Ivy Bridge", None, "12.2.0", "19.99.99"),
    MacDevice("iMac14,1", "i5-4570R", "Haswell", None, "12.4.0", "19.99.99"),
    MacDevice("iMac14,2", "i7-4771", "Haswell", "NVIDIA GeForce GT 750M", "12.4.0", "19.99.99"),
    MacDevice("iMac14,3", "i5-4570S", "Haswell", "NVIDIA GeForce GT 755M", "12.4.0", "19.99.99"),
    MacDevice("iMac14,4", "i5-4260U", "Haswell", None, "13.2.0", "20.99.99"),
    MacDevice("iMac15,1", "i7-4790K", "Haswell", "AMD Radeon R9 M290X", "14.0.0", "20.99.99"),
    MacDevice("iMac16,1", "i5-5250U", "Broadwell", None, "15.0.0", "21.99.99"),
    MacDevice("iMac16,2", "i5-5675R", "Broadwell", None, "15.0.0", "21.99.99"),
    MacDevice("iMac17,1", "i5-6500", "Skylake", "AMD Radeon R9 M380", "15.0.0", "21.99.99"),
    MacDevice("iMac18,1", "i5-7360U", "Kaby Lake", None, "16.5.0", "22.99.99"),
    MacDevice("iMac18,2", "i5-7400", "Kaby Lake", "AMD Radeon Pro 555", "16.5.0", "22.99.99"),
    MacDevice("iMac18,3", "i5-7600K", "Kaby Lake", "AMD Radeon Pro 570", "16.5.0", "22.99.99"),
    MacDevice("iMac19,1", "i9-9900K", "Coffee Lake", "AMD Radeon Pro 570X", "18.5.0"),
    MacDevice("iMac19,2", "i5-8500", "Coffee Lake", "AMD Radeon Pro 555X", "18.5.0"),
    MacDevice("iMac20,1", "i5-10500", "Comet Lake", "AMD Radeon Pro 5300", "19.6.0"),
    MacDevice("iMac20,2", "i9-10910", "Comet Lake", "AMD Radeon Pro 5300", "19.6.0"),
    # MacBook Models
    MacDevice("MacBook8,1", "M-5Y51", "Broadwell", None, "14.1.0", "20.99.99"),
    MacDevice("MacBook9,1", "m3-6Y30", "Skylake", None, "15.4.0", "21.99.99"),
    MacDevice("MacBook10,1", "m3-7Y32", "Kaby Lake", None, "16.6.0", "22.99.99"),
    # MacBookAir Models
    MacDevice("MacBookAir4,1", "i5-2467M", "Sandy Bridge", None, "11.0.0", "17.99.99"),
    MacDevice("MacBookAir4,2", "i5-2557M", "Sandy Bridge", None, "11.0.0", "17.99.99"),
    MacDevice("MacBookAir5,1", "i5-3317U", "Ivy Bridge", None, "11.4.0", "19.99.99"),
    MacDevice("MacBookAir5,2", "i5-3317U", "Ivy Bridge", None, "12.2.0", "19.99.99"),
    MacDevice("MacBookAir6,1", "i5-4250U", "Haswell", None, "12.4.0", "20.99.99"),
    MacDevice("MacBookAir6,2", "i5-4250U", "Haswell", None, "12.4.0", "20.99.99"),
    MacDevice("MacBookAir7,1", "i5-5250U", "Broadwell", None, "14.1.0", "21.99.99"),
    MacDevice("MacBookAir7,2", "i5-5250U", "Broadwell", None, "14.1.0", "21.99.99"),
    MacDevice("MacBookAir8,1", "i5-8210Y", "Amber Lake", None, "18.2.0"),
    MacDevice("MacBookAir8,2", "i5-8210Y", "Amber Lake", None, "18.6.0"),
    MacDevice("MacBookAir9,1", "i3-1000NG4", "Ice Lake", None, "19.4.0"),
    # MacBookPro Models
    MacDevice("MacBookPro8,1", "i5-2415M", "Sandy Bridge", None, "10.6.0", "17.99.99"),
    MacDevice("MacBookPro8,2", "i7-2675QM", "Sandy Bridge", "AMD Radeon HD 6490M", "10.6.0", "17.99.99"),
    MacDevice("MacBookPro8,3", "i7-2820QM", "Sandy Bridge", "AMD Radeon HD 6750M", "10.6.0", "17.99.99"),
    MacDevice("MacBookPro9,1", "i7-3615QM", "Ivy Bridge", "NVIDIA GeForce GT 650M", "11.3.0", "19.99.99"),
    MacDevice("MacBookPro9,2", "i5-3210M", "Ivy Bridge", None, "11.3.0", "19.99.99"),
    MacDevice("MacBookPro10,1", "i7-3615QM", "Ivy Bridge", "NVIDIA GeForce GT 650M", "11.4.0", "19.99.99"),
    MacDevice("MacBookPro10,2", "i5-3210M", "Ivy Bridge", None, "12.2.0", "19.99.99"),
    MacDevice("MacBookPro11,1", "i5-4258U", "Haswell", None, "13.0.0", "20.99.99"),
    MacDevice("MacBookPro11,2", "i7-4770HQ", "Haswell", None, "13.0.0", "20.99.99"),
    MacDevice("MacBookPro11,3", "i7-4850HQ", "Haswell", "NVIDIA GeForce GT 750M", "13.0.0", "20.99.99"),
    MacDevice("MacBookPro11,4", "i7-4770HQ", "Haswell", None, "14.3.0", "21.99.99"),
    MacDevice("MacBookPro11,5", "i7-4870HQ", "Haswell", "AMD Radeon R9 M370X", "14.3.0", "21.99.99"),
    MacDevice("MacBookPro12,1", "i5-5257U", "Broadwell", None, "14.1.0", "21.99.99"),
    MacDevice("MacBookPro13,1", "i5-6360U", "Skylake", None, "16.0.0", "22.99.99"),
    MacDevice("MacBookPro13,2", "i7-6567U", "Skylake", None, "16.1.0", "22.99.99"),
    MacDevice("MacBookPro13,3", "i7-6700HQ", "Skylake", "AMD Radeon Pro 450", "16.1.0", "22.99.99"),
    MacDevice("MacBookPro14,1", "i5-7360U", "Kaby Lake", None, "16.6.0", "22.99.99"),
    MacDevice("MacBookPro14,2", "i5-7267U", "Kaby Lake", None, "16.6.0", "22.99.99"),
    MacDevice("MacBookPro14,3", "i7-7700HQ", "Kaby Lake", "AMD Radeon Pro 555", "16.6.0", "22.99.99"),
    MacDevice("MacBookPro15,1", "i7-8750H", "Coffee Lake", "AMD Radeon Pro 555X", "17.99.99"),
    MacDevice("MacBookPro15,2", "i7-8559U", "Coffee Lake", None, "17.99.99"),
    MacDevice("MacBookPro15,3", "i7-8850H", "Coffee Lake", "AMD Radeon Pro Vega 16", "18.2.0"),
    MacDevice("MacBookPro15,4", "i5-8257U", "Coffee Lake", None, "18.6.0"),
    MacDevice("MacBookPro16,1", "i7-9750H", "Coffee Lake", "AMD Radeon Pro 5300", "19.0.0"),
    MacDevice("MacBookPro16,2", "i5-1038NG7", "Ice Lake", None, "19.4.0"),
    MacDevice("MacBookPro16,3", "i5-8257U", "Coffee Lake", None, "19.4.0"),
    MacDevice("MacBookPro16,4", "i7-9750H", "Coffee Lake", "AMD Radeon Pro 5600M", "19.0.0"),
    # Macmini Models
    MacDevice("Macmini5,1", "i5-2415M", "Sandy Bridge", None, "11.0.0", "17.99.99"),
    MacDevice("Macmini5,2", "i5-2520M", "Sandy Bridge", None, "11.0.0", "17.99.99"),
    MacDevice("Macmini5,3", "i7-2635QM", "Sandy Bridge", None, "11.0.0", "17.99.99"),
    MacDevice("Macmini6,1", "i5-3210M", "Ivy Bridge", None, "10.8.1", "19.99.99"),
    MacDevice("Macmini6,2", "i7-3615QM", "Ivy Bridge", None, "10.8.1", "19.99.99"),
    MacDevice("Macmini7,1", "i5-4260U", "Haswell", None, "14.0.0", "21.99.99"),
    MacDevice("Macmini8,1", "i7-8700B", "Coffee Lake", None, "18.0.0"),
    # iMacPro Models
    MacDevice("iMacPro1,1", "W-2140B", "Skylake-W", "AMD Radeon RX Vega 56", "17.3.0"),
    # MacPro Models
    MacDevice("MacPro6,1", "E5-1620 v2", "Ivy Bridge EP", "AMD FirePro D300", "10.9.1", "21.99.99"),
    MacDevice("MacPro7,1", "W-3245M", "Cascade Lake-W", "AMD Radeon Pro 580X", "19.0.0")
]

def get_mac_device_by_name(name):
    return next((mac_device for mac_device in mac_devices if mac_device.name == name), None)