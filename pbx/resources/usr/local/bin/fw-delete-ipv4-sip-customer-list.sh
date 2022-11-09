#!/bin/bash
/usr/bin/sudo /usr/sbin/nft delete element inet filter ipv4_sip_customer_list { $1 }
