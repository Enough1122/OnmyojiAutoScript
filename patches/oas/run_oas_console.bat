@echo off
cd /d D:\Hermes\repos\OAS
title OAS-Server (oas_daily)
toolkit\python.exe start_oas.py
echo.
echo [start_oas.py exited] window kept open to hold the console handle.
pause
