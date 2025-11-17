<br/>
<div align="center">
  <h3 align="center">OpCore Simplify Vulnerabilities fixes</h3>

  <p> ⚠️ Disclaimer: This fork of OpCore-Simplify exists solely to demonstrate and propose a fix for a different vulnerabilities found in this project. </p>
<p> It is not intended for general use or long-term maintenance. Users are strongly encouraged to use the official repository here https://github.com/lzhoang2801/OpCore-Simplify for stable and trusted releases. </p>
<p> This fork includes a proof-of-concept patch to mitigate all vulnerabilities. If accepted, it should be merged upstream. </p>
<p>Vulnerabilities that are mitigated in this project:</p>
<p>-an attacker could redirect kext downloads to malicious URLs - which could lead to placing malicious kexts in the EFI partition and then installing kernel level malware. This exploit is already in the wild - OpCore-Simplify2 (whose repo is https://github.com/w1842893/OpCore-Simplify2) already exploits this vulnerability. It is mitigated by checking kexts against trusted repos.
<p>-it uses an outdated user agent of Google Chrome - Google Chrome 131. This opens also all vulnerabilities that Google has patched in newer versions of Chrome. This exploit is mitigated by changing the user agent to the latest version of Safari - Safari 26.1. And this opens also a vulnerability where websites redirect to outdated servers which can lead to even more vulnerabilities.</p>
<p>- An attacker could upload a maliciously crafted JSON file that could execute files outside the OpCore-Simplify's folder - this is mitigated by not allowing the script to execute outside OpCore-Simplify's workspace</p>
<p>-An attacker could upload a specially crafted JSON file to crash the project or execute code - this is mitigated by denying uploads of invalid JSON files</p>
<p>-An attacker could upload an empty JSON file without triggering any warnings - this is mitigated by denying uploads of invalid JSON files</p>
<p>-An attacker could upload oversized JSON files like 1GB JSON reports - no genuine JSON report is large 1GB - this is mitgated by not allowing JSON reports more than 100MB</p>
<p>-An attacker could delete files outside OpCore-Simplify's workspace - which could lead to corrupting the operating system or introduce vulnerabilities</p>
Other fixes:
<p>Previously OpCore-Simplify if ran on Windows 8 or older versions gave errors that for non-experienced users are hard to understand. This is fixed by checking at the beginning of the batch file to check if that computer runs Windows 10 or newer and if not, to warn the user that this version of Windows is unsupported and stop executing anything.</p>
<p>On some Windows 10 versions, OpCore-Simplify's project can't execute properly - this is fixed by checking for updates right at the beginning of the batch file and adding a requirements file in the GitHub.</p>
<p>To updater.py, it is added an automated troubleshooter if any errors appear but are basic checks - for most OSes, it is for checking updates only, on Windows it is also about to run SFC /scannow and sometimes even check for Windows 11 requirements if they are met. And additional troubleshooter will be added for troubleshooting internet issues.</p>
