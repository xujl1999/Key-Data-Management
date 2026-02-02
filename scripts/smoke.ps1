<#
Smoke test runner (PowerShell)

A tiny, reproducible experiment to quickly verify the local "health" toolchain.
It intentionally avoids service restarts or privileged operations.

What it does
- Runs health doctor checks (data quality + dashboard json)
- Runs dashboard updater in "dry" mode (network enabled) by default; if you want to avoid
  network calls, pass -NoNetwork.

Usage
  pwsh -File scripts/smoke.ps1
  pwsh -File scripts/smoke.ps1 -Days 7
  pwsh -File scripts/smoke.ps1 -NoNetwork

Notes
- This is meant for local dev and CI (future).
- Exit code is non-zero if doctor reports issues.
#>

param(
  [int]$Days = 14,
  [switch]$NoNetwork
)

$ErrorActionPreference = 'Stop'

Write-Host "[smoke] python: $(python -V)" -ForegroundColor Cyan

Write-Host "[smoke] running health doctor (--days $Days)" -ForegroundColor Cyan
python health/scripts/doctor.py --days $Days
$doctorExit = $LASTEXITCODE

if ($doctorExit -ne 0) {
  Write-Host "[smoke] doctor exit code: $doctorExit" -ForegroundColor Yellow
}

if (-not $NoNetwork) {
  Write-Host "[smoke] updating dashboard_data.json (network calls enabled)" -ForegroundColor Cyan
  python health/scripts/update_dashboard_data.py
  if ($LASTEXITCODE -ne 0) {
    throw "update_dashboard_data.py failed"
  }
} else {
  Write-Host "[smoke] skipping dashboard update due to -NoNetwork" -ForegroundColor Yellow
}

if ($doctorExit -ne 0) {
  exit $doctorExit
}

Write-Host "[smoke] OK" -ForegroundColor Green
exit 0
