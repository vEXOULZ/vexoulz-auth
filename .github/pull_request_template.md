## What changed

## Checklist
- [ ] The branch is named per [Conventional Branch](../CONTRIBUTING.md#branches) (`feature/`, `bugfix/`, `hotfix/`, `release/`, `chore/`).
- [ ] A schema change is a new migration with a working downgrade (CI runs every revision down and up again).
- [ ] Nothing a site sends is trusted for more than it proves: return URLs, redirect URIs and origins are checked against the configuration.
- [ ] No Twitch token, client secret or session token is logged or returned to a browser.
- [ ] **No private infrastructure**: no hostnames of machines, IPs, server paths, proxy/tunnel config or deploy scripts. Those belong in the private homelab docs, not here.
