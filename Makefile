
# Some configuration.
LINUX_VERSION=4.6.2
RISCV-LINUX-SHA=8205b66a1104171284699985409ddd4d6921400d

linux=linux-$(LINUX_VERSION)


all: bblvmlinux

# This setups the repository for automatic generation of ramdisk images
# by running through the manual configuration stages of linux and busybox
setup: busybox/.config.old $(linux)/.config.old

###############################################################################
# Get sources and configure
###############################################################################

# Busybox is a submodule. Init it before commencing
busybox/.config: busybox_config
	cp -f $< $@

# Configure busybox. Hopefully this is a NOP!
busybox/.config.old: busybox/.config
	make -C $(@D) oldconfig

# Fetch linux sources and apply RISCV patch
$(linux):
	curl -L https://cdn.kernel.org/pub/linux/kernel/v4.x/$(linux).tar.xz | tar -xJ
	cd $(linux); git init;  git remote add -t master origin https://github.com/riscv/riscv-linux.git; git fetch; git checkout -f $(RISCV-LINUX-SHA)

$(linux)/.config: linux_config $(linux)
	cp -f $< $@

# Configure linux. Hopefully this is a nop.
$(linux)/.config.old: $(linux)/.config
	make -C $(@D) ARCH=riscv oldconfig

###############################################################################
# Build
###############################################################################

initramfs.txt: build-initram.py $(linux)
	./build-initram.py

busybox/busybox: busybox/.config.old profile
	@echo "Building busybox."
	time make -C $(@D) -j

$(linux)/vmlinux: $(linux)/.config.old initramfs.txt busybox/busybox
	@echo "Building riscv linux."
	time make -C $(@D) -j ARCH=riscv vmlinux

bblvmlinux: $(linux)/vmlinux
	@echo "Building an bbl instance with your payload."
	time ./build-pk.sh

clean:
	rm -rf $(linux) initramfs.txt bblvmlinux
	cd busybox && git clean -x -d -f

.PHONY: setup all clean
