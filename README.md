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

# Example 

## Before Run
```
pi@pihole:~ $ cat /etc/hosts
127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters

127.0.1.1       pihole
```

## After Run
```
pi@pi-hole:~ $ cat /etc/dnsmasq.d/04-pihole-static-dhcp.conf
dhcp-host=80:51:62:2F:D9:EB,192.168.1.5,esxi
dhcp-host=1A:B8:93:BE:B5:C9,192.168.1.20,office-desktop
dhcp-host=4C:77:10:56:1E:8B,192.168.1.21,livingroom-firestick
dhcp-host=80:51:62:2F:D9:EB,192.168.1.22,work-laptop
```

```
pi@pihole:~ $ cat /etc/hosts
127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters

127.0.1.1       pihole

### BEGIN: Auto-Generated by dhcp_hosts.py. DO NOT EDIT ###
192.168.1.5     esxi
192.168.1.20    office-desktop
192.168.1.21    livingroom-firestick
192.168.1.22    work-laptop
###   END: Auto-Generated by dhcp_hosts.py. DO NOT EDIT ###
```

# Testing

Install tox if you don't have it yet:
```pip install tox```

Then run the tests via tox:

```tox```
