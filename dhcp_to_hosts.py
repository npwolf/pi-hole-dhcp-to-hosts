#!/usr/bin/env python
import logging
import re
import argparse
import os.path
import os
import sys
from functools import total_ordering

log = logging.getLogger(__name__)

@total_ordering
class DHCPRecord(object):
    """Store DHCP fields needed for execution."""
    def __init__(self, host, ip):
        self.host = host.lower()
        self.ip = ip

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    # total_ordering only provides this on the most recent python versions
    # https://bugs.python.org/issue25732
    def __ne__(self, other):
        return self.__dict__ != other.__dict__

    def __lt__(self, other):
        return self.__dict__ < other.__dict__

class Dhcp2Hosts(object):
    """Transoform DHCP hosts file into system hosts file."""

    # Example 00:01:FF:AB:09
    MAC_REGEX = r'(?:[0-9A-F]{2}[:-]){5}(?:[0-9A-F]{2})'
    # contains at least one character and a maximum of 63 characters
    # consists only of allowed characters
    # doesn't begin or end with a hyphen.
    HOST_REGEX = r'(?!-)[A-Z\d-]{1,63}(?<!-)'
    # Example 192.168.1.100
    IP_REGEX = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    # Example dhcp-host=10:2F:05:87:6D:7B,192.168.1.34,example.com
    DHCP_HOSTSFILE_REGEX = r'dhcp-host=' + MAC_REGEX + \
                           r',(?P<ip>' + IP_REGEX + r')' + \
                           r',(?P<host>' + HOST_REGEX + r')'

    # Header/Footer we enclose dhcp records in
    SECTION_HEADER = "\n### BEGIN: Auto-Generated by dhcp_hosts.py. DO NOT EDIT ###\n"
    SECTION_FOOTER = "###   END: Auto-Generated by dhcp_hosts.py. DO NOT EDIT ###\n"
    HOSTS_FILE = '/etc/hosts'

    def __init__(self, dhcp_hostsfile):
        self.dhcp_hostsfile = dhcp_hostsfile
        self.dhcp_records = []

    def needs_update(self):
        """Return bool to indicate if hosts file should be updated."""
        return os.path.getmtime(self.dhcp_hostsfile) != os.path.getmtime(self.HOSTS_FILE)

    def read_dhcp_records(self):
        """Read dnsmasq dhcp hostsfile and return list of DHCPRecords"""
        with open(self.dhcp_hostsfile, 'r') as hosts_fh:
            contents = hosts_fh.read()
        matches = re.findall(self.DHCP_HOSTSFILE_REGEX, contents, re.IGNORECASE|re.MULTILINE)
        log.debug("Found %s DHCP reservations.", len(matches))
        self.dhcp_records = []
        for match in matches:
            self.dhcp_records.append(DHCPRecord(host=match[1], ip=match[0]))

    def _get_generated_block(self):
        """Return a blob to append to hosts file based on dhcp record objects"""
        block = Dhcp2Hosts.SECTION_HEADER + \
                "\n".join(["{}\t{}".format(record.ip, record.host) for record in self.dhcp_records]) + \
                "\n" + Dhcp2Hosts.SECTION_FOOTER
        return block

    def update(self):
        """Update hosts file with dhcp records."""
        log.debug("Begin updating '%s' from data in '%s'", self.HOSTS_FILE, self.dhcp_hostsfile)
        # We copy access and modificationt time to
        # hosts file when update complete. This
        # allows needs_update to function
        dhcp_file_stat = os.stat(self.dhcp_hostsfile)

        self.read_dhcp_records()

        # Read in current hosts contents
        with open(self.HOSTS_FILE, 'r') as dhcp_hosts_fh:
            contents = dhcp_hosts_fh.read()

        # Remove any auto generated block that exists
        block_re = re.compile(re.escape(Dhcp2Hosts.SECTION_HEADER) + r'.*' + re.escape(Dhcp2Hosts.SECTION_FOOTER), re.MULTILINE|re.DOTALL)
        contents =  block_re.sub('', contents)

        # Now add auto generated records block
        contents += self._get_generated_block()

        # Write it all back
        with open(self.HOSTS_FILE, 'w') as hosts_fh:
            hosts_fh.write(contents)
        # Set modification time to match dchp file so needs_update works correctly
        os.utime(self.HOSTS_FILE, (dhcp_file_stat.st_atime, dhcp_file_stat.st_mtime))
        log.debug("Completed updating '%s' from data in '%s'", self.HOSTS_FILE, self.dhcp_hostsfile)

def get_args(args):
    """Parse command line"""
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Read in dnsmasq dhcp host file and write out hosts and IPs to /etc/hosts')
    parser.add_argument('--dhcp_hostsfile', required=True, help="DHCP Host file")
    return parser.parse_args(args)

def run(args):
    parsed_args = get_args(args)
    dhcp2hosts = Dhcp2Hosts(parsed_args.dhcp_hostsfile)
    if dhcp2hosts.needs_update():
       dhcp2hosts.update()
    else:
        log.info("No update needed.")

if __name__ == '__main__':
    run(sys.argv[1:])

