[CmdletBinding()]
param(
    [ValidateSet('Both', 'Codex', 'Claude')]
    [string]$Target = 'Both',
    [string]$ProfileDirectory = $env:USERPROFILE,
    [switch]$Preview
)

$ErrorActionPreference = 'Stop'
$source = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot 'skill/full-stack')).Path
if (-not $ProfileDirectory) { throw 'Supply -ProfileDirectory for the target user.' }
$profileRoot = [IO.Path]::GetFullPath($ProfileDirectory)
$relativeRoots = @()
if ($Target -in @('Both', 'Codex')) { $relativeRoots += '.agents/skills/full-stack' }
if ($Target -in @('Both', 'Claude')) { $relativeRoots += '.claude/skills/full-stack' }

# The source must be ordinary files too; a redirected source would install
# content from outside this checkout.
if ((Get-Item -LiteralPath $source -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
    throw "Package source must be an ordinary directory: $source"
}
$sourceFiles = @(Get-ChildItem -LiteralPath $source -Recurse -Force | Where-Object {
    if ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Redirected package entry: $($_.FullName)" }
    -not $_.PSIsContainer
})
$expected = @{}
foreach ($file in $sourceFiles) {
    $expected[$file.FullName.Substring($source.Length + 1)] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
}

# Preflight every destination before changing any. Never follow a redirected
# install root or silently keep obsolete instructions from an older package.
$plans = @()
foreach ($relativeRoot in $relativeRoots) {
    $destination = Join-Path $profileRoot $relativeRoot
    $cursor = $destination
    while ($cursor) {
        if (Test-Path -LiteralPath $cursor) {
            $item = Get-Item -LiteralPath $cursor -Force
            if (-not $item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
                throw "Install path must be an ordinary directory: $cursor"
            }
        }
        $cursor = Split-Path -Parent $cursor
    }
    $changed = @()
    if (Test-Path -LiteralPath $destination) {
        foreach ($item in Get-ChildItem -LiteralPath $destination -Recurse -Force) {
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Redirected install entry: $($item.FullName)" }
            if (-not $item.PSIsContainer) {
                $relative = $item.FullName.Substring($destination.Length + 1)
                if (-not $expected.ContainsKey($relative)) { throw "Unexpected installed file; preserve or relocate it before reinstalling: $($item.FullName)" }
            }
        }
        foreach ($relative in $expected.Keys) {
            $installed = Join-Path $destination $relative
            if (-not (Test-Path -LiteralPath $installed) -or (Get-FileHash -LiteralPath $installed -Algorithm SHA256).Hash -ne $expected[$relative]) {
                $changed += $relative
            }
        }
        $state = if ($changed.Count) { 'update' } else { 'unchanged' }
    } else {
        $state = 'new'
    }
    $plans += [pscustomobject]@{ Host = $relativeRoot.Split('/')[0].TrimStart('.'); Destination = $destination; State = $state; Changed = $changed }
}

foreach ($plan in $plans) {
    Write-Output "$($plan.State): $($plan.Destination)"
    foreach ($relative in $plan.Changed) { Write-Output "  differs from source (local edit or older package): $relative" }
}
if ($Preview) { Write-Output 'Preview only; nothing was copied.'; return }

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
foreach ($plan in $plans | Where-Object { $_.State -ne 'unchanged' }) {
    $destination = $plan.Destination
    $parent = Split-Path -Parent $destination
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    # Stage beside the destination so the final move stays on one volume.
    $staging = Join-Path $parent ".full-stack.staging-$PID"
    $backup = $null
    try {
        foreach ($file in $sourceFiles) {
            $relative = $file.FullName.Substring($source.Length + 1)
            $copy = Join-Path $staging $relative
            New-Item -ItemType Directory -Path (Split-Path -Parent $copy) -Force | Out-Null
            Copy-Item -LiteralPath $file.FullName -Destination $copy
            if ((Get-FileHash -LiteralPath $copy -Algorithm SHA256).Hash -ne $expected[$relative]) {
                throw "Staged file differs from source: $copy"
            }
        }
        if ($plan.State -eq 'update') {
            # Backups live outside every skills directory so hosts never load them.
            $backupRoot = Join-Path $profileRoot '.full-stack-backups'
            New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
            $backup = Join-Path $backupRoot "$($plan.Host)-$stamp"
            Move-Item -LiteralPath $destination -Destination $backup
        }
        try {
            Move-Item -LiteralPath $staging -Destination $destination
        } catch {
            if ($backup) { Move-Item -LiteralPath $backup -Destination $destination }
            throw
        }
    } finally {
        if (Test-Path -LiteralPath $staging) { Remove-Item -LiteralPath $staging -Recurse -Force }
    }
    Write-Output "Installed and SHA256-verified $($sourceFiles.Count) files: $destination"
    if ($backup) { Write-Output "  previous copy kept at: $backup" }
}
