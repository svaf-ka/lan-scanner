# LAN Scanner

Simple desktop app that scans your local network (LAN) and lists connected devices with their IP address, hostname and MAC address.

![LAN Scanner screenshot](screenshot.png)

## Features

- Detects your router's IP automatically (you can change it)
- Scans the whole `/24` subnet (254 addresses) in a few seconds
- Shows IP address, hostname and MAC address of every device
- Marks the router and your own computer
- Simple window with a progress bar, no terminal needed
- No external dependencies, only the Python standard library

## How it works

1. Pings every address in the subnet in parallel.
2. Reads the system ARP table to find devices that responded.
3. Resolves hostnames with reverse DNS (devices without a name show `-`).

## Run

You need Python 3.

```
python skaner_gui.py
```

Click **Skanuj** (Scan). The results appear in the table.

## Build a Windows .exe

Double-click `zbuduj_exe.bat`. It installs PyInstaller and builds the app.
The finished file is in the `dist` folder as `Skaner sieci.exe`.

Windows SmartScreen may show a warning because the file is not signed.
That is normal for self-built programs.

## Notes

- Built and tested on Windows. It should also work on Linux and macOS
  (on Linux you may need to install `python3-tk`).
- Assumes a `/24` subnet, which is the most common home setup.

## Disclaimer

Use this tool only on your own network or on networks you have permission to scan.

## License

MIT
