#!/bin/bash
/usr/bin/sudo /usr/sbin/nft delete element inet filter ipv4_white_list { $1 }
