# Contributing back (PR-back rule)

Upstream merges slowly (3 PRs sat 2-9 months), so keep every proposal reviewable in under 15 minutes:

1. **One root cause per PR.** Never bundle SSL, scraper, and iasl changes together.
2. **Link reproduction evidence.** Each PR references the failing command/URL/log and the upstream issue number it fixes.
3. **Branch from a clean `main` mirror.** PR branches start at the synced upstream tip, never from `usable-windows` (which carries fork-only docs).
4. **Fork stays usable regardless.** Every PR notes the fork commit carrying the fix so daily use is never blocked on a merge.
