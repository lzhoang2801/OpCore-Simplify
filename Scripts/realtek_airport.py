"""Selection policy for the PCIe Realtek AirPort drivers (Darwin versions)."""
def selected_kexts(version):
    major = int(version.split(".")[0])
    if 18 <= major <= 20:
        return ["Realtek88LegacyAirport"]
    if major == 22:
        return ["AirPort_RTW88"]
    if 23 <= major <= 25:
        return ["AirPort_RTW88", "IO80211FamilyLegacy", "IOSkywalkFamily", "AMFIPass"]
    return []
