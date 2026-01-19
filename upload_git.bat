@echo off
setlocal

:: Clear conflicting git environment variables
set GIT_EXEC_PATH=
set GIT_DIR=
set GIT_WORK_TREE=

:: Path to Git - Using the one verified to exist
set "GIT_EXE=C:\Program Files\Git\bin\git.exe"

echo Follow this script to upload...
echo.

"%GIT_EXE%" init
"%GIT_EXE%" add .
"%GIT_EXE%" commit -m "Agentic upload of full project"
"%GIT_EXE%" branch -M main

:: Remove origin if it exists to clean up previous attempts
"%GIT_EXE%" remote remove origin
"%GIT_EXE%" remote add origin https://github.com/Samritsec/-F-tenshiguard_ai-.git

echo Pushing to GitHub...
"%GIT_EXE%" push -u origin main

echo.
echo Done.
