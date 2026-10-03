[CmdletBinding()]
param(
    [ValidateSet('Both', 'Codex', 'Claude')]
    [string]$Target = 'Both',
    [string]$ProfileDirectory = $env:USERPROFILE
)

$ErrorActionPreference = 'Stop'
$source = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot 'skill/full-stack')).Path
if (-not $ProfileDirectory) { throw 'Supply -ProfileDirectory for the target user.' }
$profileRoot = [IO.Path]::GetFullPath($ProfileDirectory)
$relativeRoots = @()
if ($Target -in @('Both', 'Codex')) { $relativeRoots += '.agents/skills/full-stack' }
if ($Target -in @('Both', 'Claude')) { $relativeRoots += '.claude/skills/full-stack' }
$sourceFiles = @(Get-ChildItem -LiteralPath $source -Recurse -File)
$expected = @{}
foreach ($file in $sourceFiles) {
    $expected[$file.FullName.Substring($source.Length + 1)] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
}

# Preflight both destinations before overwriting either. Never follow a redirected
# install root or silently keep obsolete instructions from an older package.
$destinations = @($relativeRoots | ForEach-Object { Join-Path $profileRoot $_ })
foreach ($destination in $destinations) {
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
    if (Test-Path -LiteralPath $destination) {
        foreach ($item in Get-ChildItem -LiteralPath $destination -Recurse -Force) {
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Redirected install entry: $($item.FullName)" }
            if (-not $item.PSIsContainer) {
                $relative = $item.FullName.Substring($destination.Length + 1)
                if (-not $expected.ContainsKey($relative)) { throw "Unexpected installed file; preserve or relocate it before reinstalling: $($item.FullName)" }
            }
        }
    }
}

foreach ($destination in $destinations) {
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    foreach ($file in $sourceFiles) {
        $relative = $file.FullName.Substring($source.Length + 1)
        $copy = Join-Path $destination $relative
        New-Item -ItemType Directory -Path (Split-Path -Parent $copy) -Force | Out-Null
        Copy-Item -LiteralPath $file.FullName -Destination $copy -Force
        if ((Get-FileHash -LiteralPath $copy -Algorithm SHA256).Hash -ne $expected[$relative]) {
            throw "Installed file differs from source: $copy"
        }
    }
    Write-Output "Installed and SHA256-verified $($sourceFiles.Count) files: $destination"
}
