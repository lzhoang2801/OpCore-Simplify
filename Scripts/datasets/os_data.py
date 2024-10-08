class macOSVersionInfo:
    def __init__(self, name, macos_version, release_status = "final"):
        self.name = name
        self.darwin_version = (int(macos_version.split(".")[1]) + 4) if "10." in macos_version else (int(macos_version.split(".")[0]) + 9)
        self.macos_version = macos_version
        self.release_status = release_status

macos_versions = [
    macOSVersionInfo("High Sierra", "10.13"),
    macOSVersionInfo("Mojave", "10.14"),
    macOSVersionInfo("Catalina", "10.15"),
    macOSVersionInfo("Big Sur", "11"),
    macOSVersionInfo("Monterey", "12"),
    macOSVersionInfo("Ventura", "13"),
    macOSVersionInfo("Sonoma", "14"),
    macOSVersionInfo("Sequoia", "15")
]

def get_latest_darwin_version():
    return "{}.{}.{}".format(macos_versions[-1].darwin_version, 99, 99)

def get_lowest_darwin_version():
    return "{}.{}.{}".format(macos_versions[0].darwin_version, 0, 0)

def get_macos_name_by_darwin(darwin_version):
    for data in macos_versions:
        if data.darwin_version == int(darwin_version[:2]):
            return "macOS {} {}{}".format(data.name, data.macos_version, "" if data.release_status == "final" else " (Beta)")
    return None
