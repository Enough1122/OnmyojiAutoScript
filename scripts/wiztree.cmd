@echo off
REM WizTree 一条龙：wiztree.cmd scan|report|folder|largest|top|search|types|filter ...
REM 例： wiztree.cmd report        wiztree.cmd folder "C:\Users\admin\AppData\Local"
python "%LOCALAPPDATA%\hermes\skills\personal\windows-disk-cleanup\scripts\wiztree.py" %*
