<br/>
<div align="center">
  <h3 align="center">OpCore Simplify</h3>

  <p align="center">
    A tool designed to simplify the creation of <a href="https://github.com/acidanthera/OpenCorePkg">OpenCore</a> EFI. It streamlines the Hackintosh installation process by automating tasks such as auto-patching DSDT, adding suitable kexts, and customizing the config.plist. Whether you're a beginner or experienced user, OpCore Simplify takes away much of the complexity associated with Hackintosh setups.
    <br />
    <br />
    <a href="https://github.com/lzhoang2601/OpCore-Simplify/issues">Report Bug</a>
    ·
    <a href="https://github.com/lzhoang2601/OpCore-Simplify/issues">Request Feature</a>
  </p>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#-features">Features</a></li>
    <li><a href="#-support-the-project">Support the Project</a></li>
    <li><a href="#-usage-guide">Usage Guide</a></li>
    <li><a href="#-contributing">Contributing</a></li>
    <li><a href="#-license">License</a></li>
    <li><a href="#-acknowledgments--credits">Acknowledgments & Credits</a></li>
    <li><a href="#-contact">Contact</a></li>
  </ol>
</details>

---

## ✨ **Features**

1. **Automatic Updates**: Automatically check and update OpenCorePkg, kexts and AMD Vanilla Patches.
   
2. **Hardware Information Gathering**: Leverages the [Hardware Sniffer](https://github.com/lzhoang2801/Hardware-Sniffer) tool to gather detailed hardware information. It uses USB ID and PCI ID databases to ensure precise hardware compatibility checks.
   
3. **Comprehensive Hardware Support**: Fully supports most modern hardware (excluding legacy devices). Use the Compatibility Checker to view supported/unsupported devices.

4. **Enhanced ACPI Patching**: Add and customize various ACPI patches with integrated support from [SSDTTime](https://github.com/corpnewt/SSDTTime).
   
5. **Device-Specific Kexts**: Automatically identifies and adds kexts for devices like WiFi, ethernet, sound codec, Bluetooth, keyboard, mouse, touchpad, USB controller, and SATA controller based on their hardware IDs.
   
6. **Custom Tweaks**: Apply additional customization based on both widely used sources and personal experience.

---

### ☕ **Support the Project**:

If you love what I'm building, consider buying me a coffee! Your support fuels new features and improvements. ☕✨

<p align="center">
  <a href="https://www.buymeacoffee.com/lzhoang2801">
    <img src="https://img.buymeacoffee.com/button-api/?text=Donate with Buy Me a Coffee&emoji=☕&slug=lzhoang2801&button_colour=FFDD00&font_colour=000000&font_family=Bree&outline_colour=000000&coffee_colour=ffffff" />
  </a>
<p>

Thank you for your support! Every little bit helps! 😊

---

## 🚀 **Usage Guide**

1. **Running OpCore Simplify**:
   - On **Windows**, run `OpCore-Simplify.bat`.
   - On **macOS**, run `OpCore-Simplify.command`.

2. **Selecting a Hardware Report**:
   - Use [**Hardware Sniffer**](https://github.com/lzhoang2801/Hardware-Sniffer) to generate a hardware report and an ACPI dump.
   - Select your hardware report (`Report.json`) and ACPI folder to proceed with configuration.

3. **Selecting macOS Version and Customizing EFI**:
   - By default, the latest compatible macOS version will be selected for your hardware.
   - OpCore Simplify will automatically apply essential ACPI patches and kexts. 
   - You can manually review and customize these settings as needed.

4. **Building OpenCore EFI**:
   - Once you've customized all options, select **Build OpenCore EFI** to generate your EFI.
   - The tool will automatically download the necessary bootloader and kexts, which may take a few minutes.

5. **USB Mapping**:
   - After building your EFI, follow the steps for mapping USB ports.

6. **Create USB and Install macOS**: Follow the guide at [OpenCore Install Guide](https://dortania.github.io/OpenCore-Install-Guide/installer-guide/) and use the generated OpenCore EFI.
   - For troubleshooting, refer to the [OpenCore Troubleshooting Guide](https://dortania.github.io/OpenCore-Install-Guide/troubleshooting/troubleshooting.html).

#### Reference Resources

- [OpenCore Install Guide](https://dortania.github.io/OpenCore-Install-Guide) (some parts may be outdated)
- [ChefKiss](https://chefkissinc.github.io/guides/hackintosh/) (dedicated to AMD CPU systems)

---

## 🤝 **Contributing**

Contributions are **highly appreciated**! If you have ideas to improve this project, feel free to fork the repo and create a pull request, or open an issue with the "enhancement" tag.

Don't forget to ⭐ star the project! Thank you for your support! 🌟

---

## 📜 **License**

Distributed under the BSD 3-Clause License. See `LICENSE` for more information.

---

## 🙌 **Acknowledgments & Credits**

- [OpenCorePkg](https://github.com/acidanthera/OpenCorePkg) and [kexts](https://github.com/lzhoang2801/OpCore-Simplify/blob/main/Scripts/datasets/kext_data.py) – The backbone of this project.
- [SSDTTime](https://github.com/corpnewt/SSDTTime) – SSDT patching utilities.
- [Hardware Sniffer](https://github.com/lzhoang2801/Hardware-Sniffer) – For hardware information gathering.
- [USBToolBox](https://github.com/USBToolBox/tool) – A USB mapping tool.
- [ProperTree](https://github.com/corpnewt/ProperTree) – For editing `config.plist` files.

---

## 📞 **Contact**

**Hoang Hong Quan**  
- Facebook: [@macforce2601](https://facebook.com/macforce2601)  
- Telegram: [@lzhoang2601](https://t.me/lzhoang2601)  
- Email: lzhoang2601@gmail.com
