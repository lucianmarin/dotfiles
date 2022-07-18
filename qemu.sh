# linux
qemu-system-x86_64 -smp 2 -m 2048 -hda umini.img -accel hvf -vga vmware
qemu-system-x86_64 -m 2048 -hda umini.img -accel hvf -vga vmware -vnc :0,password -monitor stdio

# fedora
qemu-img create -f qcow2 fedora.img 16G
qemu-system-x86_64 -smp 2 -m 2048 -hda fedora.img -accel hvf -vga vmware -cdrom
Fedora-Workstation-Live-x86_64-36-1.5.iso
qemu-system-x86_64 -smp 2 -m 2048 -hda fedora.img -accel hvf -vga vmware 

# haiku
qemu-system-x86_64 -m 2048 -accel hvf -vga vmware -cdrom haiku-release-anyboot.iso
qemu-system-x86_64 -m 2048 -accel hvf -vga vmware -hda haiku.qcow2 -cdrom haiku-release-anyboot.iso
qemu-system-x86_64 -m 2048 -accel hvf -vga vmware -hda haiku.qcow2

# win
qemu-system-x86_64 -m 2048 -hda xp.qcow2 -accel hvf -vga vmware -soundhw ac97 -net nic,model=rtl8139 -net user -cdrom WXPVOL_EN.iso
