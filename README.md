<br/>
<div align="center">
  <h3 align="center">OpCore Simplify</h3>

  <p align="center">
    A tool designed to simplify the creation of <a href="https://github.com/acidanthera/OpenCorePkg">OpenCore</a> EFI. It includes features such as auto-patching DSDT, adding suitable kexts, and customizing the config.plist to make Hackintosh installation easy for beginners.
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
    <li><a href="#features">Features</a></li>
    <li><a href="#usage-guide">Usage Guide</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

## Features 

1. **Automatic Updates**: Check and update AMD Vanilla Patches, OpenCore NO ACPI, and kexts automatically.
2. **Hardware Information Gathering**: Use AIDA64 reports to collect detailed hardware information, utilizing USB ID and PCI ID for the most precise compatibility checks.
3. **Comprehensive Hardware Support**: Fully supports all available hardware (excluding legacy hardware). Try and view results on the Compatibility Checker screen.
4. **Enhanced ACPI Patching**: Add various ACPI patches with support from the [SSDTTime](https://github.com/corpnewt/SSDTTime).
5. **Device-Specific Kexts**: Identify and add the correct kexts for devices such as WiFi, ethernet, sound codec, bluetooth, keyboard, mouse, touchpad, USB controller, and SATA controller based on their IDs.
6. **Custom Tweaks**: Apply additional customizations based on a variety of sources and personal experience.

## Usage Guide

Follow the steps, customize as needed, and enjoy your optimized system!

1. Run `OpCore-Simplify.bat` on Windows or `OpCore-Simplify.command` on macOS.

2. **AIDA64 Report**: Enter the path or drag and drop your AIDA64 report.
   - Ensure you follow any instructions on this screen.

3. **Review Hardware Information**: Verify the detected hardware information and receive compatibility results.

4. **Select macOS Version**: Choose the compatible macOS version you wish to install.

5. **Enter ACPI Tables Folder Path**: 
   - Select `P` to dump ACPI tables from the current machine if it is the same machine used for the AIDA64 report.

6. **Preview OpenCore EFI Results**: 
   - Review the generated OpenCore EFI for your hardware.
   - Make sure to read any green-highlighted lines (in parentheses).

7. **USB Mapping**: Use USBToolBox with the 'Use Native Class' option enabled to map USBs and add the resulting kext to `OC/Kexts`.

8. **Create USB and Install macOS**: Follow the guide at [OpenCore Install Guide](https://dortania.github.io/OpenCore-Install-Guide/installer-guide/) and use the generated OpenCore EFI.
    - For troubleshooting issues booting macOS, please refer to the [OpenCore Troubleshooting Guide](https://dortania.github.io/OpenCore-Install-Guide/troubleshooting/troubleshooting.html) or contact me for assistance.

#### Reference Resources

- [OpenCore Install Guide](https://dortania.github.io/OpenCore-Install-Guide) (some parts may be outdated)
- [ChefKissNext](https://chefkissnext.netlify.app/guides/hackintosh/) (dedicated to AMD CPU systems)

## Contributing

Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

**Don't forget to give the project a star! Thanks again!**

## License

Distributed under the BSD 3-Clause License. See `LICENSE` for more information.

## Contact

Hoang Hong Quan - [@facebook](https://facebook.com/macforce2601) - [@telegram](https://t.me/lzhoang2601) - lzhoang2601@gmail.com