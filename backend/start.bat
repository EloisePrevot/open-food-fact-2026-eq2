@echo off
setlocal
pushd "%~dp0"
call gradlew.bat run
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%
