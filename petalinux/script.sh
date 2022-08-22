petalinux-create --type project -s *.bsp
mkdir vcuomi/images && mkdir vcuomi/images/linux
cat linux/images/vmlinuxa* > linux/images/vmlinux
cp linux/images/rootfs.cpio.gz linux/images/rootfs.cpio2.gz
gunzip linux/images/rootfs.cpio2.gz
mv linux/images/rootfs.cpio2 linux/images/rootfs.cpio
cp -r linux/images/* vcuomi/images/linux/.

