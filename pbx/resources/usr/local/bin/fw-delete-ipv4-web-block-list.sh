#!/bin/bash
/usr/bin/sudo /usr/sbin/nft delete element inet filter ipv4_web_block_list { $1 }
