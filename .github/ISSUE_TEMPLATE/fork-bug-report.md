---
name: Fork bug report
about: Report a problem with the usable-windows fork build
title: "[fork] "
labels: fork
---

## Environment

- Fork commit (`git log --oneline -1`):
- Upstream sync SHA (from README sync table):
- Windows Python version (`python --version`):
- `certifi` installed? (`pip show certifi`):

## What happened

<!-- What did you run, and what failed? Paste the error output. -->

## Upstream reproduction

- [ ] I tested the same steps on pristine upstream `main` (`lzhoang2801/OpCore-Simplify`)
- Result upstream: <!-- same failure / works upstream / not tested -->

## Notes for triage

- If it reproduces on pristine upstream, the maintainer will link/open the upstream issue instead of tracking a full duplicate here.
- One root cause per issue; small focused PRs are preferred (see README sync table + CONTRIBUTING note).
