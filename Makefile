linux_version=4.6.2
linux=linux-$(linux_version)
riscv-linux-sha=8205b66a1104171284699985409ddd4d6921400d

all: linux pk

initramfs.txt: build-initram.py $(linux)
	./build-initram.py

busybox/.config: busybox_config
	cp -f $< $@

busybox/busybox: busybox/.config
	@echo "Building busybox."
	cd busybox && make menuconfig
	cd busybox && time make -j4

$(linux)/.config: linux_config
	cp -f $< $@

$(linux)/arch/riscv/initramfs.txt: initramfs.txt
	ln -sf ../../../$< $@
$(linux)/inittab: inittab
	ln -sf ../$< $@

$(linux):
	curl -L https://cdn.kernel.org/pub/linux/kernel/v4.x/$(linux).tar.xz | tar -xJ
	cd $(linux); git init;  git remote add -t master origin https://github.com/riscv/riscv-linux.git; git fetch; git checkout -f $(riscv-linux-sha)

linux: $(linux) $(linux)/.config $(linux)/arch/riscv/initramfs.txt busybox/busybox $(linux)/inittab
	@echo "Building riscv linux."
	cd $< && make ARCH=riscv menuconfig
	cd $< && time make -j4 ARCH=riscv vmlinux

pk:
	@echo "Building pk."
	time ./build-pk.sh

. PHONY: pk linux
