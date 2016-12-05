#CC= CXX= build_project riscv-pk --prefix=$RISCV --host=riscv64-unknown-elf --with-payload=/scratch/celio/linux-4.6.2/vmlinux

VMLINUX=$PWD/linux-4.6.2/vmlinux
JOBS=16
# Use gmake instead of make if it exists.   
MAKE=`command -v gmake || command -v make`  


mkdir -p riscv-pk/build                      
cd riscv-pk/build                            
echo "Configuring riscv-pk"          
../configure --prefix=$RISCV --host=riscv64-unknown-elf --with-payload=$VMLINUX > build.log
echo "Building riscv-pk"             
$MAKE -j$JOBS >> build.log
cd -
cp riscv-pk/build/bbl bblvmlinux
