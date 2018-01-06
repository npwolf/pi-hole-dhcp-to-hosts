# pi-hole-dhcp-to-hosts
[![Build Status](https://travis-ci.org/npwolf/pi-hole-dhcp-to-hosts.svg?branch=master)](https://travis-ci.org/npwolf/pi-hole-dhcp-to-hosts)

Keep DNS updated with DHCP reservations in dnsmasq even if they're not active. I built this after I installed [pi-hole](https://pi-hole.net/) on a Raspberry Pi.

My preference is to have even inactive DHCP reservations return in DNS queries. I set my servers up with static IPs, but I like to keep track of them by creating DHCP reservations for them. Normally you would have to edit /etc/hosts yourself. This script does it for you.

pi-hole is probably never going to support this because dnsmasq could have more than one dhcp host entry with addresses on different subnets. Most home users probably never need to worry about that though. [See](http://lists.thekelleys.org.uk/pipermail/dnsmasq-discuss/2015q2/009396.html)

# Installation on pi-hole

Install from the web:
`curl -sSL https://raw.githubusercontent.com/npwolf/pi-hole-dhcp-to-hosts/master/install.sh | sudo bash`

or

Clone this repo and run 
`sudo install.sh`

It will place dhcp_to_hosts.py in /usr/local/bin and a crontab in /etc/cron.d/dhcp_to_hosts set to run every 5 minutes.

# Testing

Install tox if you don't have it yet:
```pip install tox```

Then run the tests via tox:

```tox```
