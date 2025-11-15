<br/>
<div align="center">
  <h3 align="center">OpCore Simplify Vulnerability fix that allows attackers to inject malicious kexts</h3>

  <p> ⚠️ Disclaimer: This fork of OpCore-Simplify exists solely to demonstrate and propose a fix for a different vulnerabilities found in this project. </p>
<p> It is not intended for general use or long-term maintenance. Users are strongly encouraged to use the official repository here https://github.com/lzhoang2801/OpCore-Simplify for stable and trusted releases. </p>
<p> This fork includes a proof-of-concept patch to mitigate all vulnerabilities. If accepted, it should be merged upstream. </p>
<p>1 of the exploits will be mitigated by adding SHA2 checks. </p>
<p> This exploit is already in the wild. At least 1-3 gits have exploited this vulnerability to inject malicious kexts into the EFI for persistance. And no antivirus can flag such a low level malware, which makes this exploit even more dangerous. </p>
<p> Another exploit found in this project is that it uses an outdated user agent of Google Chrome - Google Chrome 131. This opens also all vulnerabilities that Google has patched in newer versions of Chrome. This exploit is mitigated by changing the user agent to the latest version of Safari.</p>
<p> And this project also has minor bug fixes too, by the way.</p>
