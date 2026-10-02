# Weekly sync checklist (fork `main` mirror)

Run from a clone with `origin` = fork and `upstream` = `lzhoang2801/OpCore-Simplify`.

1. `git checkout main && git fetch upstream`
2. Compare: `git rev-parse main upstream/main`
   - Same SHA → nothing to merge. Update the README sync table `Last checked` date and push.
   - Behind → `git merge --ff-only upstream/main`. If fast-forward fails, record the conflict in the sync commit message (rebase notes) instead of force-pushing silently.
3. Update the README sync table (`Upstream baseline`, `Last checked`) and push `main`.
4. Rebase `usable-windows` onto the new `main` only if it fast-forwards cleanly; otherwise keep the last tagged snapshot and note the divergence.
5. Cut a new `usable-YYYY-MM-DD` tag only after the hardware-report menu boots on Windows (see README fork notes).

Dry-run 2026-10-02: `main` == `upstream/main` (`e5d8a9f`), no merge needed.
