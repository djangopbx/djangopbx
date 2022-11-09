#!/bin/bash
/usr/bin/sudo /usr/sbin/nft delete element inet filter ipv4_sip_gateway_list { $1 }
