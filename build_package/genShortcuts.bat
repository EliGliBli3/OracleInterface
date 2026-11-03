@echo off
setlocal

set "EXE_LINK=Oracle Interface"
set "LOGS_LINK=logs"

set "SCRIPT_DIR=%~dp0"
set /a OK=0, FAIL=0

call :MakeLink "%EXE_LINK%"  "%~dp0.\main\main.exe" "%~dp0.\main"      file
call :MakeLink "%LOGS_LINK%" "%~dp0.\main\logs"     "%~dp0.\main\logs" folder

echo.
exit /b 0


:MakeLink
for %%I in (%2) do set "TARGET_PATH=%%~fI"
for %%I in (%3) do set "WORK_DIR=%%~fI"
set "LINK_PATH=%SCRIPT_DIR%%~1.lnk"

if not exist "%TARGET_PATH%" (
    echo [SKIP] Not found: %TARGET_PATH%
    set /a FAIL+=1
    exit /b 1
)

if /i "%~4"=="folder" (
    set "ICON=%SystemRoot%\System32\imageres.dll,3"
    set "DESC=Open logs folder"
) else (
    set "ICON=%TARGET_PATH%,0"
    set "DESC=Launch main.exe"
)

powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command ^
  "$ws = New-Object -ComObject WScript.Shell;" ^
  "$sc = $ws.CreateShortcut($env:LINK_PATH);" ^
  "$sc.TargetPath = $env:TARGET_PATH;" ^
  "$sc.WorkingDirectory = $env:WORK_DIR;" ^
  "$sc.IconLocation = $env:ICON;" ^
  "$sc.Description = $env:DESC;" ^
  "$sc.Save()"

if errorlevel 1 (
    echo [ERROR] Failed to create %LINK_PATH%
    set /a FAIL+=1
    exit /b 1
)

echo [OK] %LINK_PATH%
set /a OK+=1
exit /b 0