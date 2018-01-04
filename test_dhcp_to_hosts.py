#!/usr/bin/env python
import pytest
import os
import types
from mock import mock_open, patch, call

import dhcp_to_hosts
from dhcp_to_hosts import DHCPRecord, Dhcp2Hosts

class DHCPHostsTestData(object):
    """Test data to represent DHCP hosts file"""
    record1 = DHCPRecord(host='family-room', ip='172.30.50.22')
    record2 = DHCPRecord(host='appletv', ip='172.30.50.2')
    records = [record1, record2]
    contents = "dhcp-range=172.30.50.51,172.30.50.99,12h\n" + \
               "dhcp-host=00:0c:1e:02:b3:a3,{},{}\n".format(record1.ip, record1.host) + \
               "dhcp-host=10:40:f3:ec:90:1c,{},{}\n".format(record2.ip, record2.host) + \
               "dhcp-host=18:b4:30:00:48:b1,nest-thermostat"

class HostsTestData(object):
    """Test data to represent hosts file"""
    record1 = DHCPHostsTestData.record1
    record2 = DHCPHostsTestData.record2
    contents_before = "127.0.0.1    localhost\n" + \
                      "::1     localhost ip6-localhost ip6-loopback\n" + \
                      "ff02::1     ip6-allnodes\n" + \
                      "ff02::2     ip6-allrouters\n\n" + \
                      "127.0.1.1   pi-hole"
    new_block = "{}".format(Dhcp2Hosts.SECTION_HEADER) + \
                "{}\t{}\n".format(record1.ip, record1.host) + \
                "{}\t{}\n".format(record2.ip, record2.host) + \
                "{}".format(Dhcp2Hosts.SECTION_FOOTER)
    contents_after = contents_before + new_block

@pytest.fixture
def dhcp2hosts():
    return Dhcp2Hosts('simulated_file')

def test_dns_record_eq():
    record1 = DHCPRecord(host='host1', ip='192.168.1.1')
    record1_same = DHCPRecord(host='host1', ip='192.168.1.1')
    assert record1 == record1_same
    assert record1 == record1

def test_dns_record_ne():
    assert not (DHCPRecord(host='host1', ip='192.168.1.1') != DHCPRecord(host='host1', ip='192.168.1.1'))
    assert DHCPRecord(host='host1', ip='192.168.1.2') != DHCPRecord(host='host1', ip='192.168.1.1')
    assert DHCPRecord(host='host2', ip='192.168.1.1') != DHCPRecord(host='host1', ip='192.168.1.1')

def test_get_ip_host_from_dhcp_hostfile(dhcp2hosts):
    with patch('dhcp_to_hosts.open', mock_open(read_data=DHCPHostsTestData.contents)) as mock_open_cm:
        dhcp2hosts.read_dhcp_records()
    mock_open_cm.assert_called_with('simulated_file', 'r')
    assert len(dhcp2hosts.dhcp_records) == 2
    assert dhcp2hosts.dhcp_records[0] == DHCPHostsTestData.record1
    assert dhcp2hosts.dhcp_records[1] == DHCPHostsTestData.record2

def test_get_generated_block(dhcp2hosts):
    dhcp2hosts.dhcp_records = DHCPHostsTestData.records
    assert dhcp2hosts._get_generated_block() == HostsTestData.new_block

@patch('dhcp_to_hosts.os.utime')
@patch('dhcp_to_hosts.os.stat')
def test_update_hosts_opens_files(_mock_utime, _mock_stat, dhcp2hosts):
    with patch('dhcp_to_hosts.open', mock_open(read_data='')) as mock_open_cm:
        dhcp2hosts.update()
    mock_open_cm.assert_any_call(Dhcp2Hosts.HOSTS_FILE, 'r')
    mock_open_cm.assert_any_call(Dhcp2Hosts.HOSTS_FILE, 'w')

@patch('dhcp_to_hosts.os.utime')
@patch('dhcp_to_hosts.os.stat')
def test_update_hosts(_mock_utime, _mock_stat, dhcp2hosts):
    def fake_read_dhcp_records(self):
        self.dhcp_records = DHCPHostsTestData.records
    with patch.object(Dhcp2Hosts, 'read_dhcp_records', autospec=True, side_effect=fake_read_dhcp_records):
        with patch('dhcp_to_hosts.open', mock_open(read_data=HostsTestData.contents_before)) as mock_open_cm:
            mock_open_cm().read.return_value = HostsTestData.contents_before
            dhcp2hosts.update()
        mock_open_cm().write.assert_called_once_with(HostsTestData.contents_after)

@patch('dhcp_to_hosts.os.utime')
@patch('dhcp_to_hosts.os.stat')
def test_update_hosts_idempotent(_mock_utime, _mock_stat, dhcp2hosts):
    """Make sure already updated contents aren't changed."""
    def fake_read_dhcp_records(self):
        self.dhcp_records = DHCPHostsTestData.records
    with patch.object(Dhcp2Hosts, 'read_dhcp_records', autospec=True, side_effect=fake_read_dhcp_records):
        with patch('dhcp_to_hosts.open', mock_open(read_data=HostsTestData.contents_before)) as mock_open_cm:
            mock_open_cm().read.return_value = HostsTestData.contents_after
            dhcp2hosts.update()
        mock_open_cm().write.assert_called_once_with(HostsTestData.contents_after)

@patch('dhcp_to_hosts.os.utime')
def test_update_modifies_hosts_modification_time(mock_utime, dhcp2hosts):
    stat_result = os.stat(os.path.realpath(__file__))
    with patch('dhcp_to_hosts.open', mock_open(read_data='no_data')) as mock_open_cm:
        with patch('dhcp_to_hosts.os.stat', return_value=stat_result):
            dhcp2hosts.update()
            mock_utime.assert_called_once_with(dhcp2hosts.HOSTS_FILE, (stat_result.st_atime, stat_result.st_mtime))
    

def test_needs_update_false(dhcp2hosts):
    with patch('dhcp_to_hosts.os.path.getmtime', return_value=1330712292):
        assert dhcp2hosts.needs_update() == False

def test_needs_update_true(dhcp2hosts):
    with patch('dhcp_to_hosts.os.path.getmtime', side_effect=[1330712292, 1230712293]):
        assert dhcp2hosts.needs_update() == True

def test_get_args_no_args():
    with pytest.raises(SystemExit):
        dhcp_to_hosts.get_args([])

def test_get_args_help():
    with pytest.raises(SystemExit):
        dhcp_to_hosts.get_args(['--help'])

@patch.object(Dhcp2Hosts, 'needs_update', autospec=True, return_value=True)
@patch.object(Dhcp2Hosts, 'update', autospec=True)
def test_run_needs_update(mock_needs_update, mock_update):
    fake_file = 'fake_file' 
    def verify_fake_file_passed_in(self):
        assert self.dhcp_hostsfile == fake_file
    mock_update.side_effect = verify_fake_file_passed_in
    dhcp_to_hosts.run(['--dhcp_hostsfile', fake_file])
    assert mock_update.called

@patch.object(Dhcp2Hosts, 'needs_update', autospec=True, return_value=False)
def test_run_no_update_needed(mock_needs_update):
    dhcp_to_hosts.run(['--dhcp_hostsfile', 'fake_file'])
    assert mock_needs_update.called

if __name__ == '__main__':
    pytest.main()
