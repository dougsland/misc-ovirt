# The kickstart file will perform

authconfig --enableshadow --passalgo=md5
keyboard us
lang en_US
timezone --utc Asia/Shanghai

liveimg --url=http://192.168.122.1/ovirt-node-ng-image.squashfs.img

bootloader --location=mbr
rootpw --plaintext T0pSecret!
network --device=eth0 --bootproto=static --ip=192.168.122.2 --netmask=255.255.255.0 --gateway=192.168.122.1

clearpart --all

part /boot --fstype xfs --size=1100 --ondisk=sda
part pv.01 --size=42000 --grow
volgroup HostVG pv.01
logvol swap --vgname=HostVG --name=swap --fstype=swap --recommended
logvol none --vgname=HostVG --name=HostPool --thinpool --size=40000 --grow
logvol /    --vgname=HostVG --name=root --thin --fstype=ext4 --poolname=HostPool --fsoptions="defaults,discard" --size=6000 --grow
logvol /var --vgname=HostVG --name=var --thin --fstype=ext4 --poolname=HostPool --fsoptions="defaults,discard" --size=15000

%pre --log=/tmp/pre-install.log
echo "imgbase create on storage lvm"
%end

%post --nochroot --log=/mnt/sysimage/root/post-install.log
cp -v /tmp/pre-install.log /mnt/sysimage/root
%end

%post --erroronfail
imgbase layout --init
%end
reboot
