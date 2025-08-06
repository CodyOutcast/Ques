@echo off
set /p CVM_IP="Enter your CVM IP address: "
set /p SSH_USER="Enter your SSH user (default: root): "
if "%SSH_USER%"=="" set SSH_USER=root

echo Uploading deployment package to %SSH_USER%@%CVM_IP%...

REM Using WinSCP or similar tool would be recommended for Windows
echo Please use WinSCP, FileZilla, or similar tool to upload this folder to:
echo %SSH_USER%@%CVM_IP%:/opt/ques-backend/
echo.
echo Or use WSL/Git Bash to run: upload_to_cvm.sh
pause
