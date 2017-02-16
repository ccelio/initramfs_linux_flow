all: 
	@echo "Building everything (linux and pk)."
	@echo "Building initramfs.txt."
	./build-initram.py
	$(MAKE) linux
	$(MAKE) pk

# use make menuconfig to set stuff...
busybox:
	@echo "Building busybox."
	cd busybox && time make

linux-4.6.2:
	curl -L https://cdn.kernel.org/pub/linux/kernel/v4.x/linux-4.6.2.tar.xz | tar -xJ
	cd linux-4.6.2; git init;  git remote add -t master origin https://github.com/riscv/riscv-linux.git; git fetch; git checkout -f -t origin/master

linux: linux-4.6.2
	@echo "Building riscv linux."
	cd $< && time make -j4 ARCH=riscv vmlinux

pk:
	@echo "Building pk."
	time ./build-pk.sh

. PHONY: pk linux
