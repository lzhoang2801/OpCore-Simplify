<br/>
<div align="center">
  <h3 align="center">OpCore Simplify</h3>

  <p align="center">
    A specialized tool that streamlines <a href="https://github.com/acidanthera/OpenCorePkg">OpenCore</a> EFI creation by automating the essential setup process and providing standardized configurations. Designed to reduce manual effort while ensuring accuracy in your Hackintosh journey.
    <br />
    <br />
    <a href="#-features">Features</a> •
    <a href="#-how-to-use">How To Use</a> •
    <a href="#-contributing">Contributing</a> •
    <a href="#-license">License</a> •
    <a href="#-credits">Credits</a> •
    <a href="#-contact">Contact</a>
  </p>
  
  <p align="center">
    <a href="https://trendshift.io/repositories/15410" target="_blank"><img src="https://trendshift.io/api/badge/repositories/15410" alt="lzhoang2801%2FOpCore-Simplify | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
  </p>
</div>

> [!NOTE]
> **OpenCore Legacy Patcher 3.0.0 – Now Supports macOS Tahoe 26!**
> 
> The long awaited version 3.0.0 of OpenCore Legacy Patcher is here, bringing **initial support for macOS Tahoe 26** to the community!
> 
> 🚨 **Please Note:**  
> - Only OpenCore-Patcher 3.0.0 **from the [lzhoang2801/OpenCore-Legacy-Patcher](https://github.com/lzhoang2801/OpenCore-Legacy-Patcher/releases/tag/3.0.0)** repository provides support for macOS Tahoe 26 with early patches.
> - Official Dortania releases or older patches **will NOT work** with macOS Tahoe 26.  

> [!WARNING]
> While OpCore Simplify significantly reduces setup time, the Hackintosh journey still requires:
> - Understanding basic concepts from the [Dortania Guide](https://dortania.github.io/OpenCore-Install-Guide/)
> - Testing and troubleshooting during the installation process
> - Patience and persistence in resolving any issues that arise
>
> Our tool does not guarantee a successful installation in the first attempt, but it should help you get started.

## 🎨 **Modern GUI with qfluentwidgets**

OpCore Simplify features a beautiful, modern graphical user interface built with [qfluentwidgets](https://qfluentwidgets.com), implementing Microsoft's Fluent Design System:

- ✨ Modern, intuitive interface with smooth animations
- 🎨 Beautiful UI components following Fluent Design principles
- 🌓 Light/dark theme support
- 📱 Responsive layout that works on various screen sizes
- 🖥️ Cross-platform compatibility (Windows, macOS, Linux)
- 💨 Fast and responsive with lazy loading
- 🔧 Built on PyQt6 for stability and performance

The GUI provides an easy-to-follow step-by-step wizard while still allowing CLI mode for advanced users or automation.

## ✨ **Features**

1. **Comprehensive Hardware and macOS Support**  
   Fully supports modern hardware. Use `Compatibility Checker` to check supported/unsupported devices and macOS version supported.

   | **Component**  | **Supported**                                                                                       |
   |----------------|-----------------------------------------------------------------------------------------------------|
   | **CPU**        | Intel: Nehalem and Westmere (1st Gen) → Arrow Lake (15th Gen/Core Ultra Series 2) <br> AMD: Ryzen and Threadripper with [AMD Vanilla](https://github.com/AMD-OSX/AMD_Vanilla) |
   | **GPU**        | Intel iGPU: Iron Lake (1st Gen) → Ice Lake (10th Gen) <br> AMD APU: The entire Vega Raven ASIC family (Ryzen 1xxx → 5xxx, 7x30 series) <br> AMD dGPU: Navi 23, Navi 22, Navi 21 generations, and older series <br> NVIDIA: Kepler, Pascal, Maxwell, Fermi, Tesla generations |
   | **macOS**      | macOS High Sierra → macOS Tahoe |

2. **ACPI Patches and Kexts**  
   Automatically detects and adds ACPI patches and kexts based on hardware configuration.
   
   - Integrated with [SSDTTime](https://github.com/corpnewt/SSDTTime) for common patches (e.g., FakeEC, FixHPET, PLUG, RTCAWAC).
   - Includes custom patches:
      - Prevent kernel panics by directing the first CPU entry to an active CPU, disabling the UNC0 device, and creating a new RTC device for HEDT systems.
      - Disable unsupported or unused PCI devices, such as the GPU (using Optimus and Bumblebee methods or adding the disable-gpu property), Wi-Fi card, and NVMe storage controller.
      - Fix sleep state values in _PRW methods (GPRW, UPRW, HP special) to prevent immediate wake.
      - Add devices including ALS0, BUS0, MCHC, PMCR, PNLF, RMNE, IMEI, USBX, XOSI, along with a Surface Patch.
      - Enable ALSD and GPI0 devices.

3. **Automatic Updates**  
    Automatically checks for and updates OpenCorePkg and kexts from [Dortania Builds](https://dortania.github.io/builds/) and GitHub releases before each EFI build.
            
4. **EFI Configuration**  
   Apply additional customization based on both widely used sources and personal experience.

   - Spoof GPU IDs for certain AMD GPUs not recognized in macOS.
   - Use CpuTopologyRebuild kext for Intel CPUs with P-cores and E-cores to enhance performance.
   - Disable System Integrity Protection (SIP).
   - Spoof CPU IDs for Intel Pentium, Celeron, Core, and Xeon processors.
   - Add custom CPU names for AMD CPUs, as well as Intel Pentium, Celeron, Xeon, and Core lines from the Rocket Lake (11th) generation and newer.
   - Add a patch to allow booting macOS with unsupported SMBIOS.
   - Add NVRAM entries to bypass checking the internal Bluetooth controller.
   - Properly configure ResizeAppleGpuBars based on specific Resizable BAR information.
   - Allow flexible iGPU configuration between headless and driving a display when a supported discrete GPU is present.
   - Force Intel GPUs into VESA mode with HDMI and DVI connectors to simplify installation process.
   - Provide configuration required for using OpenCore Legacy Patcher.
   - Add built-in device property for network devices (fix 'Could not communicate with the server' when using iServices) and storage controllers (fix internal drives shown as external).
   - Prioritize SMBIOS optimized for both power management and performance.
   - Re-enable CPU power management on legacy Intel CPUs in macOS Ventura 13 and newer.
   - Apply WiFi profiles for itlwm kext to enable auto WiFi connections at boot time.

   and more...

5. **Easy Customization**  
   In addition to the default settings applied, users can easily make further customizations if desired.

   - Custom ACPI patches, kexts, and SMBIOS adjustments (**not recommended**).
   - Force load kexts on unsupported macOS versions.

6. **Config.plist Editor** 🆕  
   A powerful TreeView-based editor for managing OpenCore configurations:
   
   - **Interactive TreeView**: Browse and edit your config.plist with a clear hierarchical display
   - **OC Snapshot**: Automatically scan and sync ACPI, Kexts, Drivers, and Tools from your EFI folder (based on [ProperTree](https://github.com/corpnewt/ProperTree))
   - **Validation**: Comprehensive checks for path lengths, structure, duplicates, and kext dependencies
   - **Type-aware Editing**: Edit values with appropriate controls for Boolean, Number, String, and Data types
   - **File Operations**: Load, Save, and Save As functionality with plist format preservation
   
   See [Config Editor Documentation](docs/CONFIG_EDITOR.md) for detailed usage instructions.

## 🚀 **How To Use**

1. **Download OpCore Simplify**:
   - Click **Code** → **Download ZIP**, or download directly via this [link](https://github.com/lzhoang2801/OpCore-Simplify/archive/refs/heads/main.zip).  
   - Extract the downloaded ZIP file to your desired location.

   ![Download OpCore Simplify](https://i.imgur.com/mcE7OSX.png)

2. **Install GUI Dependencies** (Optional, for GUI mode):
   ```bash
   pip install -r requirements.txt
   ```
   Or install manually:
   ```bash
   pip install PyQt6 PyQt6-Fluent-Widgets
   ```
   
   **Note:** If GUI dependencies are not installed, the application will automatically run in CLI mode. You can also explicitly use CLI mode with `python OpCore-Simplify.py --cli`.

3. **Running OpCore Simplify**:
   - On **Windows**, run `OpCore-Simplify.bat`.
   - On **macOS**, run `OpCore-Simplify.command`.
   - On **Linux**, run `OpCore-Simplify.py` with existing Python interpreter.

   ![OpCore Simplify Menu](https://i.imgur.com/vTr1V9D.png)

4. **Selecting hardware report**:
   - On Windows, there will be an option for `E. Export hardware report`. It's recommended to use this for the best results with your hardware configuration and BIOS at the time of building.
   - Alternatively, use [**Hardware Sniffer**](https://github.com/lzhoang2801/Hardware-Sniffer) to create a `Report.json` and ACPI dump for configuration manully.

   ![Selecting hardware report](https://i.imgur.com/MbRmIGJ.png)

   ![Loading ACPI Tables](https://i.imgur.com/SbL6N6v.png)

   ![Compatibility Checker](https://i.imgur.com/kuDGMmp.png)

5. **Selecting macOS Version and Customizing OpenCore EFI**:
   - By default, the latest compatible macOS version will be selected for your hardware.
   - OpCore Simplify will automatically apply essential ACPI patches and kexts. 
   - You can manually review and customize these settings as needed.

   ![OpCore Simplify Menu](https://i.imgur.com/TSk9ejy.png)

6. **Building OpenCore EFI**:
   - Once you've customized all options, select **Build OpenCore EFI** to generate your EFI.
   - The tool will automatically download the necessary bootloader and kexts, which may take a few minutes.

   ![WiFi Profile Extractor](https://i.imgur.com/71TkJkD.png)

   ![Choosing Codec Layout ID](https://i.imgur.com/Mcm20EQ.png)

   ![Building OpenCore EFI](https://i.imgur.com/deyj5de.png)

7. **USB Mapping**:
   - After building your EFI, follow the steps for mapping USB ports.

   ![Results](https://i.imgur.com/MIPigPF.png)

8. **Create USB and Install macOS**: 
   - Use [**UnPlugged**](https://github.com/corpnewt/UnPlugged) on Windows to create a USB macOS installer, or follow [this guide](https://dortania.github.io/OpenCore-Install-Guide/installer-guide/mac-install.html) for macOS.
   - For troubleshooting, refer to the [OpenCore Troubleshooting Guide](https://dortania.github.io/OpenCore-Install-Guide/troubleshooting/troubleshooting.html).

> [!NOTE]
> 1. After a successful installation, if OpenCore Legacy Patcher is required, simply apply root patches to activate the missing features (such as modern Broadcom Wi-Fi card and graphics acceleration).
> 
> 2. For AMD GPUs, after applying root patches from OpenCore Legacy Patcher, you need to remove the boot argument `-radvesa`/`-amd_no_dgpu_accel` for graphics acceleration to work.

## 🤝 **Contributing**

Contributions are **highly appreciated**! If you have ideas to improve this project, feel free to fork the repo and create a pull request, or open an issue with the "enhancement" tag.

Don't forget to ⭐ star the project! Thank you for your support! 🌟

## 📜 **License**

Distributed under the BSD 3-Clause License. See `LICENSE` for more information.

## 🙌 **Credits**

- [OpenCorePkg](https://github.com/acidanthera/OpenCorePkg) and [kexts](https://github.com/lzhoang2801/OpCore-Simplify/blob/main/Scripts/datasets/kext_data.py) – The backbone of this project.
- [SSDTTime](https://github.com/corpnewt/SSDTTime) – SSDT patching utilities.

## 📞 **Contact**

**Hoang Hong Quan**
> Facebook [@macforce2601](https://facebook.com/macforce2601) &nbsp;&middot;&nbsp;
> Telegram [@lzhoang2601](https://t.me/lzhoang2601) &nbsp;&middot;&nbsp;
> Email: lzhoang2601@gmail.com

## 🌟 **Star History**

[![Star History Chart](https://api.star-history.com/svg?repos=lzhoang2801/OpCore-Simplify&type=Date)](https://star-history.com/#lzhoang2801/OpCore-Simplify&Date)
