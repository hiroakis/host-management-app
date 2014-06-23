import sys, os
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../'))

from srvadm import validator
import unittest

class TestValidator(unittest.TestCase):

    def setUp(self):
        self.rs = [{'role': 'web', 'ip': '192.168.1.101', 'hostname': 'web01'}, {'role': 'web', 'ip': '192.168.1.102', 'hostname': 'web02'}, {'role': 'web', 'ip': '192.168.1.102', 'hostname': 'web03'}]
        self.exp_hosts = "192.168.1.101\tweb01\n192.168.1.102\tweb02\n192.168.1.102\tweb03\n"
        self.exp_fablist = "192.168.1.101,192.168.1.102,192.168.1.102"
        self.exp_hankaku = "192.168.1.101 192.168.1.102 192.168.1.102"
        self.valid_ips = ["192.168.1.1", "1.1.1.1", "255.255.255.255"]
        self.exp_valid_ips = [True, True, True]
        self.invalid_ips = ["092.168.1.1", "192.168.1.1111" ,"192.168.1" ,"192.168.1.1.1" ,"192.168.1.a"]
        self.exp_invalid_ips = [False, False, False, False, False]

    def test_is_valid_ip(self):
        ret = []
        for ip in self.valid_ips:
            ret.append(validator.is_valid_ip(ip))
        self.assertEqual(ret, self.exp_valid_ips)

    def test_is_valid_ip_invalid(self):
        ret = []
        for ip in self.invalid_ips:
            ret.append(validator.is_valid_ip(ip))
        self.assertEqual(ret, self.exp_invalid_ips)


if __name__ == '__main__':
    unittest.main()
