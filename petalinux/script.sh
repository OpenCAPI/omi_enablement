petalinux-create --type project -s *.bsp
mkdir vcuomi/images && mkdir vcuomi/images/linux
cp -r linux/images/* vcuomi/images/linux/.
