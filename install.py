#!/usr/bin/env python3

import os
import subprocess
import sys

def run_command(command):
    """Run a command and handle errors."""
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with error: {e}")
        sys.exit(1)

def finish():
    ret = os.WEXITSTATUS(os.system("echo $?"))
    if ret not in (0, 130):
        print("\nERROR: Failed to setup XFCE on Termux.")
        print("Please refer to the error message(s) above")

try:
    # Register the finish function to be called on exit
    import atexit
    atexit.register(finish)

    # Clear the terminal
    os.system("clear")

    print("\nThis script will install XFCE Desktop in Termux along with a Debian proot\n")
    username = input("Please enter username for proot installation: ")

    run_command("termux-change-repo")
    run_command("pkg update -y -o Dpkg::Options::='--force-confold'")
    run_command("pkg upgrade -y -o Dpkg::Options::='--force-confold'")
    run_command("sed -i '12s/^#//' $HOME/.termux/termux.properties")

    # Display a message and wait for a single character input
    os.system("clear -x")
    print("\nSetting up Termux Storage access.\n")
    input("Press any key to continue...")
    run_command("termux-setup-storage")

    pkgs = ['wget', 'python', 'ncurses-utils', 'dbus', 'proot-distro', 'x11-repo', 'tur-repo', 'pulseaudio']

    run_command("pkg uninstall dbus -y")
    run_command("pkg update")
    run_command(f"pkg install {' '.join(pkgs)} -y -o Dpkg::Options::='--force-confold'")

    # Create default directories
    os.makedirs("Desktop", exist_ok=True)
    os.makedirs("Downloads", exist_ok=True)

    # Download required install scripts
    run_command("wget https://github.com/L4ur3nsk1s/Termux-XFCE-Custom/raw/main/xfce.py")
    run_command("wget https://github.com/L4ur3nsk1s/Termux-XFCE-Custom/raw/main/proot.py")
    run_command("wget https://github.com/L4ur3nsk1s/Termux-XFCE-Custom/raw/main/utils.py")
    run_command("chmod +x *.py")

    run_command(f"./xfce.py {username}")
    run_command(f"./proot.py {username}")
    run_command("./utils.py")

    # Display a message and wait for a single character input
    os.system("clear -x")
    print("\nInstalling Termux-X11 APK\n")
    input("Press any key to continue...")
    run_command("wget https://github.com/termux/termux-x11/releases/download/nightly/app-arm64-v8a-debug.apk")
    run_command("mv app-arm64-v8a-debug.apk $HOME/storage/downloads/")
    run_command("termux-open $HOME/storage/downloads/app-arm64-v8a-debug.apk")

    run_command("source $PREFIX/etc/bash.bashrc")
    run_command("termux-reload-settings")

    os.system("clear -x")
    print("\n\nSetup completed successfully!\n")
    print("You can now connect to your Termux XFCE4 Desktop to open the desktop use the command start")
    print("\nThis will start the termux-x11 server in termux and start the XFCE Desktop and then open the installed Termux-X11 app.")
    print("\nTo exit, double click the Kill Termux X11 icon on the panel.")
    print("\nEnjoy your Termux XFCE4 Desktop experience!\n\n")

    os.remove("xfce.py")
    os.remove("proot.py")
    os.remove("utils.py")
    os.remove("install.py")

except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)
