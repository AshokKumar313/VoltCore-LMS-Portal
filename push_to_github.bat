@echo off
echo ========================================================
echo  VoltCore Apex Academia - GitHub Sync Utility
echo  Platform Lead: Ashok Kumar A (MIT Campus, Anna University)
echo ========================================================
echo.
echo Pushing local 'main' branch to:
echo https://github.com/AshokKumar313/VoltCore-LMS-Portal.git
echo.
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Repository successfully pushed to GitHub!
) else (
    echo [NOTICE] If prompted for authentication, log in via your browser or enter your GitHub Personal Access Token (PAT).
    echo Ensure you have created the repository 'VoltCore-LMS-Portal' at: https://github.com/new
)
echo.
pause

