#!/bin/bash
/usr/bin/sudo /usr/sbin/nft add element inet filter ipv4_web_block_list { $1 }
