#!/bin/bash
/usr/bin/sudo /usr/sbin/nft add element inet filter ipv6_white_list { $1 }
