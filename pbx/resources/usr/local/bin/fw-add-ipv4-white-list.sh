#!/bin/bash
/usr/bin/sudo /usr/sbin/nft add element inet filter ipv4_white_list { $1 }
