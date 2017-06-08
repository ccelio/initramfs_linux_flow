
# Some configuration.
LINUX_VERSION=4.1.17
RISCV-LINUX-BRANCH=master
RISCV-LINUX-SHA=174f395

linux=linux-$(LINUX_VERSION)


all: vmlinux

initramfs: initramfs.txt

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
	cd $(linux); \
	git init; \
	git remote add -t $(RISCV-LINUX-BRANCH) origin https://github.com/riscv/riscv-linux.git; \
	git fetch --all; git checkout -f $(RISCV-LINUX-SHA)

#$(linux)/.config: linux_config $(linux)
#	cp -f $< $@

# Configure linux. Hopefully this is a nop.
#$(linux)/.config.old: $(linux)/.config
#	make -C $(@D) ARCH=riscv oldconfig

###############################################################################
# Build
###############################################################################
profile:
	@echo "Give me a real profile script! Using a dummy instead."
	cp dummy_profile profile

DIRNAME ?= hello
initramfs.txt: build-initram.py
	./build-initram.py --dir=/nscratch/midas/initram/$(DIRNAME)

busybox/busybox: busybox/.config.old profile
	@echo "Building busybox."
	time make -C $(@D) -j

$(linux)/vmlinux: $(linux) initramfs.txt busybox/busybox
	@echo "Building riscv linux."
	make -C $(@D) ARCH=riscv defconfig
	make -C $(@D) -j ARCH=riscv vmlinux

vmlinux: $(linux)/vmlinux
	cp $< $@

clean:
	rm -rf $(linux) initramfs.txt vmlinux
	cd busybox && git clean -x -d -f

.PHONY: setup all clean
