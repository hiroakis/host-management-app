import sys, os
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../'))

import unittest
import json
from datetime import datetime

from srvadm.models import Role, IP, Host, RoleMap
from srvadm import app, db

TEST_DB = 'srv_test'
TEST_DSN = 'mysql+pymysql://root:@localhost/?charset=utf8'
DROP_TEST_DB = 'drop database if exists %s' % TEST_DB
CREATE_TEST_DB = 'create database %s' % TEST_DB
USE_TEST_DB = 'use %s' % TEST_DB

class TestApiBase(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DSN
        db.engine.execute(DROP_TEST_DB)
        db.engine.execute(CREATE_TEST_DB)
        db.engine.execute(USE_TEST_DB)
        db.create_all()
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        db.engine.execute(DROP_TEST_DB)
    
    def create_test_role_data(self):
        role_list = ['web', 'app', 'db', 'session', 'cache', 'vip']
        for role_name in role_list:
            role = Role(role_name=role_name)
            db.session.add(role)
        db.session.commit()

    def create_test_ip_data(self):
        ip_list = [('192.168.1.100', 1), ('192.168.1.101', 1), ('192.168.1.102', 1),\
                ('192.168.1.103', 1), ('192.168.1.111', 1), ('192.168.1.112', 1), ('192.168.1.113', 1),\
                ('192.168.1.121', 1), ('192.168.1.122', 0)]
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

class TestApi(TestApiBase):

    # IP
    def test_list_ip(self):
        expected = dict(result=['192.168.1.100', '192.168.1.101', '192.168.1.102',\
                '192.168.1.103', '192.168.1.111', '192.168.1.112', '192.168.1.113',\
                '192.168.1.121', '192.168.1.122'])
        self.create_test_ip_data()
        uri = '/api/list/ip'

        res = self.app.get(uri)
        j = json.JSONDecoder()
        actual = j.decode(res.data.decode())
        self.assertDictEqual(expected, actual)

    def test_list_ip_unused(self):
        expected = dict(result=['192.168.1.122'])
        self.create_test_ip_data()
        uri = '/api/list/ip/unused'

        res = self.app.get(uri)
        j = json.JSONDecoder()
        actual = j.decode(res.data.decode())
        self.assertDictEqual(expected, actual)
        #assert b'192.168.1.100' in rv.data

    def test_list_ip_used(self):
        expected = dict(result=['192.168.1.100', '192.168.1.101', '192.168.1.102',\
                '192.168.1.103', '192.168.1.111', '192.168.1.112', '192.168.1.113',\
                '192.168.1.121'])
        self.create_test_ip_data()
        uri = '/api/list/ip/used'

        res = self.app.get(uri)
        j = json.JSONDecoder()
        actual = j.decode(res.data.decode())
        self.assertDictEqual(expected, actual)

    def test_list_ip_by_role(self):
        expected = dict(result=['192.168.1.101', '192.168.1.102', '192.168.1.103'])
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/list/ip/role/%s' % ('app')

        res = self.app.get(uri)
        j = json.JSONDecoder()
        actual = j.decode(res.data.decode())
        self.assertDictEqual(expected, actual)

    def test_list_ip_by_role_csv(self):
        expected = '192.168.1.101,192.168.1.102,192.168.1.103'
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/list/ip/role/app?format=csv'
        uri = '/api/list/ip/role/%s?format=%s' % ('', 'csv')

        res = self.app.get('/api/list/ip/role/app?format=csv')
        actual = res.data.decode()
        self.assertEqual(expected, actual)

    def test_search_by_ip_web(self):
        expected = dict(result=[dict(host_name="web01",\
                ip="192.168.1.101",\
                role=['web', 'app'])])
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/ip/%s' % ('192.168.1.101')

        res = self.app.get('/api/ip/192.168.1.101')
        j = json.JSONDecoder()
        actual = j.decode(res.data.decode())
        self.assertDictEqual(expected, actual)

    def test_search_by_ip_db(self):
        expected = dict(result=[dict(host_name="db01",\
                ip="192.168.1.111",\
                role=['db'])])
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/ip/%s' % ('192.168.1.111')

        res = self.app.get(uri)
        j = json.JSONDecoder()
        actual = j.decode(res.data.decode())
        self.assertDictEqual(expected, actual)

    def test_add_ip(self):
        headers = [('Content-Type', 'application/json')]
        data = dict(ip="192.168.1.114")
        uri = '/api/ip'

        json_data = json.dumps(data)
        res = self.app.post(uri, headers=headers, data=json_data)
        assert '200' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'OK' in res.data.decode()

    def test_add_exist_ip(self):
        self.create_test_ip_data()
        headers = [('Content-Type', 'application/json')]
        data = dict(ip="192.168.1.101")
        uri = '/api/ip'

        json_data = json.dumps(data)
        res = self.app.post(uri, headers=headers, data=json_data)
        res = self.app.post(uri, headers=headers, data=json_data)
        assert '500' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'Could not complete your request. may be duprecated.' in res.data.decode()

    def test_add_bad_format_ip(self):
        headers = [('Content-Type', 'application/json')]
        data = dict(ip="192.168.1.11aa4")
        uri = '/api/ip'

        json_data = json.dumps(data)
        res = self.app.post(uri, headers=headers, data=json_data)
        assert '400' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'Check the format you requested' in res.data.decode()

    def test_delete_ip(self):
        self.create_test_ip_data()
        uri = '/api/ip/%s' % ('192.168.1.122')

        res = self.app.delete(uri)
        assert '200' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'OK' in res.data.decode()

    def test_delete_used_ip(self):
        self.create_test_ip_data()
        uri = '/api/ip/%s' % ('192.168.1.101')

        res = self.app.delete(uri)
        assert '500' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'Could not complete your request. may be duprecated.' in res.data.decode()

    # Role
    def test_list_role(self):
        expected = dict(result=sorted(['web', 'app', 'db', 'session', 'cache', 'vip']))
        self.create_test_role_data()
        uri = '/api/list/role'

        res = self.app.get(uri)
        j = json.JSONDecoder()
        actual = j.decode(res.data.decode())
        self.assertDictEqual(expected, actual)


    def test_search_by_role_web(self):
        l = []
        l.append(dict(host_name="web01", ip="192.168.1.101", role=['web', 'app']))
        l.append(dict(host_name="web02", ip="192.168.1.102", role=['web', 'app']))
        l.append(dict(host_name="web03", ip="192.168.1.103", role=['web', 'app']))
        expected = dict(result=l)
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/role/%s' % ('app')

        res = self.app.get(uri)
        j = json.JSONDecoder()
        actual = j.decode(res.data.decode())
        self.assertDictEqual(expected, actual)

    def test_search_by_role_db(self):
        l = []
        l.append(dict(host_name="db01", ip="192.168.1.111", role=['db']))
        l.append(dict(host_name="db02", ip="192.168.1.112", role=['db']))
        l.append(dict(host_name="db03", ip="192.168.1.113", role=['db']))
        expected = dict(result=l)
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/role/%s' % ('db')

        res = self.app.get(uri)
        j = json.JSONDecoder()
        actual = j.decode(res.data.decode())
        self.assertDictEqual(expected, actual)

    def test_add_role(self):
        headers = [('Content-Type', 'application/json')]
        data = dict(role="hoge")
        uri = '/api/role'

        json_data = json.dumps(data)
        res = self.app.post(uri, headers=headers, data=json_data)
        assert '200' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'OK' in res.data.decode()

    def test_add_exist_role(self):
        headers = [('Content-Type', 'application/json')]
        data = dict(role="web")
        json_data = json.dumps(data)
        self.create_test_role_data()
        uri = '/api/role'

        res = self.app.post(uri, headers=headers, data=json_data)
        assert '500' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'Could not complete your request. may be duprecated.' in res.data.decode()

    def test_delete_role(self):
        self.create_test_role_data()
        uri = '/api/role/%s' % ('web')

        res = self.app.delete(uri)
        assert '200' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'OK' in res.data.decode()

    def test_delete_used_role(self):
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/role/%s' % ('web')

        res = self.app.delete(uri)
        assert '500' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'Could not complete your request. may be duprecated.' in res.data.decode()

    # Host
    def test_list_host(self):
        expected = dict(result=sorted(['web01', 'web02', 'web03',\
                'db01', 'db02', 'db03', 'mem01', 'vip01']))
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/list/host'

        res = self.app.get(uri)
        j = json.JSONDecoder()
        actual = j.decode(res.data.decode())
        self.assertDictEqual(expected, actual)

    def test_search_by_host_web(self):
        expected = dict(result=[dict(host_name="web01",\
            ip="192.168.1.101",\
            role=['app', 'web'])])
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/host/%s' % ('web01')

        res = self.app.get(uri)
        j = json.JSONDecoder()
        actual = j.decode(res.data.decode())
        self.assertDictEqual(expected, actual)

    def test_search_by_host_db(self):
        expected = dict(result=[dict(host_name="db01",\
                ip="192.168.1.111",\
                role=['db'])])
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/host/%s' % ('db01')

        res = self.app.get(uri)
        j = json.JSONDecoder()
        actual = j.decode(res.data.decode())
        self.assertDictEqual(expected, actual)

    def test_add_host(self):
        headers = [('Content-Type', 'application/json')]
        data = dict(host_name="mem02",\
                ip="192.168.1.122",\
                role=["cache", "session"])
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/host'

        json_data = json.dumps(data)
        res = self.app.post(uri, headers=headers, data=json_data)
        assert 'OK' in res.data.decode()
        assert 'add host' in res.data.decode()

    def test_add_used_hostname(self):
        headers = [('Content-Type', 'application/json')]
        data = dict(host_name="web01",\
                ip="192.168.1.122",\
                role=["cache", "session"])
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/host'

        json_data = json.dumps(data)
        res = self.app.post(uri, headers=headers, data=json_data)
        assert '500' in str(res.status_code)
        assert 'Could not complete your request. may be duprecated.' in res.data.decode()

    def test_add_host_by_used_ip(self):
        headers = [('Content-Type', 'application/json')]
        data = dict(host_name="mem02",\
                ip="192.168.1.101",\
                role=["cache", "session"])
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/host'

        json_data = json.dumps(data)
        res = self.app.post(uri, headers=headers, data=json_data)
        assert '500' in str(res.status_code)
        assert 'Could not complete your request. may be duprecated.' in res.data.decode()

    def test_add_host_by_undefied_ip(self):
        headers = [('Content-Type', 'application/json')]
        data = dict(host_name="mem02",\
                ip="192.168.1.190",\
                role=["cache", "session"])
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/host'

        json_data = json.dumps(data)
        res = self.app.post(uri, headers=headers, data=json_data)
        assert '500' in str(res.status_code)
        assert 'Could not complete your request. may be duprecated.' in res.data.decode()

    def test_add_host_by_undefied_role(self):
        headers = [('Content-Type', 'application/json')]
        data = dict(host_name="mem02",\
                ip="192.168.1.122",\
                role=["aaaa"])
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/host'

        json_data = json.dumps(data)
        res = self.app.post(uri, headers=headers, data=json_data)
        assert '500' in str(res.status_code)
        assert 'Could not complete your request. may be duprecated.' in res.data.decode()

    # Host
    def test_list_host(self):
        expected = dict(result=sorted(['web01', 'web02', 'web03',\
                'db01', 'db02', 'db03', 'mem01', 'vip01']))
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/list/host'

        res = self.app.get(uri)
        j = json.JSONDecoder()
        actual = j.decode(res.data.decode())
        self.assertDictEqual(expected, actual)

    def test_search_by_host_web(self):
        expected = dict(result=[dict(host_name="web01",\
                ip="192.168.1.101",\
                role=['web', 'app'])])
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/host/%s' % ('web01')

        res = self.app.get(uri)
        j = json.JSONDecoder()
        actual = j.decode(res.data.decode())
        self.assertDictEqual(expected, actual)

    def test_search_by_host_db(self):
        expected = dict(result=[dict(host_name="db01",\
                ip="192.168.1.111",\
                role=['db'])])
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/host/%s' % ('db01')

        res = self.app.get(uri)
        j = json.JSONDecoder()
        actual = j.decode(res.data.decode())
        self.assertDictEqual(expected, actual)

    def test_add_host(self):
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        headers = [('Content-Type', 'application/json')]
        data = dict(host_name="mem02",
                ip="192.168.1.122",
                role=["cache", "session"])
        uri = '/api/host'

        json_data = json.dumps(data)
        res = self.app.post(uri, headers=headers, data=json_data)
        assert '200' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'OK' in res.data.decode()

    def test_add_used_hostname(self):
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        headers = [('Content-Type', 'application/json')]
        data = dict(host_name="web01",
                ip="192.168.1.122",
                role=["cache", "session"])
        uri = '/api/host'

        json_data = json.dumps(data)
        res = self.app.post(uri, headers=headers, data=json_data)
        assert '500' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'Could not complete your request. may be duprecated.' in res.data.decode()

    def test_add_host_by_used_ip(self):
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        headers = [('Content-Type', 'application/json')]
        data = dict(host_name="mem02",
                ip="192.168.1.101",
                role=["cache", "session"])
        uri = '/api/host'

        json_data = json.dumps(data)
        res = self.app.post(uri, headers=headers, data=json_data)
        assert '500' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'Could not complete your request. may be duprecated.' in res.data.decode()

    def test_add_host_by_undefied_ip(self):
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        headers = [('Content-Type', 'application/json')]
        data = dict(host_name="mem02",
                ip="192.168.1.190",
                role=["cache", "session"])
        uri = '/api/host'

        json_data = json.dumps(data)
        res = self.app.post(uri, headers=headers, data=json_data)
        assert '500' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'Could not complete your request. may be duprecated.' in res.data.decode()

    def test_add_host_by_undefied_role(self):
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        headers = [('Content-Type', 'application/json')]
        data = dict(host_name="mem02",
                ip="192.168.1.122",
                role=["aaaa"])
        uri = '/api/host'

        json_data = json.dumps(data)
        res = self.app.post(uri, headers=headers, data=json_data)
        assert '500' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'Could not complete your request. may be duprecated.' in res.data.decode()

    def test_delete_host(self):
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        uri = '/api/host/%s' % ('db01')

        res = self.app.delete(uri)
        assert '200' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'OK' in res.data.decode()

    def test_update_ip(self):
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        headers = [('Content-Type', 'application/json')]
        data = dict(ip="192.168.1.114")
        uri = '/api/ip/%s' % ('192.168.1.101')

        json_data = json.dumps(data)
        res = self.app.put(uri, headers=headers, data=json_data)
        assert '200' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'OK' in res.data.decode()

    def test_update_ip_duplicate(self):
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        headers = [('Content-Type', 'application/json')]
        data = dict(ip="192.168.1.102")
        uri = '/api/ip/%s' % ('192.168.1.101')

        json_data = json.dumps(data)
        res = self.app.put(uri, headers=headers, data=json_data)
        assert '500' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'Could not complete your request. may be duprecated.' in res.data.decode()

    def test_update_role(self):
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        headers = [('Content-Type', 'application/json')]
        data = dict(role="webweb")
        uri = '/api/role/%s' % ('web')

        json_data = json.dumps(data)
        res = self.app.put(uri, headers=headers, data=json_data)
        assert '200' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'OK' in res.data.decode()

    def test_update_role_duplicate(self):
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        headers = [('Content-Type', 'application/json')]
        data = dict(role="db")
        uri = '/api/role/%s' % ('web')

        json_data = json.dumps(data)
        res = self.app.put(uri, headers=headers, data=json_data)
        assert '500' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'Could not complete your request. may be duprecated.' in res.data.decode()

    def test_update_host(self):
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        headers = [('Content-Type', 'application/json')]
        data = dict(host_name="mem02",\
                ip="192.168.1.122",\
                role=["cache", "session"])
        uri = '/api/host/%s' % ('web01')

        json_data = json.dumps(data)
        res = self.app.put(uri, headers=headers, data=json_data)
        assert '200' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'OK' in res.data.decode()

    def test_update_host_duplicate(self):
        self.create_test_ip_data()
        self.create_test_role_data()
        self.create_test_host_data()
        self.create_test_role_map_data()
        headers = [('Content-Type', 'application/json')]
        data = dict(host_name="web02",\
                ip="192.168.1.122",\
                role=["cache", "session"])
        uri = '/api/host/%s' % ('web01')

        json_data = json.dumps(data)
        res = self.app.put(uri, headers=headers, data=json_data)
        assert '500' in str(res.status_code)
        assert 'application/json' in str(res.headers['Content-Type'])
        assert 'Could not complete your request. may be duprecated.' in res.data.decode()

if __name__ == '__main__':
    unittest.main()

