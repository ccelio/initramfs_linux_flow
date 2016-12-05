all: 
	@echo "Building everything (linux and pk)."
	@echo "Building initramfs.txt."
	./build-initram.py
	$(MAKE) linux
	$(MAKE) pk

# use make menuconfig to set stuff...
busybox:
	@echo "Building busybox."
	cd busybox-1.21.1 && time make


linux:
	@echo "Building riscv linux."
	cd linux-4.6.2 && time make -j4 ARCH=riscv vmlinux

pk:
	@echo "Building pk."
	time ./build-pk.sh

.PHONY: pk linux
