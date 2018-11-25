#!/usr/bin/env python

# Generate the initramfs.txt file for building initramFS Linux.
#

import argparse
import subprocess
import os
import getpass


OUTNAME="initramfs.txt"

#---------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dirs', dest='dirs', type=str, nargs='+',
        help='input directory (to put into Linux)', required=True)
    args = parser.parse_args()

    with open(OUTNAME, 'w') as f:
        initialize_init_file(f)
        f.write("dir /celio 755 0 0\n")
        for dirname in args.dirs:
            append_init_file(f, "/celio/" + os.path.basename(dirname), dirname)

# Input: list of full path names to all of the files/directories we want to include.
def initialize_init_file(f):
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

    f.write("\n")
    f.write("file /etc/inittab ../inittab 755 0 0\n")
    f.write("file /etc/profile ../profile 755 0 0\n")
    f.write("\n")

def append_init_file(f, dest_dir, src_dir):
    paths = os.listdir(src_dir)
    f.write("dir %s 755 0 0\n" % dest_dir)
    for name in paths:
        dest_path = os.path.join(dest_dir, name)
        src_path = os.path.join(src_dir, name)
        if os.path.isdir(src_path):
            # print dest_path, "->", src_path
            append_init_file(f, dest_path, src_path)
        elif os.path.islink(src_path):
            #print "Link: %s" % (p)
            #print "Name: %s" % (name)
            #print " -> : %s" % (os.readlink(p))
            link = os.readlink(src_path)
            if os.path.isdir(link):
                append_init_file(f, dest_path, link)
            else:
                f.write("slink %s %s 755 0 0\n" % (dest_path, link))
        elif os.path.isfile(src_path):
            f.write("file %s %s 755 0 0\n" % (dest_path, src_path))
        else:
            assert False
 
#---------------------
if __name__ == '__main__':
    main()
 

