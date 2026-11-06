# dotfiles

Personal macOS and server configuration files (`~/.config`), editor settings, PgBouncer pooling configuration, and QEMU virtualization scripts.

## Structure

- **`.config/`**
  - `fish/config.fish` — Fish shell configuration and prompt settings.
  - `mpv/mpv.conf` — MPV media player playback and hardware decoding preferences.
  - `pip/pip.conf` — Global `pip` package index/install configuration.
  - `zed/settings.json` — Zed editor theme, font, and formatting settings.
- **`.vscode/settings.json`** — Visual Studio Code workspace/user preferences.
- **`.gitconfig`** — Global Git identity (`user.name`, `user.email`).
- **`.nanorc`** — GNU `nano` syntax highlighting (`/usr/local/Cellar/nano/*/share/nano/*.nanorc`), 4-space tabs, softwrap, autoindent, and minibar.
- **`pgbouncer/`**
  - `pgbouncer.ini` — Lightweight connection pooler configuration for PostgreSQL (`6432`).
  - `userlist.txt` — PgBouncer authentication user list.
- **`qemu.sh`** — `qemu-system-x86_64` launch commands using macOS Hypervisor.framework (`-accel hvf -vga vmware`) for Ubuntu Mini, Fedora Workstation, Haiku OS, and Windows XP virtual machines.
- **`commands.sh`** — Helpful CLI one-liners (e.g., bulk uninstalling global `pip3` packages).
