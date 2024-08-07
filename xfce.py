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

if len(sys.argv) != 2:
    print("Usage: script.py <username>")
    sys.exit(1)

username = sys.argv[1]

pkgs = [
    'git', 'neofetch', 'virglrenderer-android', 'papirus-icon-theme', 
    'xfce4', 'xfce4-goodies', 'eza', 'pavucontrol-qt', 'bat', 'jq', 
    'nala', 'wmctrl', 'firefox', 'netcat-openbsd', 'termux-x11-nightly'
]

# Install xfce4 desktop and additional packages
run_command(f"pkg install {' '.join(pkgs)} -y -o Dpkg::Options::='--force-confold'")

# Put Firefox icon on Desktop
run_command("cp $PREFIX/share/applications/firefox.desktop $HOME/Desktop")
run_command("chmod +x $HOME/Desktop/firefox.desktop")

# Set aliases
aliases = f"""
alias debian='proot-distro login debian --user {username} --shared-tmp'
alias hud='GALLIUM_HUD=fps '
alias ls='eza -lF --icons'
alias cat='bat '
alias apt='nala '
alias install='nala install -y '
alias uninstall='nala remove -y '
alias search='nala search '
alias list='nala list --upgradeable'
alias show='nala show'
"""
with open(os.path.join(os.getenv("PREFIX"), "etc/bash.bashrc"), "a") as bashrc:
    bashrc.write(aliases)

# Download Wallpaper
run_command("wget https://raw.githubusercontent.com/L4ur3nsk1s/Termux-XFCE-Custom/main/peakpx.jpg")
run_command("wget https://raw.githubusercontent.com/L4ur3nsk1s/Termux-XFCE-Custom/main/dark_waves.png")
run_command("mv peakpx.jpg $PREFIX/share/backgrounds/xfce/")
run_command("mv dark_waves.png $PREFIX/share/backgrounds/xfce/")

# Install WhiteSur-Dark Theme
run_command("wget https://github.com/vinceliuice/WhiteSur-gtk-theme/archive/refs/tags/2023-04-26.zip")
run_command("unzip 2023-04-26.zip")
run_command("tar -xf WhiteSur-gtk-theme-2023-04-26/release/WhiteSur-Dark-44-0.tar.xz")
run_command("mv WhiteSur-Dark/ $PREFIX/share/themes/")
run_command("rm -rf WhiteSur* 2023-04-26.zip")

# Install Fluent Cursor Icon Theme
run_command("wget https://github.com/vinceliuice/Fluent-icon-theme/archive/refs/tags/2023-02-01.zip")
run_command("unzip 2023-02-01.zip")
run_command("mv Fluent-icon-theme-2023-02-01/cursors/dist $PREFIX/share/icons/")
run_command("mv Fluent-icon-theme-2023-02-01/cursors/dist-dark $PREFIX/share/icons/")
run_command("rm -rf Fluent* 2023-02-01.zip")

# Setup Fonts
run_command("wget https://github.com/microsoft/cascadia-code/releases/download/v2111.01/CascadiaCode-2111.01.zip")
os.makedirs(".fonts", exist_ok=True)
run_command("unzip CascadiaCode-2111.01.zip")
run_command("mv otf/static/* .fonts/ && rm -rf otf")
run_command("mv ttf/* .fonts/ && rm -rf ttf/")
run_command("rm -rf woff2/ CascadiaCode-2111.01.zip")

run_command("wget https://github.com/ryanoasis/nerd-fonts/releases/download/v3.0.2/Meslo.zip")
run_command("unzip Meslo.zip")
run_command("mv *.ttf .fonts/")
run_command("rm Meslo.zip LICENSE.txt readme.md")

run_command("wget https://github.com/L4ur3nsk1s/Termux-XFCE-Custom/raw/main/NotoColorEmoji-Regular.ttf")
run_command("mv NotoColorEmoji-Regular.ttf .fonts")

run_command("wget https://github.com/L4ur3nsk1s/Termux-XFCE-Custom/raw/main/font.ttf")
run_command("mv font.ttf .termux/font.ttf")

# Setup Fancybash Termux
run_command("wget https://raw.githubusercontent.com/L4ur3nsk1s/Termux-XFCE-Custom/main/fancybash.sh")
run_command("mv fancybash.sh .fancybash.sh")
with open(os.path.join(os.getenv("PREFIX"), "etc/bash.bashrc"), "a") as bashrc:
    bashrc.write(f"source $HOME/.fancybash.sh\n")
run_command(f"sed -i '326s/\\\\u/{username}/' $HOME/.fancybash.sh")
run_command("sed -i '327s/\\\\h/termux/' $HOME/.fancybash.sh")

# Autostart Conky and Flameshot
run_command("wget https://github.com/L4ur3nsk1s/Termux-XFCE-Custom/raw/main/config.tar.gz")
run_command("tar -xvzf config.tar.gz")
run_command("rm config.tar.gz")
run_command("chmod +x .config/autostart/conky.desktop")
run_command("chmod +x .config/autostart/org.flameshot.Flameshot.desktop")
