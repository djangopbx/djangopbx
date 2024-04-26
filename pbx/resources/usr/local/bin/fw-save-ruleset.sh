#!/bin/bash

now=$(date +%Y%m%d%H%M)

# Using the nft list ruleset for a restore can, under some versions, cause a segmentation fault.
# You must check that nftables starts ok after saving a ruleset this way for the first time.

/usr/bin/sudo /usr/bin/mv /etc/nftables.conf /etc/nftables.conf_${now}
/usr/bin/echo "#!/usr/sbin/nft -f" > /home/django-pbx/tmp/nftables.conf
/usr/bin/echo "" >> /home/django-pbx/tmp/nftables.conf
/usr/bin/echo "flush ruleset" >> /home/django-pbx/tmp/nftables.conf
/usr/bin/echo "" >> /home/django-pbx/tmp/nftables.conf
/usr/bin/sudo /usr/sbin/nft --stateless list ruleset >> /home/django-pbx/tmp/nftables.conf
/usr/bin/chmod +x /home/django-pbx/tmp/nftables.conf
/usr/bin/sudo /usr/bin/mv /home/django-pbx/tmp/nftables.conf /etc/nftables.conf
/usr/bin/sudo /usr/bin/chown root:root /etc/nftables.conf
