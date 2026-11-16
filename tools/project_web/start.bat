@echo off
chcp 65001 >nul
title AI CAD - Quan ly Project
cd /d "%~dp0"
rem Server dang chay (cong 8780 dang nghe) thi chi mo trang web, khong chay lai server.
netstat -ano | findstr /r /c:":8780 .*LISTENING" >nul
if not errorlevel 1 (
  start "" http://localhost:8780/
  exit /b
)
where py >nul 2>nul && (set PY=py) || (set PY=python)
rem Mo trang sau 2 giay de server kip khoi dong
start "" /min cmd /c "timeout /t 2 >nul & start http://localhost:8780/"
%PY% server.py
pause
