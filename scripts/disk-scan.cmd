@echo off
REM 一键磁盘体检：提权扫描 + 三档候选清单（✅可清 / ⚠️拍板 / ⛔禁删）
REM 用法: disk-scan.cmd [盘符]      例如 disk-scan.cmd D:\
setlocal
set SKILL=%LOCALAPPDATA%\hermes\skills\personal\windows-disk-cleanup\scripts
set DRIVE=%1
if "%DRIVE%"=="" set DRIVE=C:\
python "%SKILL%\wiztree.py" scan "%DRIVE%"
if errorlevel 1 goto :eof
python "%SKILL%\wiztree.py" report
endlocal
