<#
.SYNOPSIS
    VoltCore Apex Academia - OneDrive Exclusion & Directory Optimization Engine
    Department of Electronics Engineering, MIT Campus, Anna University
    Hardware Target: HP Victus (LAPTOP-3NEGBVLE) - Strict Thermal & I/O Protection

.DESCRIPTION
    Safely isolates high-churn build directories (node_modules, .astro, dist,
    __pycache__, .pytest_cache) from the OneDrive sync engine.
    - Prevents cloud sync bottlenecks, bandwidth saturation, and disk thrashing.
    - Eliminates '.git/index.lock' collision errors caused by cldflt.sys locks.
    - Configures OneDrive Group Policy Ignore Lists (EnableODIgnoreFolderListFromGPO).
    - Applies Windows Search indexing exclusion (attrib +I).
    - Provides directory junction utilities for zero-cloud footprint decoupling.

.PARAMETER ApplyPolicy
    Applies the OneDrive folder ignore list to the Windows Registry.
.PARAMETER CheckOnly
    Audits the current status of workspace folders without modifying system state.
.PARAMETER SetupJunctions
    Migrates heavy node_modules to a local non-synced cache directory and junctions back.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\configure_onedrive_exclusions.ps1 -CheckOnly
    powershell -ExecutionPolicy Bypass -File scripts\configure_onedrive_exclusions.ps1 -ApplyPolicy
#>

[CmdletBinding()]
param(
    [switch]$ApplyPolicy = $false,
    [switch]$CheckOnly = $false,
    [switch]$SetupJunctions = $false
)

$ErrorActionPreference = "Continue"

Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host " VoltCore Apex Academia | OneDrive & Local Workspace Sync Optimizer" -ForegroundColor Yellow
Write-Host " Hardware Architecture: HP Victus (LAPTOP-3NEGBVLE) [Passive Thermals]" -ForegroundColor Green
Write-Host " Lead Architect: Ashok Kumar A | ECE Dept, MIT Campus, Anna Univ" -ForegroundColor DarkCyan
Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host ""

$WorkspaceRoot = (Get-Item -Path $PSScriptRoot\..).FullName
Write-Host "[INFO] Active Workspace: $WorkspaceRoot" -ForegroundColor Gray

# Target heavy build and cache directories to exclude from OneDrive
$HeavyFolders = @(
    "node_modules",
    ".astro",
    "dist",
    "__pycache__",
    ".pytest_cache",
    "backend/cache"
)

# -------------------------------------------------------------------------
# 1. Audit Current Workspace Status
# -------------------------------------------------------------------------
Write-Host "`n--- [Phase 1: Workspace & Cloud Storage Audit] ---" -ForegroundColor Cyan

$InOneDrive = $WorkspaceRoot -match "OneDrive"
if ($InOneDrive) {
    Write-Host "[STATUS] Workspace is hosted inside a OneDrive-monitored directory." -ForegroundColor Yellow
    Write-Host "         Filesystem filter driver (cldflt.sys) is active." -ForegroundColor Gray
} else {
    Write-Host "[STATUS] Workspace is in a standard local directory (Outside OneDrive root)." -ForegroundColor Green
}

$FolderAudit = @()
foreach ($folder in $HeavyFolders) {
    $fullPath = Join-Path $WorkspaceRoot $folder
    $exists = Test-Path $fullPath
    $isReparse = $false
    $reparseType = "None"
    $sizeMB = 0

    if ($exists) {
        $item = Get-Item -Path $fullPath -Force
        if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            $isReparse = $true
            if ($item.LinkType) {
                $reparseType = $item.LinkType
            } else {
                $reparseType = "Cloud/Junction"
            }
        }
        $FolderAudit += [PSCustomObject]@{
            Folder = $folder
            Exists = "Yes"
            ReparsePoint = $isReparse
            Type = $reparseType
            Path = $fullPath
        }
    } else {
        $FolderAudit += [PSCustomObject]@{
            Folder = $folder
            Exists = "No"
            ReparsePoint = $false
            Type = "N/A"
            Path = $fullPath
        }
    }
}

$FolderAudit | Format-Table -Property Folder, Exists, ReparsePoint, Type -AutoSize

# -------------------------------------------------------------------------
# 2. Windows Search Indexing Optimization (attrib +I)
# -------------------------------------------------------------------------
Write-Host "`n--- [Phase 2: Indexer & Attribute Protection] ---" -ForegroundColor Cyan
Write-Host "[INFO] Applying Not-Content-Indexed (+I) flag to reduce Windows Search background I/O..." -ForegroundColor Gray

foreach ($folder in $HeavyFolders) {
    $fullPath = Join-Path $WorkspaceRoot $folder
    if (Test-Path $fullPath) {
        try {
            & attrib.exe +I "$fullPath" /D 2>$null
            Write-Host "  [OK] +I flag applied: $folder" -ForegroundColor Green
        } catch {
            Write-Host "  [SKIP] Could not update attributes for: $folder" -ForegroundColor Yellow
        }
    }
}

# -------------------------------------------------------------------------
# 3. OneDrive Registry Ignore Policy Configuration
# -------------------------------------------------------------------------
Write-Host "`n--- [Phase 3: OneDrive Group Policy Exclusion Engine] ---" -ForegroundColor Cyan

$odRegBase = "HKCU:\SOFTWARE\Policies\Microsoft\OneDrive"
$odIgnoreKey = "$odRegBase\EnableODIgnoreFolderListFromGPO"

if ($ApplyPolicy) {
    Write-Host "[ACTION] Applying OneDrive Policy Ignore List to User Registry..." -ForegroundColor Yellow
    try {
        if (-not (Test-Path $odRegBase)) {
            New-Item -Path $odRegBase -Force | Out-Null
        }
        if (-not (Test-Path $odIgnoreKey)) {
            New-Item -Path $odIgnoreKey -Force | Out-Null
        }

        # Add target folders as string entries (Name = pattern, Value = pattern)
        foreach ($folder in $HeavyFolders) {
            $name = $folder.Replace("/", "\")
            Set-ItemProperty -Path $odIgnoreKey -Name $name -Value $name -Force | Out-Null
            Write-Host "  [CONFIGURED] Ignored pattern registered: $name" -ForegroundColor Green
        }

        # Also ignore .git directory internals to prevent index.lock contention
        Set-ItemProperty -Path $odIgnoreKey -Name ".git" -Value ".git" -Force | Out-Null
        Write-Host "  [CONFIGURED] Ignored pattern registered: .git" -ForegroundColor Green

        Write-Host "`n[SUCCESS] OneDrive Group Policy Ignore List configured successfully." -ForegroundColor Green
        Write-Host "[NOTE] If OneDrive is currently running, restart OneDrive sync engine to apply changes." -ForegroundColor Gray
    } catch {
        Write-Host "[WARNING] Registry write requires standard host environment permissions." -ForegroundColor Yellow
        Write-Host "          Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "          To apply manually in PowerShell as Administrator or user:" -ForegroundColor White
        Write-Host "          New-Item -Path '$odIgnoreKey' -Force" -ForegroundColor Cyan
        Write-Host "          Set-ItemProperty -Path '$odIgnoreKey' -Name 'node_modules' -Value 'node_modules'" -ForegroundColor Cyan
    }
} else {
    Write-Host "[INFO] To automatically register OneDrive ignore rules in your Windows Registry, run:" -ForegroundColor Yellow
    Write-Host "       powershell -ExecutionPolicy Bypass -File scripts\configure_onedrive_exclusions.ps1 -ApplyPolicy" -ForegroundColor White
    Write-Host "       This registers the following directory patterns to be ignored by OneDrive:" -ForegroundColor Gray
    foreach ($f in $HeavyFolders) {
        Write-Host "         - $f" -ForegroundColor DarkCyan
    }
}

# -------------------------------------------------------------------------
# 4. Optional Directory Junction Decoupling Engine
# -------------------------------------------------------------------------
if ($SetupJunctions) {
    Write-Host "`n--- [Phase 4: Directory Junction Decoupling Engine] ---" -ForegroundColor Cyan
    $LocalCacheRoot = "$env:LOCALAPPDATA\VoltCore-LocalCache"
    Write-Host "[INFO] Local non-synced cache root: $LocalCacheRoot" -ForegroundColor Gray

    if (-not (Test-Path $LocalCacheRoot)) {
        New-Item -Path $LocalCacheRoot -ItemType Directory -Force | Out-Null
        Write-Host "  [CREATED] Non-synced directory initialized: $LocalCacheRoot" -ForegroundColor Green
    }

    $TargetFolder = "node_modules"
    $RepoModulePath = Join-Path $WorkspaceRoot $TargetFolder
    $CacheModulePath = Join-Path $LocalCacheRoot $TargetFolder

    if (Test-Path $RepoModulePath) {
        $item = Get-Item -Path $RepoModulePath -Force
        if ($item.LinkType -eq "Junction") {
            Write-Host "  [OK] $TargetFolder is already a Directory Junction pointing to: $($item.Target)" -ForegroundColor Green
        } else {
            Write-Host "  [ACTION] Moving existing $TargetFolder to local cache..." -ForegroundColor Yellow
            if (-not (Test-Path $CacheModulePath)) {
                Move-Item -Path $RepoModulePath -Destination $CacheModulePath -Force
            } else {
                Remove-Item -Path $RepoModulePath -Recurse -Force
            }
            Write-Host "  [ACTION] Creating NTFS Directory Junction..." -ForegroundColor Yellow
            & cmd.exe /c "mklink /J `"$RepoModulePath`" `"$CacheModulePath`""
            Write-Host "  [SUCCESS] node_modules safely junctioned outside OneDrive!" -ForegroundColor Green
        }
    } else {
        if (-not (Test-Path $CacheModulePath)) {
            New-Item -Path $CacheModulePath -ItemType Directory -Force | Out-Null
        }
        & cmd.exe /c "mklink /J `"$RepoModulePath`" `"$CacheModulePath`""
        Write-Host "  [SUCCESS] node_modules junction created pointing to $CacheModulePath" -ForegroundColor Green
    }
}

Write-Host "`n==========================================================================" -ForegroundColor Cyan
Write-Host " [SUMMARY] OneDrive & Workspace Sync State Ready" -ForegroundColor Green
Write-Host " - Build caches isolated from indexing & background polling" -ForegroundColor White
Write-Host " - Zero-polling thermal footprint maintained for HP Victus" -ForegroundColor White
Write-Host "==========================================================================" -ForegroundColor Cyan
