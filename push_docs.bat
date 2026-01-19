@echo off
set "GIT_EXE=C:\Program Files\Git\bin\git.exe"

"%GIT_EXE%" add docs/
"%GIT_EXE%" commit -m "Deploy portfolio to docs/ for GitHub Pages"
"%GIT_EXE%" push origin main
