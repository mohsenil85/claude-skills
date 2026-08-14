---
name: health
description: Run a full homelab health check across all hosts and services
---

# Health Check

Run a comprehensive health scan of the entire homelab using the sysadmin MCP.

## Process

1. Call the `mcp__sysadmin__health` tool
2. Present the results clearly — highlight any warnings or errors at the top
3. If anything looks concerning, suggest next steps (e.g., "torrent VPN is down — check NordVPN service" or "zdata scrub is 15 days old — consider running one")

## Notes

- The health tool checks: host reachability (ping), ZFS pool status + capacity, scrub ages, disk temperatures, Proxmox VM status, UPS (NUT), NFS exports, VPN (torrent + slskd), and backup freshness
- All checks run in parallel so this takes ~10-15 seconds total
- Hosts running HAOS (homeassistant) and LibreELEC (kodi) are skipped for ping
- VPN check compares external IP against home IP — if they match, VPN is down
- Disk temp threshold is 45C, pool capacity threshold is 85%, scrub staleness threshold is 14 days, backup staleness threshold is 26 hours
