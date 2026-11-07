# VoltCore Apex Academia: Synchronization & Workflow Guide
**Department of Electronics Engineering | MIT Campus, Anna University**  
*Regulation 2023 | Hardware Architecture: HP Victus (`LAPTOP-3NEGBVLE`)*  
*Lead Systems Architect: Ashok Kumar A*  

---

## 1. Executive Summary & Architecture Overview

The **VoltCore Apex Academia** portal operates across a three-way synchronization topology:
1. **Local VS Code Workspace**: Active code editing, Vite HMR, and local test runs on your HP Victus laptop.
2. **Microsoft OneDrive Cloud Mirror**: Windows Documents cloud backup via the NTFS Cloud Files Filter Driver (`cldflt.sys`).
3. **GitHub Remote Repository (`origin/main`)**: Canonical version control repository at `https://github.com/AshokKumar313/VoltCore-LMS-Portal.git`.

```
               +-------------------------------------------+
               |         GitHub Remote Repository          |
               | (https://github.com/AshokKumar313/...)    |
               +-------------------------------------------+
                                   ^
                                   | Git HTTPS (Push / Rebase Pull)
                                   v
+--------------------------------------------------------------------------+
|                     HP VICTUS (LAPTOP-3NEGBVLE)                          |
|                                                                          |
|   +--------------------------+         +-------------------------------+ |
|   |    VS Code Workspace     | <=====> | OneDrive Sync Engine          | |
|   |  - files.watcherExclude  |  Local  |  - cldflt.sys filter driver   | |
|   |  - Smart Commit active   |  I/O    |  - EnableODIgnoreFolderList   | |
|   |  - Zero Polling Daemons  |         |  - attrib +I index exclusions | |
|   +--------------------------+         +-------------------------------+ |
|                 |                                      |                 |
|                 +------------------+-------------------+                 |
|                                    v                                     |
|                      Target Heavy Directories:                           |
|                      - node_modules/   - dist/                           |
|                      - .astro/         - __pycache__/                    |
|                      - .pytest_cache/  - backend/cache/                  |
+--------------------------------------------------------------------------+
```

---

## 2. Root Cause Analysis: OneDrive & Git Contention

When a Git repository resides inside a OneDrive-synced folder, two significant friction points emerge on Windows:

### A. The `.git/index.lock` Collision
- **Mechanism**: Whenever Git prepares a staging or commit operation, it creates a temporary lock file: `.git/index.lock`.
- **OneDrive Interference**: OneDrive's file system filter driver (`cldflt.sys`) immediately intercepts the creation of `.git/index.lock` to inspect metadata and compute hashes for cloud backup.
- **The Failure**: When Git finishes writing and attempts to atomically rename or delete `index.lock`, Windows rejects the call with `WinError 32: The process cannot access the file because it is being used by another process` or `fatal: Unable to create '.git/index.lock': File exists / Permission denied`.

### B. Thermal Throttling & Fan Noise on HP Victus
- **Mechanism**: The workspace contains over 40,000 files across `node_modules`, `.astro`, and `dist`.
- **VS Code Overhead**: By default, VS Code's file watcher (Chokidar) scans all 40,000+ files for modifications.
- **OneDrive Overhead**: OneDrive syncs every temporary cache file generated during Vite HMR or `npm run build`.
- **The Result**: CPU utilization jumps to 15-30% on idle, triggering aggressive laptop fan spin and thermal throttling.

---

## 3. The VoltCore Optimization Architecture

VoltCore solves both challenges through four coordinated layers:

### Layer 1: VS Code Workspace Exclusions (`.vscode/settings.json`)
We have configured `.vscode/settings.json` to instruct VS Code to completely ignore high-churn cache folders:
- **`files.watcherExclude`**: Ignores `node_modules/**`, `.astro/**`, `dist/**`, `__pycache__/**`, `.pytest_cache/**`, and `.git/objects/**`. File watcher CPU drops to **< 0.5%**.
- **`search.exclude`**: Fast, instantaneous text searching without indexing gigabytes of third-party libraries.
- **`git.autofetch: false`**: Disables periodic background Git polling. Prevents spurious authentication prompts, rate limits, and `.git/FETCH_HEAD` lock collisions.
- **`git.enableSmartCommit: true`**: Allows frictionless 1-click commits directly from the VS Code Source Control tab.

### Layer 2: Windows Search & Indexing Isolation (`attrib +I`)
Run `scripts/configure_onedrive_exclusions.ps1` to apply the **Not Content Indexed (`+I`)** NTFS attribute across all cache directories:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\configure_onedrive_exclusions.ps1 -CheckOnly
```
This commands the Windows Search Indexer (`SearchIndexer.exe`) to skip these directories, protecting SSD write cycles and CPU thermals.

### Layer 3: OneDrive Group Policy Exclusions (`EnableODIgnoreFolderListFromGPO`)
OneDrive supports an official registry-based folder ignore policy:
- **Registry Key**: `HKCU:\SOFTWARE\Policies\Microsoft\OneDrive\EnableODIgnoreFolderListFromGPO`
- **Ignored Patterns**:
  - `node_modules`
  - `.astro`
  - `dist`
  - `__pycache__`
  - `.pytest_cache`
  - `.git`
To apply this policy to your user account, execute:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\configure_onedrive_exclusions.ps1 -ApplyPolicy
```

### Layer 4: Optional Directory Junction Decoupling (`mklink /J`)
For developers desiring **100% physical separation** between heavy build artifacts and OneDrive:
- `node_modules` can be relocated to `%LOCALAPPDATA%\VoltCore-LocalCache\node_modules` (outside OneDrive).
- An NTFS Directory Junction is created inside the repository:
  ```cmd
  mklink /J "node_modules" "%LOCALAPPDATA%\VoltCore-LocalCache\node_modules"
  ```
- **Why it works**: OneDrive **does not follow NTFS directory junctions**. `node_modules` becomes invisible to OneDrive while Node, Vite, and Astro access it at native SSD speeds.
- To execute automatically:
  ```powershell
  powershell -ExecutionPolicy Bypass -File scripts\configure_onedrive_exclusions.ps1 -SetupJunctions
  ```

---

## 4. Daily Synchronization Workflows

You have two seamless options for daily development:

### Option A: VS Code Graphical Interface (Fast & Visual)
1. **Stage & Review**: Open the **Source Control** view (`Ctrl + Shift + G`). Click `+` on specific files or stage all.
2. **Commit**: Type your message in the commit box (e.g., `feat(course): update unit III simulator notes [Lead: Ashok Kumar A]`) and press `Ctrl + Enter`.
3. **Sync**: Click the **Sync Changes** button in the VS Code status bar (bottom left) to pull and push in one click.

### Option B: The VoltCore 1-Click Sync Engine (CLI / Script)
We provide an automated, self-healing synchronization script:
- PowerShell: `scripts/sync_repo.ps1`
- Batch Wrapper: `scripts/sync_repo.bat`

#### 1. Quick Non-Interactive Sync
Stages all modifications, creates a standard conventional commit, and pushes to GitHub:
```powershell
.\scripts\sync_repo.bat -Quick
```
*(or via PowerShell)*:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\sync_repo.ps1 -Quick
```

#### 2. Custom Message Sync with Pre-Commit Verification
Runs targeted pytest checks (`tests/test_course_config.py`) to verify curriculum integrity, creates the commit with your message and attribution, and pushes:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\sync_repo.ps1 -Message "feat(quiz): add assessment engine"
```

#### 3. Status Audit Only (Read-Only)
Checks local vs remote commit status and dirty file list without modifying anything:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\sync_repo.ps1 -StatusOnly
```

---

## 5. Self-Healing & Troubleshooting Reference

### Issue: "fatal: Unable to create '.git/index.lock': File exists"
- **Cause**: OneDrive or an interrupted process held a handle to `.git/index.lock`.
- **Fix**: Run `.\scripts\sync_repo.bat`. The script automatically checks whether a real `git.exe` process is running. If not, it safely removes the orphaned lock and proceeds.
- **Manual Fix**:
  ```powershell
  if (Test-Path .git\index.lock) { Remove-Item -Force .git\index.lock }
  ```

### Issue: "Permission denied (publickey)" or GitHub Auth Prompts
- **Fix**: Verify your GitHub connection:
  ```powershell
  git remote -v
  ```
  Ensure credentials are stored in Windows Credential Manager:
  ```powershell
  git config --global credential.helper manager
  ```

### Issue: High Fan Noise / Laptop Running Hot
- Confirm VS Code workspace settings are active:
  Verify `.vscode/settings.json` contains `files.watcherExclude`.
- Confirm no background servers are left running. Kill any orphaned node or python tasks:
  ```powershell
  Get-Process node, python -ErrorAction SilentlyContinue | Format-Table Id, ProcessName, CPU
  ```

---

## 6. Verification Checklist

| Checkpoint | Target State | Command to Verify |
| :--- | :--- | :--- |
| **VS Code File Watcher** | Heavy folders excluded | Check `.vscode/settings.json` |
| **Indexing Isolation** | Not Content Indexed (`+I`) | `attrib node_modules` -> displays `I` |
| **Stale Lock Auto-Healing** | Clean or Auto-Healed | `powershell scripts\sync_repo.ps1 -StatusOnly` |
| **Remote Branch** | Synchronized with `origin/main` | `git status` -> `working tree clean` |
| **Thermal Budget** | Passive CPU (<8%) | Windows Task Manager / Victus Dashboard |

---
*VoltCore Apex Academia — Department of Electronics Engineering, MIT Campus, Anna University.*
