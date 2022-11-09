#!/bin/bash

if [ "$#" -lt 1 ]; then
    echo "You must supply a command line argument."
    exit 1
fi

if [[ ! ${1:-n} =~ ^[Yy]$ ]]; then
    echo "You must supply the command line argument Y or y."
    exit 1
fi

/usr/bin/sudo /usr/sbin/nft flush set inet filter ipv6_sip_customer_list
