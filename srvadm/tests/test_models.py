import sys, os
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../'))

import unittest
from datetime import datetime

from srvadm.models import Role, IP, Host, RoleMap
from srvadm import app, db

TEST_DB = 'srv_test'
TEST_DSN = 'mysql+pymysql://root:@localhost/?charset=utf8'
DROP_TEST_DB = 'drop database if exists %s' % TEST_DB
CREATE_TEST_DB = 'create database %s' % TEST_DB
USE_TEST_DB = 'use %s' % TEST_DB

class TestModelsBase(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DSN
        db.engine.execute(DROP_TEST_DB)
        db.engine.execute(CREATE_TEST_DB)
        db.engine.execute(USE_TEST_DB)
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.engine.execute(DROP_TEST_DB)

    def create_test_role_data(self):
        role_list = ['web', 'app', 'db', 'session', 'cache', 'vip']
        for role_name in role_list:
            role = Role(role_name=role_name)
            db.session.add(role)
        db.session.commit()

    def create_test_ip_data(self):
        ip_list = [('192.168.1.101', 1),('192.168.1.102', 1),('192.168.1.103', 1),\
                ('192.168.1.111', 1),('192.168.1.112', 1),('192.168.1.113', 1),\
                ('192.168.1.121', 1),('192.168.1.122', 0),('192.168.1.100', 1)]
        for i in ip_list:
            ip = IP(ip=i[0], is_used=i[1])
            db.session.add(ip)
        db.session.commit()

    def create_test_role_map_data(self):
        role_map_list = [('web01', 'web'),('web01', 'app'),('web02', 'web'),\
                ('web02', 'app'),('web03', 'web'),('web03', 'app'),\
                ('db01', 'db'),('db02', 'db'),('db03', 'db'),\
                ('mem01', 'session'),('mem01', 'cache'),('vip01', 'vip')]
        for r in role_map_list:
            role_map = RoleMap(host_name=r[0], role_name=r[1])
            db.session.add(role_map)
        db.session.commit()

    def create_test_host_data(self):
        host_list = [('web01', '192.168.1.101', datetime.now(), datetime.now()),\
                ('web02', '192.168.1.102', datetime.now(), datetime.now()),\
                ('web03', '192.168.1.103', datetime.now(), datetime.now()),\
                ('db01', '192.168.1.111', datetime.now(), datetime.now()),\
                ('db02', '192.168.1.112', datetime.now(), datetime.now()),\
                ('db03', '192.168.1.113', datetime.now(), datetime.now()),\
                ('mem01', '192.168.1.121', datetime.now(), datetime.now()),\
                ('vip01', '192.168.1.100', datetime.now(), datetime.now())]
        for h in host_list:
            host = Host(host_name=h[0], ip=h[1], created_at=h[2], updated_at=h[3])
            db.session.add(host)
        db.session.commit()

class TestRole(TestModelsBase):

    def test_get_all(self):
        expected = ['web', 'app', 'db', 'session', 'cache', 'vip']
        self.create_test_role_data()
        roles = Role.get_all(db.session.query)
        actual = [r.role_name for r in roles]
        self.assertListEqual(sorted(expected), sorted(actual))

    def test_get_one(self):
        expected = 'web'
        self.create_test_role_data()
        role = Role.get_one(db.session.query, 'web')
        actual = role.role_name
        self.assertEqual(expected, actual)

    def test_get_one_miss(self):
        expected = None
        self.create_test_role_data()
        role = Role.get_one(db.session.query, 'we')
        actual = role
        self.assertEqual(expected, actual)

    def test_get_in_role_names(self):
        expected = ['db', 'cache', 'vip']
        self.create_test_role_data()
        roles = Role.get_in_role_names(db.session.query, ['db', 'cache', 'vip'])
        actual = [r.role_name for r in roles]
        self.assertListEqual(sorted(expected), sorted(actual))

    def test_get_in_role_names_miss(self):
        expected = []
        self.create_test_role_data()
        roles = Role.get_in_role_names(db.session.query, ['xx', 'yy', 'zz'])
        actual = [r.role_name for r in roles]
        self.assertListEqual(sorted(expected), sorted(actual))

    def test_get_in_role_names_harf(self):
        expected = ['web', 'db']
        self.create_test_role_data()
        roles = Role.get_in_role_names(db.session.query, ['xx', 'db', 'web', 'zz'])
        actual = [r.role_name for r in roles]
        self.assertListEqual(sorted(expected), sorted(actual))

class TestIP(TestModelsBase):

    def test_get_all(self):
        expected = ['192.168.1.101','192.168.1.102','192.168.1.103',\
                '192.168.1.111','192.168.1.112','192.168.1.113',\
                '192.168.1.121','192.168.1.122','192.168.1.100']
        self.create_test_ip_data()
        ips = IP.get_all(db.session.query)
        actual = [r.ip for r in ips]
        self.assertListEqual(sorted(expected), sorted(actual))

    def test_get_used(self):
        expected = ['192.168.1.101','192.168.1.102','192.168.1.103',\
                '192.168.1.111','192.168.1.112','192.168.1.113',\
                '192.168.1.121','192.168.1.100']
        self.create_test_ip_data()
        ips = IP.get_used(db.session.query)
        actual = [r.ip for r in ips]
        self.assertListEqual(sorted(expected), sorted(actual))

    def test_get_unused(self):
        expected = ['192.168.1.122']
        self.create_test_ip_data()
        ips = IP.get_unused(db.session.query)
        actual = [r.ip for r in ips]
        self.assertListEqual(sorted(expected), sorted(actual))

    def test_get_one(self):
        expected = '192.168.1.102'
        self.create_test_ip_data()
        ip = IP.get_one(db.session.query, '192.168.1.102')
        actual = ip.ip
        self.assertEqual(expected, actual)

    def test_get_one_miss(self):
        expected = None
        self.create_test_ip_data()
        ip = IP.get_one(db.session.query, '192.168.1.10')
        actual = ip
        self.assertEqual(expected, actual)


class TestRoleMap(TestModelsBase):

    def test_get_by_role_name(self):
        expected = [('web01', 'app'), ('web02', 'app'), ('web03', 'app')]
        self.create_test_role_data()
        self.create_test_ip_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        role_maps = RoleMap.get_by_role_name(db.session.query, 'app')
        actual = [(r.host_name, r.role_name) for r in role_maps]
        self.assertListEqual(sorted(expected), sorted(actual))

    def test_get_one_by_role_name(self):
        expected = ('web01', 'app')
        self.create_test_role_data()
        self.create_test_ip_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        role_map = RoleMap.get_one_by_role_name(db.session.query, 'app')
        actual = (role_map.host_name, role_map.role_name)
        self.assertEqual(expected, actual)

    def test_get_by_host_name(self):
        expected = [('web01', 'app'), ('web01', 'web')]
        self.create_test_role_data()
        self.create_test_ip_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        role_maps = RoleMap.get_by_host_name(db.session.query, 'web01')
        actual = [(r.host_name, r.role_name) for r in role_maps]
        self.assertListEqual(sorted(expected), sorted(actual))

class TestHost(TestModelsBase):

    def test_get_all(self):
        expected = [('web01', '192.168.1.101'),\
                ('web02', '192.168.1.102'),\
                ('web03', '192.168.1.103'),\
                ('db01', '192.168.1.111'),\
                ('db02', '192.168.1.112'),\
                ('db03', '192.168.1.113'),\
                ('mem01', '192.168.1.121'),\
                ('vip01', '192.168.1.100')]
        self.create_test_role_data()
        self.create_test_ip_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        hosts = Host.get_all(db.session.query)
        actual = [(h.host_name, h.ip) for h in hosts]
        self.assertListEqual(sorted(expected), sorted(actual))

    def test_get_one_by_ip(self):
        expected = ('web01', '192.168.1.101')
        self.create_test_role_data()
        self.create_test_ip_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        host = Host.get_one_by_ip(db.session.query, '192.168.1.101')
        actual = (host.host_name, host.ip)
        self.assertEqual(expected, actual)

    def test_get_one_by_host_name(self):
        expected = ('web01', '192.168.1.101')
        self.create_test_role_data()
        self.create_test_ip_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        host = Host.get_one_by_host_name(db.session.query, 'web01')
        actual = (host.host_name, host.ip)
        self.assertEqual(expected, actual)

    def test_get_all(self):
        expected = [('web01', '192.168.1.101'),\
                ('web02', '192.168.1.102'),\
                ('mem01', '192.168.1.121'),\
                ('vip01', '192.168.1.100')]
        self.create_test_role_data()
        self.create_test_ip_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        hosts = Host.get_in_host_names(db.session.query, ['web01', 'web02', 'mem01', 'vip01'])
        actual = [(h.host_name, h.ip) for h in hosts]
        self.assertListEqual(sorted(expected), sorted(actual))

if __name__ == '__main__':
    unittest.main()

