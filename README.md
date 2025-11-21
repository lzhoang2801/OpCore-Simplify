<br/>
<div align="center">
  <h3 align="center">OpCore Simplify Vulnerabilities fixes</h3>

  <p> ⚠️ Disclaimer: This fork of OpCore-Simplify exists solely to demonstrate and propose a fix for a different vulnerabilities found in this project. And also it adds minor fixes to this project that can make this project even more user friendly. </p>
<p> It is not intended for general use or long-term maintenance. Users are strongly encouraged to use the official repository here https://github.com/lzhoang2801/OpCore-Simplify for stable and trusted releases. </p>
<p> This fork includes a proof-of-concept patch to mitigate all vulnerabilities. If accepted, it should be merged upstream. </p>
<p>Vulnerabilities that are mitigated in this project:</p>
<p>-An attacker could delete files outside OpCore-Simplify's workspace - which could lead to corrupting the operating system or introduce vulnerabilities. CVSS v3.1 Base Score: 9.5</p>
<p> Oversized file uploads (DoS risk) - CVSS v3.1 Base Score: 6.1. This could lead to uploading too large files to exhaust CPU or RAM usage and crash the system. This is mitigated by enforcing 100MB file size limit. </p>
<p> Unreadable/malicious file crash - CVSS v3.1 Base Score: 5.9. This can lead to crashing the checker, leading to denial of service attacks. This is mitigated by adding try/except around file reads. </p>
<p> Another zero day vulnerability: Blind trust in manifest - CVSS v3.1 Base Score: 8.2. This allows attackers to replace the manifest to hide malicious files or bypass detection. This is mitigated by adding HMAC signing of manifests. </p>
<p> Another 0 day exploit: Invalid/empty manifest acceptance - CVSS v3.1 Base Score: 9.1. This allows attackers to place empty or malformed manifests that could bypass integrity checks. This is mitigated by introducing schema validation for manifest structure.</p>
<p> Another 0 day exploit: command injection via shell=True - CVSS v3.1 Base Score: 9.8. This can lead to arbitary code execution with full user privileges. This is mitigated by removing shell=True; arguments are being sanitized and passed safely to subprocess.Popen. </p>
<p> Another 0 day exploit: Unvalidated commands - CVSS v3.1 Base Score: 8.2. An attacker could execute unintended or malicious binaries. It is mitigated by making a whitelist of allowed commands (ls, cp, mv, etc.); rejects anything outside of this range.</p>
</p> Another 0 day exploit: Path traversal / workspace escape - CVSS v3.1 Base Score: 9.1. Attackers could gain access to sensitive files outside the project's scope. It is mitigated by rejecting absolute paths unless inside safe_cwd using os.path.commonpath.
<p> Uncontrolled environment - CVSS v3.1 Base Score: 7.4. Attakers could exploit enviornment variables to hijack execution. It is mitigated by using minimal, sanitized environment (PATH, LANG, LC_ALL).</p>
<p> Resource exhaustion (DoS) - CVSS v3.1 Base Score: 5.1. Attackers can crash or freeze via infinite loops or massive output. This is mitigated by adding timeouts (default 5 min) and output size caps (10MB). </p>
<p> Output injection / log spoofing - CVSS v3.1 Base Score: 6.5. Attackers can mislead logs and escape sequence injection. This is mitigated by sanitizing output by stripping non‑printable characters and ANSI escapes. </p>
<p> Silent error handling - CVSS v3.1 Base Score: 7.9. Attackers can hide exploitation attempts, so making these exploitation attempts harder to debug. So attackers can make it next to impossible to debug exploitation attempts. It is mitigated by making specific exception handling with structured error messages.</p>

Other fixes:
<p>-Previously OpCore-Simplify if ran on Windows 8 or older versions gave errors that for non-experienced users are hard to understand. This is fixed by checking at the beginning of the batch file to check if that computer runs Windows 10 or newer and if not, to warn the user that this version of Windows is unsupported and stop executing anything.</p>
<p>-On some Windows 10 versions, OpCore-Simplify's project can't execute properly - this is fixed by checking for updates right at the beginning of the batch file.</p>
<p> Added a placeholder that is called __init__.py to fix Python libraries importing issues.</p>
<p>-Clarifying the user why their GPU is unsupported and kindly ask not to report issues for unsupported GPUs. And also open OpenCore Buyer's guide when unsupported GPUs detected.</p>
<p>-If the user uses Legacy BIOS and first gen i3/i5/i7 to clarify them that OpenCore is not recommended and to expect instability.</p>
