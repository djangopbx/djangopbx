#!/bin/bash
/usr/bin/sudo /usr/sbin/nft delete element inet filter ipv6_sip_gateway_list { $1 }
