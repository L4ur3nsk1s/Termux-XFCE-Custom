#!/usr/bin/env python3

import os
import subprocess

def run_command(command):
    """Run a command and handle errors."""
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with error: {e}")
        exit(1)

# Function to create and set permissions for scripts
def create_script(script_path, content):
    with open(script_path, 'w') as file:
        file.write(content)
    run_command(f"chmod +x {script_path}")

# Set PREFIX variable
PREFIX = os.getenv("PREFIX")

# Create prun script
prun_script = f"""#!/bin/bash
varname=$(basename {PREFIX}/var/lib/proot-distro/installed-rootfs/debian/home/*)
pd login debian --user $varname --shared-tmp -- env DISPLAY=:1.0 $@
"""
create_script(f"{PREFIX}/bin/prun", prun_script)

# Create zrun script
zrun_script = f"""#!/bin/bash
varname=$(basename {PREFIX}/var/lib/proot-distro/installed-rootfs/debian/home/*)
pd login debian --user $varname --shared-tmp -- env DISPLAY=:1.0 MESA_LOADER_DRIVER_OVERRIDE=zink TU_DEBUG=noconform $@
"""
create_script(f"{PREFIX}/bin/zrun", zrun_script)

# Create zrunhud script
zrunhud_script = f"""#!/bin/bash
varname=$(basename {PREFIX}/var/lib/proot-distro/installed-rootfs/debian/home/*)
pd login debian --user $varname --shared-tmp -- env DISPLAY=:1.0 MESA_LOADER_DRIVER_OVERRIDE=zink TU_DEBUG=noconform GALLIUM_HUD=fps $@
"""
create_script(f"{PREFIX}/bin/zrunhud", zrunhud_script)

# Create cp2menu script
cp2menu_script = f"""#!/bin/bash

cd

user_dir="{PREFIX}/var/lib/proot-distro/installed-rootfs/debian/home/"

# Get the username from the user directory
username=$(basename "$user_dir"/*)

action=$(zenity --list --title="Choose Action" --text="Select an action:" --radiolist --column="" --column="Action" TRUE "Copy .desktop file" FALSE "Remove .desktop file")

if [[ -z $action ]]; then
  zenity --info --text="No action selected. Quitting..." --title="Operation Cancelled"
  exit 0
fi

if [[ $action == "Copy .desktop file" ]]; then
  selected_file=$(zenity --file-selection --title="Select .desktop File" --file-filter="*.desktop" --filename="{PREFIX}/var/lib/proot-distro/installed-rootfs/debian/usr/share/applications")

  if [[ -z $selected_file ]]; then
    zenity --info --text="No file selected. Quitting..." --title="Operation Cancelled"
    exit 0
  fi

  desktop_filename=$(basename "$selected_file")

  cp "$selected_file" "{PREFIX}/share/applications/"
  sed -i "s/^Exec=\\(.*\\)$/Exec=pd login debian --user $username --shared-tmp -- env DISPLAY=:1.0 \\1/" "{PREFIX}/share/applications/$desktop_filename"

  zenity --info --text="Operation completed successfully!" --title="Success"
elif [[ $action == "Remove .desktop file" ]]; then
  selected_file=$(zenity --file-selection --title="Select .desktop File to Remove" --file-filter="*.desktop" --filename="{PREFIX}/share/applications")

  if [[ -z $selected_file ]]; then
    zenity --info --text="No file selected for removal. Quitting..." --title="Operation Cancelled"
    exit 0
  fi

  desktop_filename=$(basename "$selected_file")

  rm "$selected_file"

  zenity --info --text="File '$desktop_filename' has been removed successfully!" --title="Success"
fi
"""
create_script(f"{PREFIX}/bin/cp2menu", cp2menu_script)

# Create cp2menu.desktop
cp2menu_desktop = """[Desktop Entry]
Version=1.0
Type=Application
Name=cp2menu
Comment=
Exec=cp2menu
Icon=edit-move
Categories=System;
Path=
Terminal=false
StartupNotify=false
"""
cp2menu_desktop_path = f"{PREFIX}/share/applications/cp2menu.desktop"
create_script(cp2menu_desktop_path, cp2menu_desktop)

# Create app-installer script
app_installer_script = f"""#!/bin/bash

# Define the directory paths
INSTALLER_DIR="$HOME/.App-Installer"
REPO_URL="https://github.com/phoenixbyrd/App-Installer.git"
DESKTOP_DIR="$HOME/Desktop"
APP_DESKTOP_FILE="$DESKTOP_DIR/app-installer.desktop"

# Check if the directory already exists
if [ ! -d "$INSTALLER_DIR" ]; then
    # Directory doesn't exist, clone the repository
    git clone "$REPO_URL" "$INSTALLER_DIR"
    if [ $? -eq 0 ]; then
        echo "Repository cloned successfully."
    else
        echo "Failed to clone repository. Exiting."
        exit 1
    fi
else
    echo "Directory already exists. Skipping clone."
    "$INSTALLER_DIR/app-installer"
fi

# Check if the .desktop file exists
if [ ! -f "$APP_DESKTOP_FILE" ]; then
    # .desktop file doesn't exist, create it
    echo "[Desktop Entry]
    Version=1.0
    Type=Application
    Name=App Installer
    Comment=
    Exec={PREFIX}/bin/app-installer
    Icon=package-install
    Categories=System;
    Path=
    Terminal=false
    StartupNotify=false
" > "$APP_DESKTOP_FILE"
    chmod +x "$APP_DESKTOP_FILE"
fi

# Ensure the app-installer script is executable
chmod +x "$INSTALLER_DIR/app-installer"
"""
create_script(f"{PREFIX}/bin/app-installer", app_installer_script)

run_command(f"bash {PREFIX}/bin/app-installer")

# Create app-installer.desktop
app_installer_desktop = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=App Installer
Comment=
Exec={PREFIX}/bin/app-installer
Icon=package-install
Categories=System;
Path=
Terminal=false
StartupNotify=false
"""
app_installer_desktop_path = os.path.expanduser("~/Desktop/app-installer.desktop")
create_script(app_installer_desktop_path, app_installer_desktop)

# Create start script
start_script = """#!/bin/bash

# Enable PulseAudio over Network
pulseaudio --start --load="module-native-protocol-tcp auth-ip-acl=127.0.0.1 auth-anonymous=1" --exit-idle-time=-1 > /dev/null 2>&1

XDG_RUNTIME_DIR=${TMPDIR} termux-x11 :1.0 & > /dev/null 2>&1
sleep 1

am start --user 0 -n com.termux.x11/com.termux.x11.MainActivity > /dev/null 2>&1
sleep 1

MESA_NO_ERROR=1 MESA_GL_VERSION_OVERRIDE=4.3COMPAT MESA_GLES_VERSION_OVERRIDE=3.2 virgl_test_server_android --angle-gl & > /dev/null 2>&1

env DISPLAY=:1.0 GALLIUM_DRIVER=virpipe dbus-launch --exit-with-session xfce4-session & > /dev/null 2>&1
# Set audio server
export PULSE_SERVER=127.0.0.1 > /dev/null 2>&1

sleep 5
process_id=$(ps -aux | grep '[x]fce4-screensaver' | awk '{{print $2}}')
kill "$process_id" > /dev/null 2>&1
"""
start_script_path = f"{PREFIX}/bin/start"
create_script(start_script_path, start_script)

# Create kill_termux_x11 script
kill_termux_x11_script = """#!/bin/bash

# Check if Apt, dpkg, or Nala is running in Termux or Proot
if pgrep -f 'apt|apt-get|dpkg|nala'; then
  zenity --info --text="Software is currently installing in Termux or Proot. Please wait for these processes to finish before continuing."
  exit 1
fi

# Get the process IDs of Termux-X11 and XFCE sessions
termux_x11_pid=$(pgrep -f /system/bin/app_process.*com.termux.x11.Loader)
xfce_pid=$(pgrep -f "xfce4-session")

# Add debug output
echo "Termux-X11 PID: $termux_x11_pid"
echo "XFCE PID: $xfce_pid"

# Check if the process IDs exist
if [ -n "$termux_x11_pid" ] && [ -n "$xfce_pid" ]; then
  # Kill the processes
  kill -9 "$termux_x11_pid" "$xfce_pid"
  zenity --info --text="Termux-X11 and XFCE sessions closed."
else
  zenity --info --text="Termux-X11 or XFCE session not found."
fi

info_output=$(termux-info)
pid=$(echo "$info_output" | grep -o 'TERMUX_APP_PID=[0-9]\\+' | awk -F= '{{print $2}}')
kill "$pid"

exit 0
"""
create_script(f"{PREFIX}/bin/kill_termux_x11", kill_termux_x11_script)

# Create kill_termux_x11.desktop
kill_termux_x11_desktop = """[Desktop Entry]
Version=1.0
Type=Application
Name=Kill Termux X11
Comment=
Exec=kill_termux_x11
Icon=system-shutdown
Categories=System;
Path=
StartupNotify=false
"""
kill_termux_x11_desktop_path = os.path.expanduser("~/Desktop/kill_termux_x11.desktop")
create_script(kill_termux_x11_desktop_path, kill_termux_x11_desktop)
run_command(f"mv {kill_termux_x11_desktop_path} {PREFIX}/share/applications")
