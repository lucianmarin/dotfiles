# uninstall pip3
pip3 freeze | xargs pip3 uninstall -y

# download wavevision1 youtube playlist
youtube-dl -f 140 -i https://www.youtube.com/watch?list=UUlB4Qjqka4uZrSaysagUa5Q

# convert SVG to PNG
qlmanage -t -s 160 -o . teal.svg; mv teal.svg.png 160.png

# archive with rsync
rsync -ar --del /source /destination

# convert to iso
hdiutil makehybrid -iso -joliet -o name.iso name.cdr

# qemu
qemu-system-x86_64 -smp threads=2 -m 2048 -accel hvf -vga virtio -hda haiku.qcow2 -full-screen -cdrom haiku-release-anyboot.iso
qemu-img create -f qcow2 vdisk.qcow2 4G
