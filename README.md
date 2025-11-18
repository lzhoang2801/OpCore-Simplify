<br/>
<div align="center">
  <h3 align="center">OpCore Simplify Vulnerabilities fixes</h3>

  <p> ⚠️ Disclaimer: This fork of OpCore-Simplify exists solely to demonstrate and propose a fix for a different vulnerabilities found in this project. </p>
<p> It is not intended for general use or long-term maintenance. Users are strongly encouraged to use the official repository here https://github.com/lzhoang2801/OpCore-Simplify for stable and trusted releases. </p>
<p> This fork includes a proof-of-concept patch to mitigate all vulnerabilities. If accepted, it should be merged upstream. </p>
<p>Vulnerabilities that are mitigated in this project:</p>
<p>-an attacker could redirect kext downloads to malicious URLs - which could lead to placing malicious kexts in the EFI partition and then installing kernel level malware. This exploit is already in the wild - OpCore-Simplify2 (whose repo is https://github.com/w1842893/OpCore-Simplify2) already exploits this vulnerability. CVSS v3.1 Base Score: 8.8. It is mitigated by checking kexts against trusted repos.
<p>-it uses an outdated user agent of Google Chrome - Google Chrome 131. This opens also all vulnerabilities that Google has patched in newer versions of Chrome. And this opens also a vulnerability where websites redirect to outdated servers which can lead to even more vulnerabilities. CVSS v3.1 Base Score: 6.6. This exploit is mitigated by changing the user agent to the latest version of Safari - Safari 26.1.</p>
<p>- An attacker could upload a maliciously crafted JSON file that could execute files outside the OpCore-Simplify's folder - this is mitigated by not allowing the script to execute outside OpCore-Simplify's workspace. CVSS v3.1 Base Score: 9.8.</p>
<p>-An attacker could upload a specially crafted JSON file to crash the project or execute code - this is mitigated by denying uploads of invalid JSON files. CVSS v3.1 Base Score: 9.1.</p>
<p>-An attacker could upload an empty JSON file without triggering any warnings - this is mitigated by denying uploads of invalid JSON files. CVSS v3.1 Base Score: 5.3</p>
<p>-An attacker could upload oversized JSON files like 1GB JSON reports - no genuine JSON report is large 1GB - this is mitgated by not allowing JSON reports more than 100MB. CVSS v3.1 Base Score: 6.1.</p>
<p>-An attacker could delete files outside OpCore-Simplify's workspace - which could lead to corrupting the operating system or introduce vulnerabilities. CVSS v3.1 Base Score: 9.5</p>
<p> Oversized file uploads (DoS risk) - CVSS v3.1 Base Score: 6.1. This could lead to uploading too large files to exhaust CPU or RAM usage and crash the system. This is mitigated by enforcing 100MB file size limit. </p>
<p> Unreadable/malicious file crash - CVSS v3.1 Base Score: 5.9. This can lead to crashing the checker, leading to denial of service attacks. This is mitigated by adding try/except around file reads. </p>
<p> Blind trust in manifest - CVSS v3.1 Base Score: 8.2. This allows attackers to replace the manifest to hide malicious files or bypass detection. This is mitigated by adding HMAC signing of manifests. </p>
<p> Invalid/empty manifest acceptance - CVSS v3.1 Base Score: 9.1. This allows attackers to place empty or malformed manifests that could bypass integrity checks. This is mitigated by introducing schema validation for manifest structure.</p>
Other fixes:
<p>-Previously OpCore-Simplify if ran on Windows 8 or older versions gave errors that for non-experienced users are hard to understand. This is fixed by checking at the beginning of the batch file to check if that computer runs Windows 10 or newer and if not, to warn the user that this version of Windows is unsupported and stop executing anything.</p>
<p>-On some Windows 10 versions, OpCore-Simplify's project can't execute properly - this is fixed by checking for updates right at the beginning of the batch file.</p>
<p> Added a placeholder that is called __init__.py to fix Python libraries importing issues.</p>
<p>-To updater.py, it is added an automated troubleshooter if any errors appear but are basic checks - for most OSes, it is for checking updates only, on Windows it is also about to run SFC /scannow and sometimes even check for Windows 11 requirements if they are met or not and what this PC doesn't meet so the troubleshooter can upgrade if needed. And additional troubleshooter will be added for troubleshooting internet issues.</p>
<p>-Clarifying the user why their GPU is unsupported and kindly ask not to report issues for unsupported GPUs. And also open OpenCore Buyer's guide when unsupported GPUs detected.</p>
