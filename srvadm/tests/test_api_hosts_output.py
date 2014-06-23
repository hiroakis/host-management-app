import sys, os
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../'))

import unittest

from srvadm import app
from srvadm.tests.test_api import TestApiBase

class TestHostsOutput(TestApiBase):

    # hosts output
    def test_web_hosts(self):
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        res = self.app.get('/api/hosts_output/web')
        print(res.data.decode())
        assert 'Not found' not in res.data.decode()

    def test_app_hosts(self):
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        res = self.app.get('/api/hosts_output/app')
        print(res.data.decode())
        assert 'Not found' not in res.data.decode()

    def test_cache_hosts(self):
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        res = self.app.get('/api/hosts_output/cache')
        print(res.data.decode())
        assert 'Not found' not in res.data.decode()

    def test_db_hosts(self):
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        res = self.app.get('/api/hosts_output/db')
        print(res.data.decode())
        assert 'Not found' not in res.data.decode()

if __name__ == '__main__':
    unittest.main()

