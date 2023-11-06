#!/bin/bash
/usr/bin/sudo /usr/sbin/nft delete element inet filter ipv6_web_block_list { $1 }
