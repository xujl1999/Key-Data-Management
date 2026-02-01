<#
Watch OneDrive Apple Health exports and auto-run the update pipeline.

Why
---
The Apple Health export -> OneDrive sync is easy to forget.
This watcher runs in a terminal and triggers parsing as soon as a new zip appears.

How to run
----------
1) Open PowerShell
2) cd D:\dream_life\data-management
3) powershell -ExecutionPolicy Bypass -File .\health\scripts\watch_onedrive.ps1

Stop with Ctrl+C.

Notes
-----
- This does NOT install a Windows service.
- It waits for file size/mtime to stabilize before triggering the pipeline.
- Update command is the same one you already use:
  python health/scripts/update_from_onedrive.py
#>

$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$SourceDir = Join-Path $env:USERPROFILE 'OneDrive\DATA'
$Pattern = '导出*.zip'

Write-Host "[watch] repoRoot=$RepoRoot"
Write-Host "[watch] sourceDir=$SourceDir"
Write-Host "[watch] pattern=$Pattern"

if (!(Test-Path $SourceDir)) {
  throw "Source directory not found: $SourceDir"
}

function Wait-StableFile {
  param(
    [string]$Path,
    [int]$TimeoutSec = 600,
    [int]$IntervalMs = 2000,
    [int]$StableChecks = 3
  )

  $start = Get-Date
  $last = $null
  $stable = 0

  while (((Get-Date) - $start).TotalSeconds -lt $TimeoutSec) {
    if (!(Test-Path $Path)) {
      Start-Sleep -Milliseconds $IntervalMs
      continue
    }

    $item = Get-Item $Path
    $current = "$($item.Length)|$($item.LastWriteTimeUtc.Ticks)"

    if ($current -eq $last) {
      $stable++
    } else {
      $stable = 0
      $last = $current
    }

    if ($stable -ge $StableChecks) {
      return $true
    }

    Start-Sleep -Milliseconds $IntervalMs
  }

  return $false
}

function Trigger-Update {
  param([string]$ZipPath)

  Write-Host "[watch] detected: $ZipPath"

  $ok = Wait-StableFile -Path $ZipPath
  if (!$ok) {
    Write-Warning "[watch] file did not stabilize in time: $ZipPath"
    return
  }

  Push-Location $RepoRoot
  try {
    Write-Host "[watch] running update_from_onedrive.py ..."
    python .\health\scripts\update_from_onedrive.py
    Write-Host "[watch] done"
  } finally {
    Pop-Location
  }
}

# Initial scan: print latest candidate (no trigger)
$latest = Get-ChildItem -Path $SourceDir -Filter $Pattern -ErrorAction SilentlyContinue |
  Sort-Object LastWriteTimeUtc, Length, Name -Descending |
  Select-Object -First 1

if ($latest) {
  Write-Host "[watch] current latest: $($latest.FullName)"
} else {
  Write-Host "[watch] no existing exports found yet"
}

$fsw = New-Object System.IO.FileSystemWatcher
$fsw.Path = $SourceDir
$fsw.Filter = '*.zip'
$fsw.IncludeSubdirectories = $false
$fsw.EnableRaisingEvents = $true

$action = {
  $full = $Event.SourceEventArgs.FullPath
  if ($full -notmatch [regex]::Escape('导出')) { return }
  if ($full -notlike "*$Pattern") { return }
  Trigger-Update -ZipPath $full
}

Register-ObjectEvent -InputObject $fsw -EventName Created -Action $action | Out-Null
Register-ObjectEvent -InputObject $fsw -EventName Changed -Action $action | Out-Null

Write-Host "[watch] watching... Ctrl+C to stop"
while ($true) {
  Start-Sleep -Seconds 1
}
