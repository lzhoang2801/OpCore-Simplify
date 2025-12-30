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

## 🚀 **How To Use**

1. **Download OpCore Simplify**:
   - Click **Code** → **Download ZIP**, or download directly via this [link](https://github.com/lzhoang2801/OpCore-Simplify/archive/refs/heads/main.zip).  
   - Extract the downloaded ZIP file to your desired location.

   ![Download OpCore Simplify](https://i.imgur.com/mcE7OSX.png)

2. **Running OpCore Simplify**:
   - On **Windows**, run `OpCore-Simplify.bat`.
   - On **macOS**, run `OpCore-Simplify.command`.
   - On **Linux**, run `OpCore-Simplify.py` with existing Python interpreter.

   ![OpCore Simplify Main](https://private-user-images.githubusercontent.com/169338399/529304376-037b1b04-8f76-4a31-87f2-b2b779ff4cdb.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjcwMzkxNjUsIm5iZiI6MTc2NzAzODg2NSwicGF0aCI6Ii8xNjkzMzgzOTkvNTI5MzA0Mzc2LTAzN2IxYjA0LThmNzYtNGEzMS04N2YyLWIyYjc3OWZmNGNkYi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUxMjI5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MTIyOVQyMDA3NDVaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT05M2JiZTA0YzE2OWFlNDljZjlmYjI2NDBjZGQ0NGU5Njg1ODMwMDgwN2EyYjcxMmQ5ZDcyODBlN2JjMDFlZDdkJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.yaVVUwu0hf8Q0pZp-cn_8KixBEr0g62lXYGslkYLITc)

3. **Selecting hardware report**:

   ![Selecting hardware report](https://private-user-images.githubusercontent.com/169338399/529304594-b1e608a7-6428-4f49-8426-f4ad289a7484.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjcwMzkxNjUsIm5iZiI6MTc2NzAzODg2NSwicGF0aCI6Ii8xNjkzMzgzOTkvNTI5MzA0NTk0LWIxZTYwOGE3LTY0MjgtNGY0OS04NDI2LWY0YWQyODlhNzQ4NC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUxMjI5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MTIyOVQyMDA3NDVaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT04ZDA0ZjljMGY4MTc5YmUzNmFmZDNhNDRjYTU5ZDJiZDQ3NzI0ZjkwMDI4ODNjMDhhMTNhZGY1M2Y3MmY5MjZlJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.-9K5kz6tXqrNHK-E4jWyAio481ave9ypIt6-Em_yBJM)

4. **Verifying hardware compatibility**:

   ![Compatibility Checker](https://private-user-images.githubusercontent.com/169338399/529304672-72d4ba8c-1d8e-4a59-80e2-23212b3213da.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjcwMzkxNjUsIm5iZiI6MTc2NzAzODg2NSwicGF0aCI6Ii8xNjkzMzgzOTkvNTI5MzA0NjcyLTcyZDRiYThjLTFkOGUtNGE1OS04MGUyLTIzMjEyYjMyMTNkYS5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUxMjI5JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MTIyOVQyMDA3NDVaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0yMTA4OWFjYWM4Zjk0NWRiNDVlZWY5YzYzYTUzNmQwMDk3MzZhMTQ0MGVhN2NkODAxMjcwOTBmY2I2MGZlMzg2JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.dgaX8DZcsK3CbuKOdu62JNOypngycO98ezN5qUxvGNI)

5. **Selecting macOS Version and Customizing OpenCore EFI**:
   - By default, the latest compatible macOS version will be selected for your hardware.
   - OpCore Simplify will automatically apply essential ACPI patches and kexts. 
   - You can manually review and customize these settings as needed.

   ![Configuration Page](https://private-user-images.githubusercontent.com/169338399/530910046-81462033-696d-46e2-91f2-358ceff37199.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjcwNzg5NjQsIm5iZiI6MTc2NzA3ODY2NCwicGF0aCI6Ii8xNjkzMzgzOTkvNTMwOTEwMDQ2LTgxNDYyMDMzLTY5NmQtNDZlMi05MWYyLTM1OGNlZmYzNzE5OS5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUxMjMwJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MTIzMFQwNzExMDRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1lOGNlNzQ4MmE3ZTkzMGI0MDU0MzliZTAyMzI0YzhkZTJjNDkwYjc5NmZmZTA4YjE2NjUwYmUyMWUyMThlYzc1JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.XuqqC-VOk4SS9zSCgyGaGfrmNbjDm-MCGiK4l597ink)

6. **Building OpenCore EFI**:
   - Once you've customized all options, select **Build OpenCore EFI** to generate your EFI.
   - The tool will automatically download the necessary bootloader and kexts, which may take a few minutes.

   ![OCLP Warning](https://private-user-images.githubusercontent.com/169338399/530910077-88987465-2aab-47b9-adf8-e56f6248c88f.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjcwNzg5NjQsIm5iZiI6MTc2NzA3ODY2NCwicGF0aCI6Ii8xNjkzMzgzOTkvNTMwOTEwMDc3LTg4OTg3NDY1LTJhYWItNDdiOS1hZGY4LWU1NmY2MjQ4Yzg4Zi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUxMjMwJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MTIzMFQwNzExMDRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT01OWUzNGM2MzZmMmMwYjA5OWU0YzYxMTQ0Yjg5M2RkM2QzNDcyZGVlMTVkZWQ1ZTE5OTU5MjYwZGQ0ODVlZGVmJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.twu-QrH30NkDnqSVsvsmySf15ePAWhCStGjZDO3ia40)

   ![Build Result](https://private-user-images.githubusercontent.com/169338399/530910249-f91813db-b201-4d6a-b604-691014d29074.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjcwNzg5NjQsIm5iZiI6MTc2NzA3ODY2NCwicGF0aCI6Ii8xNjkzMzgzOTkvNTMwOTEwMjQ5LWY5MTgxM2RiLWIyMDEtNGQ2YS1iNjA0LTY5MTAxNGQyOTA3NC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUxMjMwJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MTIzMFQwNzExMDRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1mZDVjYjM2MzY2ZGJhMDcxODRlZGUzY2RhNGFjMjYzNGMyYWFiYWVmZGM4YzRmMDlkZTgzNzEwZjRjYWY2MDM1JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.uq7WzyDJKImuoUFjgfQG41s4VfgMq7h64BaSjRpU6cg)

7. **Create USB and Install macOS**: 
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
- [@rubentalstra](https://github.com/rubentalstra): Idea and code prototype [Implement GUI #471](https://github.com/lzhoang2801/OpCore-Simplify/pull/471)

## 📞 **Contact**

**Hoang Hong Quan**
> Facebook [@macforce2601](https://facebook.com/macforce2601) &nbsp;&middot;&nbsp;
> Telegram [@lzhoang2601](https://t.me/lzhoang2601) &nbsp;&middot;&nbsp;
> Email: lzhoang2601@gmail.com

## 🌟 **Star History**

[![Star History Chart](https://api.star-history.com/svg?repos=lzhoang2801/OpCore-Simplify&type=Date)](https://star-history.com/#lzhoang2801/OpCore-Simplify&Date)