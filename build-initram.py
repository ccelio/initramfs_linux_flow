#!/usr/bin/env python

# Generate the initramfs.txt file for building initramFS Linux.
#

import optparse
import subprocess
import os
import getpass


DIRNAME="/nscratch/midas/initram/hello"       # default source directory for copying over into linux initramfs.
OUTNAME="initramfs.txt"
RISCV="/nscratch/midas/riscv-tools/current-tools" # RISCV install location. TODO: get this through bash environment.
LIBPATH=os.path.join(RISCV, "sysroot", "lib64", "lp64d")

# This is a HACK! I'm struggling to fit the initramfs onto a very small FPGA memory,
# so include in the initramfs only the files we really need.
ENABLE_GCC=False
ENABLE_BASH=False
ENABLE_PYTHON=False

#---------------------
def main():
    global DIRNAME
    global ENABLE_GCC
    global ENABLE_BASH
    global ENABLE_PYTHON

    parser = optparse.OptionParser()
    parser.add_option('-d', '--dir', dest='dirname', help='input directory (to put into Linux)', default=DIRNAME)
    parser.add_option('-b', '--bmark', dest='bmark', help='input benchmark (helps decide stuff to include, since not everything can fit :( )', default="none")
    (options, args) = parser.parse_args()
    DIRNAME=options.dirname
    print "Using %s." % DIRNAME
    print "For   %s." % options.bmark

    enables = (False,False,False)
    if options.bmark == "all":
        enables = (True,True,True)
    elif options.bmark =="riscv-pk":
        enables = (True,True,False)
    elif options.bmark =="python":
        enables = (False,False,True)
    ENABLE_GCC,ENABLE_BASH,ENABLE_PYTHON = enables

    initialize_init_file()
    append_init_file("celio", DIRNAME)
    append_init_file("celio/rv_counters", os.path.join("/nscratch", "midas", "initram", "rv_counters"))
    # append_init_file("/lib", LIBPATH) # TODO: too big
    # needed for compiling
    if ENABLE_GCC or ENABLE_PYTHON: 
        append_init_file("usr/bin", os.path.abspath(os.curdir) + "/sysroot_usr_bin")
    if ENABLE_GCC:
        append_init_file("usr/include", os.path.abspath(os.curdir) + "/sysroot_usr_include")
        append_init_file("usr/lib/gcc", os.path.abspath(os.curdir) + "/sysroot_usr_lib/gcc")
        append_init_file("usr/lib/riscv64-poky-linux/6.1.1", os.path.abspath(os.curdir) + "/sysroot_usr_lib_riscv64-poky-linux_6.1.1")
        append_init_file("lib", os.path.abspath(os.curdir) + "/sysroot_lib")

    # adds ~40mb 
    if ENABLE_PYTHON:
        append_init_file("usr/lib/python2.7", os.path.abspath(os.curdir) + "/sysroot_usr_lib/python2.7")
        append_init_file("lib", RISCV + "/riscv64-unknown-linux-gnu/lib")


# Input: list of full path names to all of the files/directories we want to include.
def initialize_init_file():
    with open(OUTNAME, 'w') as f:
        f.write("slink /init /bin/busybox 755 0 0\n")
        f.write("dir /bin 755 0 0\n")
        f.write("file /bin/busybox ../busybox/busybox 755 0 0\n")
        f.write("dir /dev 755 0 0\n")
        f.write("nod /dev/console 644 0 0 c 5 1\n")
        f.write("nod /dev/null 644 0 0 c 1 3\n")
        f.write("dir /proc 755 0 0\n")
        f.write("dir /sbin 755 0 0\n")
        f.write("dir /usr 755 0 0\n")
        f.write("dir /usr/bin 755 0 0\n")
        f.write("dir /usr/sbin 755 0 0\n")
        f.write("dir /etc 755 0 0\n")
        f.write("dir /lib 755 0 0\n")
        f.write("\n")
        f.write("dir /usr/lib 755 0 0\n")
        f.write("dir /usr/libexec 755 0 0\n")
        f.write("dir /usr/libexec/gcc 755 0 0\n")

        if ENABLE_GCC:
            f.write("dir /usr/libexec/gcc/riscv64-poky-linux 755 0 0\n")
            f.write("dir /usr/libexec/gcc/riscv64-poky-linux/6.1.1 755 0 0\n")
            f.write("file /usr/libexec/gcc/riscv64-poky-linux/6.1.1/cc1 ../sysroot_usr_libexec/gcc/riscv64-poky-linux/6.1.1/cc1 755 0 0\n")
            f.write("file /usr/libexec/gcc/riscv64-poky-linux/6.1.1/cc1plus ../sysroot_usr_libexec/gcc/riscv64-poky-linux/6.1.1/cc1plus 755 0 0\n")
            f.write("file /usr/libexec/gcc/riscv64-poky-linux/6.1.1/collect2 ../sysroot_usr_libexec/gcc/riscv64-poky-linux/6.1.1/collect2 755 0 0\n")
            f.write("file /usr/libexec/gcc/riscv64-poky-linux/6.1.1/libcc1plugin.so.0.0.0 ../sysroot_usr_libexec/gcc/riscv64-poky-linux/6.1.1/libcc1plugin.so.0.0.0 755 0 0\n")
            f.write("file /usr/libexec/gcc/riscv64-poky-linux/6.1.1/libcc1.so.0.0.0 ../sysroot_usr_libexec/gcc/riscv64-poky-linux/6.1.1/libcc1.so.0.0.0 755 0 0\n")
            f.write("file /usr/libexec/gcc/riscv64-poky-linux/6.1.1/liblto_plugin.so.0.0.0 ../sysroot_usr_libexec/gcc/riscv64-poky-linux/6.1.1/liblto_plugin.so.0.0.0 755 0 0\n")
            f.write("file /usr/libexec/gcc/riscv64-poky-linux/6.1.1/lto1 ../sysroot_usr_libexec/gcc/riscv64-poky-linux/6.1.1/lto1 755 0 0\n")
            f.write("file /usr/libexec/gcc/riscv64-poky-linux/6.1.1/lto-wrapper ../sysroot_usr_libexec/gcc/riscv64-poky-linux/6.1.1/lto-wrapper 755 0 0\n")
            f.write("slink /usr/libexec/gcc/riscv64-poky-linux/6.1.1/libcc1plugin.so.0  libcc1plugin.so.0.0.0 755 0 0\n")
            f.write("slink /usr/libexec/gcc/riscv64-poky-linux/6.1.1/libcc1.so.0        libcc1.so.0.0.0 755 0 0\n")
            f.write("slink /usr/libexec/gcc/riscv64-poky-linux/6.1.1/liblto_plugin.so.0 liblto_plugin.so.0.0.0 755 0 0\n")
            f.write("slink /usr/libexec/gcc/riscv64-poky-linux/6.1.1/liblto_plugin.so   liblto_plugin.so.0.0.0 755 0 0\n")
            f.write("file /usr/lib/libopcodes-2.27.0.20160806.so ../sysroot_usr_lib/libopcodes-2.27.0.20160806.so 755 0 0\n")
            f.write("file /usr/lib/libbfd-2.27.0.20160806.so ../sysroot_usr_lib/libbfd-2.27.0.20160806.so 755 0 0\n")
            f.write("file /usr/lib/libmpc.so.3.0.0 ../sysroot_usr_lib/libmpc.so.3.0.0 755 0 0\n")
            f.write("slink /usr/lib/libmpc.so.3 libmpc.so.3.0.0 755 0 0\n")
            f.write("file /usr/lib/libmpfr.so.4.1.4 ../sysroot_usr_lib/libmpfr.so.4.1.4 755 0 0\n")
            f.write("slink /usr/lib/libmpfr.so.4 libmpfr.so.4.1.4 755 0 0\n")
            f.write("file /usr/lib/libgmp.so.10.3.1 ../sysroot_usr_lib/libgmp.so.10.3.1 755 0 0\n")
            f.write("slink /usr/lib/libgmp.so.10 libgmp.so.10.3.1 755 0 0\n")
            f.write("file /usr/lib/crt1.o ../sysroot_usr_lib/crt1.o 755 0 0\n")
            f.write("file /usr/lib/libc.so ../sysroot_usr_lib/libc.so 755 0 0\n")
            f.write("file /usr/lib/libc_nonshared.a ../sysroot_usr_lib/libc_nonshared.a 755 0 0\n")
            f.write("file /lib/libdl-2.24.so ../sysroot_lib/libdl-2.24.so 755 0 0\n")
            f.write("slink /lib/libdl.so.2 libdl-2.24.so 755 0 0\n")
            f.write("slink /usr/lib/libdl.so ../../lib/libdl.so.2 755 0 0\n")
            f.write("file /lib/libz.so.1.2.8 ../sysroot_lib/libz.so.1.2.8 755 0 0\n")
            f.write("slink /lib/libz.so.1 libz.so.1.2.8 755 0 0\n")

        if ENABLE_BASH:
            f.write("file /lib/libtinfo.so.5.9 ../sysroot_lib/libtinfo.so.5.9 755 0 0 \n")
            f.write("slink /lib/libtinfo.so.5 libtinfo.so.5.9 755 0 0 \n")
            f.write("slink /bin/bash /celio/bash 755 0 0\n")
 
        if ENABLE_PYTHON:
            f.write("file /usr/lib/libpython2.7.so.1.0 ../sysroot_usr_lib/libpython2.7.so.1.0 755 0 0\n")
 
        
        # f.write("file /lib/libgcc_s.so.1 ../sysroot_lib/libgcc_s.so.1 755 0 0 \n")
        # f.write("slink /lib/libgcc_s.so libgcc_s.so.1 755 0 0 \n")
        # f.write("file /lib/libc-2.24.so ../sysroot_lib/libc-2.24.so 755 0 0 \n")
        # f.write("slink /lib/libc.so.6 libc-2.24.so 755 0 0 \n")
  

        # f.write("dir /tmp 755 0 0\n")
        # f.write("dir /usr/lib/riscv64-poky-linux 755 0 0\n")
        # f .write("dir /usr/bin/riscv64-poky-linux 755 0 0\n")
        # f.write("slink /usr/bin/riscv64-poky-linux/ar ../../../usr/bin/riscv64-poky-linux-ar           755 0 0\n")
        # f.write("slink /usr/bin/riscv64-poky-linux/as ../../../usr/bin/riscv64-poky-linux-as           755 0 0\n")
        # f.write("slink /usr/bin/riscv64-poky-linux/ld ../../../usr/bin/riscv64-poky-linux-ld           755 0 0\n")
        # f.write("slink /usr/bin/riscv64-poky-linux/ld.bfd ../../../usr/bin/riscv64-poky-linux-ld.bfd   755 0 0\n")
        # f.write("slink /usr/bin/riscv64-poky-linux/nm ../../../usr/bin/riscv64-poky-linux-nm           755 0 0\n")
        # f.write("slink /usr/bin/riscv64-poky-linux/objcopy ../../../usr/bin/riscv64-poky-linux-objcopy 755 0 0\n")
        # f.write("slink /usr/bin/riscv64-poky-linux/objdump ../../../usr/bin/riscv64-poky-linux-objdump 755 0 0\n")
        # f.write("slink /usr/bin/riscv64-poky-linux/ranlib ../../../usr/bin/riscv64-poky-linux-ranlib   755 0 0\n")
        # f.write("slink /usr/bin/riscv64-poky-linux/readelf ../../../usr/bin/riscv64-poky-linux-readelf 755 0 0\n")
        # f.write("slink /usr/bin/riscv64-poky-linux/strip ../../../usr/bin/riscv64-poky-linux-strip     755 0 0\n")


        ##c++
        # f.write("slink /usr/lib/libstdc++.so libstdc++.so.6.0.22 755 0 0\n")
        # f.write("slink /usr/lib/libstdc++.so.6 libstdc++.so.6.0.22 755 0 0\n")
        # f.write("file /usr/lib/libstdc++.so.6.0.22 ../sysroot_usr_lib/libstdc++.so.6.0.22 755 0 0\n")


        f.write("\n")
        f.write("file /etc/inittab ../inittab 755 0 0\n")
        f.write("file /etc/profile ../profile 755 0 0\n")
        f.write("\n")

def append_init_file(dest_dir, src_dir):
         
    assert (src_dir[-1] != '/') # don't include "/" at the end of your source directory

    cmd = "find " + src_dir
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    paths = output.split('\n')[1:] # remove the first element, which is just src_dir.
    assert output.split('\n')[0] == src_dir

    with open(OUTNAME, 'a') as f:
        f.write("dir /" + dest_dir + " 755 0 0\n")
        for p in paths:
            if not p:
                continue
            if os.path.isdir(p):
                name = p.split(src_dir+ "/")[1]
                f.write("dir /" + dest_dir + "/" + name + " 755 0 0\n")
            elif os.path.islink(p):
                name = p.split(src_dir+ "/")[1]
                #print "Link: %s" % (p)
                #print "Name: %s" % (name)
                #print " -> : %s" % (os.readlink(p))
                link = os.readlink(p)
                f.write("slink /" + dest_dir + "/" + name + " " + link + " 755 0 0\n")
            else:
                #short = os.path.basename(p)
                name = p.split(src_dir+ "/")[1]
                f.write("file /" + dest_dir + "/" + name + " " + p + " 755 0 0\n")

 
 
#---------------------
if __name__ == '__main__':
    main()
 

