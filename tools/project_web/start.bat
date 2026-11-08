@echo off
chcp 65001 >nul
title AI CAD - Quan ly Project
cd /d "%~dp0"
where py >nul 2>nul && (set PY=py) || (set PY=python)
start "" http://localhost:8780/
%PY% server.py
pause
