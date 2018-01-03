# pi-hole-dhcp-to-hosts
[![Build Status](https://travis-ci.org/npwolf/pi-hole-dhcp-to-hosts.svg?branch=master)](https://travis-ci.org/npwolf/pi-hole-dhcp-to-hosts)

Keep DNS updated with DHCP reservations in dnsmasq even if they're not active. 

# Why?

My preference is to have even inactive DHCP reservations return in DNS queries. Normally you would have to edit /etc/hosts yourself. This script does it for you.

pi-hole is probably never going to support this because dnsmasq could have more than one dhcp host entry with addresses on different subnets. Most home users probably never need to worry about that though. [See](http://lists.thekelleys.org.uk/pipermail/dnsmasq-discuss/2015q2/009396.html)

# Installation on pi-hole

TODO

# Testing

Install tox if you don't have it yet:
```pip install tox```

Then run the tests via tox:

```tox```
