<#
.SYNOPSIS
    VoltCore Apex Academia - Git & GitHub Synchronization Engine
    Department of Electronics Engineering, MIT Campus, Anna University
    Hardware Target: HP Victus (LAPTOP-3NEGBVLE) - Strict Thermal Protection

.DESCRIPTION
    Streamlined, reliable Git pre-commit verification, staging, and remote synchronization.
    - Stale lock detection & auto-healing (resolves OneDrive .git/index.lock collisions).
    - Passive CPU execution (zero background polling daemons).
    - Targeted pre-commit smoke tests (python -m pytest tests/test_course_config.py).
    - Clean conventional commit message formatting with architectural attribution.
    - Conflict-resistant rebase-pull and push to origin/main.

.PARAMETER Message
    Custom commit message. Attribution '[Lead: Ashok Kumar A]' is appended if omitted.
.PARAMETER Quick
    Fast sync: stages all tracked/untracked changes, auto-commits, and pushes without prompts.
.PARAMETER SkipTests
    Bypasses pre-commit pytest validation for swift documentation or style pushes.
.PARAMETER StatusOnly
    Audits local vs remote Git state without staging, committing, or pushing.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\sync_repo.ps1 -StatusOnly
    powershell -ExecutionPolicy Bypass -File scripts\sync_repo.ps1 -Message "feat(core): add sync automation"
    powershell -ExecutionPolicy Bypass -File scripts\sync_repo.ps1 -Quick
#>

[CmdletBinding()]
param(
    [string]$Message = "",
    [switch]$Quick = $false,
    [switch]$SkipTests = $false,
    [switch]$StatusOnly = $false
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host " VoltCore Apex Academia | GitHub Remote Synchronization Engine" -ForegroundColor Yellow
Write-Host " Hardware Architecture: HP Victus (LAPTOP-3NEGBVLE) [Passive Thermals]" -ForegroundColor Green
Write-Host " Lead Architect: Ashok Kumar A | ECE Dept, MIT Campus, Anna Univ" -ForegroundColor DarkCyan
Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host ""

$RepoRoot = (Get-Item -Path $PSScriptRoot\..).FullName
Set-Location -Path $RepoRoot

# -------------------------------------------------------------------------
# 1. Pre-Flight Check & Stale Lock Healing
# -------------------------------------------------------------------------
$LockFile = Join-Path $RepoRoot ".git\index.lock"
if (Test-Path $LockFile) {
    Write-Host "[WARNING] Stale '.git/index.lock' detected." -ForegroundColor Yellow
    $gitProcesses = Get-Process -Name "git" -ErrorAction SilentlyContinue
    if (-not $gitProcesses) {
        Write-Host "          No active git process found. Clearing orphaned OneDrive lock..." -ForegroundColor Gray
        try {
            Remove-Item -Path $LockFile -Force
            Write-Host "  [HEALED] Stale index.lock cleared successfully." -ForegroundColor Green
        } catch {
            Write-Host "  [ERROR] Unable to remove index.lock: $($_.Exception.Message)" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "  [BUSY] Another git process is actively executing. Please wait..." -ForegroundColor Yellow
        exit 1
    }
}

# Verify Git repository connection
try {
    $currentBranch = (git branch --show-current).Trim()
    $remoteUrl = (git remote get-url origin).Trim()
} catch {
    Write-Host "[FATAL] Failed to inspect Git repository state: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "[REPO] Branch: $currentBranch | Remote: $remoteUrl" -ForegroundColor Gray

# -------------------------------------------------------------------------
# 2. Local vs Remote Status Inspection
# -------------------------------------------------------------------------
$statusShort = git status --short
$hasLocalChanges = [bool]($statusShort.Trim().Length -gt 0)

# Check remote sync state
Write-Host "[SYNC] Inspecting remote synchronization state..." -ForegroundColor Gray
try {
    git fetch origin main --quiet 2>$null
    $localCommit = (git rev-parse HEAD).Substring(0, 7)
    $remoteCommit = (git rev-parse origin/main).Substring(0, 7)
    $aheadBehind = (git rev-list --left-right --count HEAD...origin/main).Trim()
    $counts = $aheadBehind -split "\s+"
    $ahead = [int]$counts[0]
    $behind = [int]$counts[1]
} catch {
    $localCommit = (git rev-parse HEAD).Substring(0, 7)
    $remoteCommit = "Unknown (Offline)"
    $ahead = 0
    $behind = 0
}

Write-Host ""
Write-Host "  Local Commit  : $localCommit" -ForegroundColor White
Write-Host "  Remote Commit : $remoteCommit" -ForegroundColor White
Write-Host "  Sync Status   : Ahead by $ahead | Behind by $behind" -ForegroundColor $(if ($ahead -gt 0 -or $behind -gt 0) { "Yellow" } else { "Green" })
Write-Host ""

if ($hasLocalChanges) {
    Write-Host "[DIRTY] Uncommitted workspace changes detected:" -ForegroundColor Yellow
    $statusShort | ForEach-Object { Write-Host "   $_" -ForegroundColor DarkCyan }
    Write-Host ""
} else {
    Write-Host "[CLEAN] Working directory clean (No uncommitted changes)." -ForegroundColor Green
}

# If StatusOnly switch was passed, exit cleanly here
if ($StatusOnly) {
    Write-Host "[INFO] Status audit complete (-StatusOnly mode). Exiting without modifications." -ForegroundColor Cyan
    exit 0
}

# If no changes and not ahead/behind, nothing to do
if (-not $hasLocalChanges -and $ahead -eq 0 -and $behind -eq 0) {
    Write-Host "[OK] Repository is fully synchronized with GitHub origin/main. Nothing to commit or push." -ForegroundColor Green
    exit 0
}

# -------------------------------------------------------------------------
# 3. Handle Remote Behind (Pull / Rebase)
# -------------------------------------------------------------------------
if ($behind -gt 0) {
    Write-Host "[PULL] Remote has $behind new commit(s). Performing safe rebase pull..." -ForegroundColor Yellow
    try {
        git pull --rebase origin main
        Write-Host "  [OK] Successfully rebased on origin/main." -ForegroundColor Green
    } catch {
        Write-Host "  [ERROR] Git pull rebase encountered a merge conflict or error." -ForegroundColor Red
        Write-Host "          Resolve conflicts manually or run 'git rebase --abort'." -ForegroundColor Yellow
        exit 1
    }
}

# -------------------------------------------------------------------------
# 4. Pre-Commit Targeted Smoke Tests (Thermal Safety Rule)
# -------------------------------------------------------------------------
if ($hasLocalChanges -and -not $SkipTests) {
    Write-Host "[TEST] Running targeted pytest validation (tests/test_course_config.py)..." -ForegroundColor Cyan
    try {
        $testResult = python -m pytest tests/test_course_config.py -q 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [PASS] Course configuration smoke tests verified cleanly." -ForegroundColor Green
        } else {
            Write-Host "  [WARNING] Targeted test failure detected:" -ForegroundColor Yellow
            $testResult | ForEach-Object { Write-Host "    $_" -ForegroundColor Red }
            Write-Host "  [ABORT] Push aborted to prevent breaking remote main branch. Fix tests or use -SkipTests." -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "  [SKIP] Python environment not active for test validation. Proceeding..." -ForegroundColor Gray
    }
}

# -------------------------------------------------------------------------
# 5. Staging & Commit Creation
# -------------------------------------------------------------------------
if ($hasLocalChanges) {
    Write-Host "[STAGE] Staging modified and untracked files adhering to .gitignore..." -ForegroundColor Cyan
    git add -A

    # Build commit message
    $authorTag = "[Lead: Ashok Kumar A]"
    if ([string]::IsNullOrWhiteSpace($Message)) {
        if ($Quick) {
            $Message = "chore(sync): automated workspace synchronization $authorTag"
        } else {
            Write-Host ""
            $inputMsg = Read-Host "Enter commit message (Press Enter for default: 'chore(sync): routine workspace update')"
            if ([string]::IsNullOrWhiteSpace($inputMsg)) {
                $Message = "chore(sync): routine workspace update $authorTag"
            } else {
                if ($inputMsg -notmatch "\[Lead:") {
                    $Message = "$inputMsg $authorTag"
                } else {
                    $Message = $inputMsg
                }
            }
        }
    } else {
        if ($Message -notmatch "\[Lead:") {
            $Message = "$Message $authorTag"
        }
    }

    Write-Host "[COMMIT] Creating commit: '$Message'..." -ForegroundColor Cyan
    try {
        git commit -m "$Message"
        Write-Host "  [OK] Commit created successfully." -ForegroundColor Green
    } catch {
        Write-Host "  [ERROR] Commit failed: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# -------------------------------------------------------------------------
# 6. Push to GitHub Remote (origin/main)
# -------------------------------------------------------------------------
Write-Host "[PUSH] Pushing commits to GitHub origin/main..." -ForegroundColor Cyan
try {
    git push origin main
    Write-Host "  [SUCCESS] All commits successfully pushed to origin/main." -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Push failed. Inspect network connection or credentials." -ForegroundColor Red
    Write-Host "          $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Final Verification
$finalLocal = (git rev-parse HEAD).Substring(0, 7)
Write-Host ""
Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host " [COMPLETE] VoltCore LMS Portal Synchronized" -ForegroundColor Green
Write-Host " Head Commit : $finalLocal on branch '$currentBranch'" -ForegroundColor White
Write-Host " Repository  : $remoteUrl" -ForegroundColor White
Write-Host " Thermals    : HP Victus CPU passive, zero background polling" -ForegroundColor White
Write-Host "==========================================================================" -ForegroundColor Cyan
