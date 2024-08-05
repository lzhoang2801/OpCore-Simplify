class GPUIdentifier:
    def identify_intel_graphics(self, hardware_id):
        gpu_codename = "Unknown"
        device_id = hardware_id[5:]

        if device_id.startswith("01"):
            if device_id[-2] in ["5", "6"]:
                gpu_codename = "Ivy Bridge"
            else:
                gpu_codename = "Sandy Bridge"
        elif device_id.startswith(("04", "0A", "0C", "0D")):
            gpu_codename = "Haswell"
        elif device_id.startswith(("0B", "16")):
            gpu_codename = "Broadwell"
        elif device_id.startswith(("09", "19")):
            gpu_codename = "Skylake"
        elif device_id.startswith("59"):
            if device_id.endswith("17"):
                gpu_codename = "Kaby Lake-R"
            else:
                gpu_codename = "Kaby Lake"
        elif device_id.startswith("87"):
            gpu_codename = "Amber Lake"
        elif device_id.startswith(("3E", "5A")):
            if device_id.endswith(("A0", "A1")):
                gpu_codename = "Whiskey Lake"
            else:
                gpu_codename = "Coffee Lake"
        elif device_id.startswith("8A"):
            gpu_codename = "Ice Lake"
        elif device_id.startswith("9B"):
            gpu_codename = "Comet Lake"

        return {
            "Manufacturer": "Intel",
            "GPU Codename": gpu_codename,
            "Device ID": hardware_id,
            "Device Type": "Unknown" if gpu_codename == "Unknown" else "Integrated GPU"
        }

    def identify_amd_graphics(self, hardware_id):
        gpu_codename = "Unknown"
        device_id = hardware_id[5:]

        if device_id.startswith("15D8"):
            gpu_codename = "Picasso"
        elif device_id.startswith("15DD"):
            gpu_codename = "Raven Ridge"
        elif device_id.startswith("15E7"):
            gpu_codename = "Barcelo"
        elif device_id.startswith("1636"):
            gpu_codename = "Renoir"
        elif device_id.startswith("1638"):
            gpu_codename = "Cezanne"
        elif device_id.startswith("164C"):
            gpu_codename = "Lucienne"
        elif device_id.startswith(("67C", "67D")):
            gpu_codename = "Ellesmere"
        elif device_id.startswith(("67E", "67F")):
            gpu_codename = "Baffin"
        elif device_id.startswith("694"):
            gpu_codename = "Polaris 22"
        elif device_id.startswith(("698", "699")):
            gpu_codename = "Lexa"
        elif device_id.startswith("69A"):
            gpu_codename = "Vega 12"
        elif device_id.startswith("6FDF"):
            gpu_codename = "Polaris 20"
        elif device_id.startswith(("686", "687")):
            gpu_codename = "Vega 10"
        elif device_id.startswith("66A"):
            gpu_codename = "Vega 20"
        elif device_id.startswith("731"):
            gpu_codename = "Navi 10"
        elif device_id.startswith("734"):
            gpu_codename = "Navi 14"
        elif device_id.startswith("736"):
            gpu_codename = "Navi 12"
        elif device_id.startswith(("73A", "73B")):
            gpu_codename = "Navi 21"
        elif device_id.startswith(("73C", "73D")):
            gpu_codename = "Navi 22"
        elif device_id.startswith(("73E", "73FF")):
            gpu_codename = "Navi 23"
        
        return {
            "Manufacturer": "AMD",
            "GPU Codename": gpu_codename,
            "Device ID": hardware_id,
            "Device Type": "Unknown" if gpu_codename == "Unknown" else "Integrated GPU" if device_id.startswith(("15", "16")) else "Discrete GPU"
        }

    def identify_nvidia_graphics(self, hardware_id):
        gpu_codename = "Unknown"
        device_id = hardware_id[5:]

        if device_id.startswith(("0FC", "0FD", "0FE", "0FF", "100", "101", "102", "103", "11", "128", "129", "12A", "12B", "130")) and device_id != "1140":
            gpu_codename = "Kepler"
        elif device_id.startswith(("05E", "05F", "0A2", "0A3", "0A6", "0A7", "0C", "10C", "10D")):
            gpu_codename = "Tesla"
        elif device_id.startswith(("06C", "06D", "0DC", "0DD", "0DE", "0DF", "0E2", "0E3", "0F0", "104", "105", "107", "108", "109", "114", "120", "121", "124", "125")):
            gpu_codename = "Fermi"
        elif device_id.startswith(("13", "14", "16", "17")) and not device_id.startswith("172"):
            gpu_codename = "Maxwell"
        elif device_id.startswith(("15", "172", "1B", "1C", "1D0", "1D1", "1D3", "1D5")):
            gpu_codename = "Pascal"
        
        return {
            "Manufacturer": "NVIDIA",
            "GPU Codename": gpu_codename,
            "Device ID": hardware_id,
            "Device Type": "Discrete GPU"
        }

    def classify_gpu(self, hardware_id):
        if hardware_id.startswith("8086"):
            return self.identify_intel_graphics(hardware_id)
        elif hardware_id.startswith("1002"):
            return self.identify_amd_graphics(hardware_id)
        elif hardware_id.startswith("10DE"):
            return self.identify_nvidia_graphics(hardware_id)
        else:
            return {
                "Manufacturer": "Unknown",
                "GPU Codename": "Unknown",
                "Device ID": hardware_id,
                "Device Type": "Unknown"
            }