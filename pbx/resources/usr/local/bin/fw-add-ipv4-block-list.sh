#!/bin/bash
/usr/bin/sudo /usr/sbin/nft add element netdev filter ipv4_block_list { $1 }
