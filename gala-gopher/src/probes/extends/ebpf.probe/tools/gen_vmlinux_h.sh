#/bin/sh

MAIN=`uname -r | awk -F . '{print $1}'`
MINOR=`uname -r | awk -F . '{print $2}'`
if [ "$MAIN" -ge 5 ] && [ "$MINOR" -ge 3 ]
    then
	echo "Gen vmlinux.h for kernel_"${MAIN}.${MINOR}
        ./bpftool btf dump file ${1:-/sys/kernel/btf/vmlinux} format c > ../src/include/vmlinux.h
fi
