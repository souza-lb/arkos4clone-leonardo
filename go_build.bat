@echo off
echo Building DTB Selector for all platforms...

echo Building Windows 32-bit...
set GOOS=windows
set GOARCH=386
go build -ldflags="-s -w" -o dtb_selector_win32.exe dtb_selector.go

@REM echo Building Windows 64-bit...
@REM set GOOS=windows
@REM set GOARCH=amd64
@REM go build -ldflags="-s -w" -o dtb_selector_win64.exe dtb_selector.go

echo Building macOS Intel...
set GOOS=darwin
set GOARCH=amd64
go build -ldflags="-s -w" -o dtb_selector_macos_intel dtb_selector.go

echo Building macOS Apple Silicon...
set GOOS=darwin
set GOARCH=arm64
go build -ldflags="-s -w" -o dtb_selector_macos_apple dtb_selector.go

@REM echo Building Linux 64-bit...
@REM set GOOS=linux
@REM set GOARCH=amd64
@REM go build -ldflags="-s -w" -o dtb_selector_linux dtb_selector.go

echo.
echo Build completed!
echo.
echo Generated files:
echo   dtb_selector_win32.exe      - Windows 32-bit
echo   dtb_selector_win64.exe      - Windows 64-bit  
echo   dtb_selector_macos_intel    - macOS Intel
echo   dtb_selector_macos_apple    - macOS Apple Silicon
echo   dtb_selector_linux          - Linux 64-bit