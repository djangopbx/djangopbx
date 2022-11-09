#!/bin/bash

now=$(date +%Y%m%d%H%M)

echo "Exit commang added for safety"
echo "Using the nft list ruleset for a restore can, under some versions, can cause a segmentation fault"
exit 0

/usr/bin/mv /etc/nftables.conf /etc/nftables.conf_${now}
echo "#!/usr/sbin/nft -f" > /etc/nftables.conf
echo "" >> /etc/nftables.conf
echo "flush ruleset" >> /etc/nftables.conf
echo "" >> /etc/nftables.conf

/usr/sbin/nft --stateless list ruleset >> /etc/nftables.conf

chmod +x /etc/nftables.conf
