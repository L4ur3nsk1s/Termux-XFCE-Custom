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

if len(sys.argv) != 2:
    print("Usage: script.py <username>")
    sys.exit(1)

username = sys.argv[1]

try:
    # Register the finish function to be called on exit
    import atexit
    atexit.register(finish)

    pkgs_proot = ['sudo', 'wget', 'nala', 'jq', 'flameshot', 'conky-all']

    # Install Debian proot
    run_command("pd install debian")
    run_command("pd login debian --shared-tmp -- env DISPLAY=:1.0 apt update")
    run_command("pd login debian --shared-tmp -- env DISPLAY=:1.0 apt upgrade -y")
    run_command(f"pd login debian --shared-tmp -- env DISPLAY=:1.0 apt install {' '.join(pkgs_proot)} -y -o Dpkg::Options::='--force-confold'")

    # Create user
    run_command(
        "pd login debian --shared-tmp -- env DISPLAY=:1.0 groupadd storage"
    )
    run_command("pd login debian --shared-tmp -- env DISPLAY=:1.0 groupadd wheel")
    run_command(f"pd login debian --shared-tmp -- env DISPLAY=:1.0 useradd -m -g users -G wheel,audio,video,storage -s /bin/bash {username}")

    # Add user to sudoers
    sudoers_path = os.path.join(os.getenv("PREFIX"), "var/lib/proot-distro/installed-rootfs/debian/etc/sudoers")
    run_command(f"chmod u+rw {sudoers_path}")
    with open(sudoers_path, "a") as sudoers_file:
        sudoers_file.write(f"{username} ALL=(ALL) NOPASSWD:ALL\n")
    run_command(f"chmod u-w {sudoers_path}")

    # Set proot DISPLAY
    bashrc_path = os.path.join(os.getenv("PREFIX"), f"var/lib/proot-distro/installed-rootfs/debian/home/{username}/.bashrc")
    with open(bashrc_path, "a") as bashrc:
        bashrc.write("export DISPLAY=:1.0\n")

    # Set proot aliases
    aliases = """
alias zink='MESA_LOADER_DRIVER_OVERRIDE=zink TU_DEBUG=noconform '
alias hud='GALLIUM_HUD=fps '
alias ls='eza -lF --icons'
alias cat='bat '
alias apt='sudo nala '
alias install='sudo nala install -y '
alias remove='sudo nala remove -y '
alias list='nala list --upgradeable'
alias show='nala show '
alias search='nala search '
alias start='echo please run from termux, not Debian proot.'
"""
    with open(bashrc_path, "a") as bashrc:
        bashrc.write(aliases)

    # Set proot timezone
    timezone = os.popen("getprop persist.sys.timezone").read().strip()
    run_command(
        "pd login debian --shared-tmp -- env DISPLAY=:1.0 rm /etc/localtime"
    )
    run_command(f"pd login debian --shared-tmp -- env DISPLAY=:1.0 cp /usr/share/zoneinfo/{timezone} /etc/localtime")

    # Setup Fancybash Proot
    run_command(f"cp .fancybash.sh {os.getenv('PREFIX')}/var/lib/proot-distro/installed-rootfs/debian/home/{username}")
    with open(bashrc_path, "a") as bashrc:
        bashrc.write("source ~/.fancybash.sh\n")
    run_command(f"sed -i '327s/termux/proot/' {os.getenv('PREFIX')}/var/lib/proot-distro/installed-rootfs/debian/home/{username}/.fancybash.sh")

    run_command("wget https://github.com/L4ur3nsk1s/Termux-XFCE-Custom/raw/main/conky.tar.gz")
    run_command("tar -xvzf conky.tar.gz")
    run_command("rm conky.tar.gz")
    run_command(f"mkdir -p {os.getenv('PREFIX')}/var/lib/proot-distro/installed-rootfs/debian/home/{username}/.config")
    run_command(f"mv .config/conky/ {os.getenv('PREFIX')}/var/lib/proot-distro/installed-rootfs/debian/home/{username}/.config")
    run_command(f"mv .config/neofetch {os.getenv('PREFIX')}/var/lib/proot-distro/installed-rootfs/debian/home/{username}/.config")

    # Set theming from XFCE to proot
    run_command(f"cp -r {os.getenv('PREFIX')}/share/icons/dist-dark {os.getenv('PREFIX')}/var/lib/proot-distro/installed-rootfs/debian/usr/share/icons/dist-dark")
    with open(os.path.join(os.getenv('PREFIX'), f"var/lib/proot-distro/installed-rootfs/debian/home/{username}/.Xresources"), "w") as xresources:
        xresources.write("Xcursor.theme: dist-dark\n")

    run_command(f"mkdir -p {os.getenv('PREFIX')}/var/lib/proot-distro/installed-rootfs/debian/home/{username}/.fonts/")
    run_command(f"cp .fonts/NotoColorEmoji-Regular.ttf {os.getenv('PREFIX')}/var/lib/proot-distro/installed-rootfs/debian/home/{username}/.fonts/")

    # Setup Hardware Acceleration
    run_command("pd login debian --shared-tmp -- env DISPLAY=:1.0 wget https://github.com/L4ur3nsk1s/Termux-XFCE-Custom/raw/main/mesa-vulkan-kgsl_24.1.0-devel-20240120_arm64.deb")
    run_command("pd login debian --shared-tmp -- env DISPLAY=:1.0 sudo apt install -y ./mesa-vulkan-kgsl_24.1.0-devel-20240120_arm64.deb")

except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)
