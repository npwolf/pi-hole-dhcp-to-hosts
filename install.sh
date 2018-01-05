#!/bin/bash
set -e
# This will install dhcp_to_hosts.py to your system.
# Run the following to install directly:
# curl -sSL https://raw.githubusercontent.com/npwolf/pi-hole-dhcp-to-hosts/master/install.sh | sudo bash 
if [[ $EUID -ne 0 ]]; then
   echo "ERROR: Run this script with sudo or root."
   exit 1
fi

PROGRAM="dhcp_to_hosts.py"
DESTINATION="/usr/local/bin/${PROGRAM}"
# Send last run output to this log
LOG_FILE="/var/log/dhcp_to_hosts.log"
DHCP_HOSTS_FILE="/etc/dnsmasq.d/04-pihole-static-dhcp.conf"

# We'll setup to run this every 5 minutes via cron
CRONTAB="# Created by https://github.com/npwolf/pi-hole-dhcp-to-hosts
*/5 * * * * /usr/local/bin/dhcp_to_hosts.py --dhcp_hostsfile ${DHCP_HOSTS_FILE} > ${LOG_FILE} 2>&1"
CRONTAB_FILE="/etc/cron.d/dhcp_to_hosts"

if [ ! -f "${DHCP_HOSTS_FILE}" ]; then
	echo "ERROR: Could not find file with dhcp reservations: ${DHCP_HOSTS_FILE}"
	echo "You may need to create at least 1 DHCP reservation to create it."
	exit 1
fi

echo "Downloading script to ${DESTINATION}"
if curl -sSL --fail "https://raw.githubusercontent.com/npwolf/pi-hole-dhcp-to-hosts/master/${PROGRAM}" -o "${DESTINATION}"; then
    chmod a+x "${DESTINATION}"
else
    echo "ERROR: Failed to download ${PROGRAM}."
    exit 1
fi

echo "Creating crontab ${CRONTAB_FILE}..."
echo $CRONTAB > $CRONTAB_FILE
