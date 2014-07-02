from flask import (
    request, jsonify, abort, make_response, current_app
)

from srvadm import app, db
from srvadm.models import Role, IP, Host, RoleMap
from srvadm.validator import is_valid_ip, is_valid_keys
from srvadm.decorator import crossdomain

from functools import update_wrapper
from datetime import timedelta

# IP
@app.route('/api/list/ip')
@crossdomain(origin='*')
def list_ip():
    fmt = request.args.get('format')

    ips = IP.get_all(db.session.query)
    result = [r.ip for r in ips]
    return formatter(fmt, result)


@app.route('/api/list/ip/used')
@crossdomain(origin='*')
def list_ip_used():
    fmt = request.args.get('format')

    ips = IP.get_used(db.session.query)
    result = [r.ip for r in ips]
    return formatter(fmt, result)


@app.route('/api/list/ip/unused')
@crossdomain(origin='*')
def list_ip_unused():
    fmt = request.args.get('format')

    ips = IP.get_unused(db.session.query)
    result = [r.ip for r in ips]
    return formatter(fmt, result)


@app.route('/api/list/ip/role/<string:role_name>')
@crossdomain(origin='*')
def list_ip_by_role(role_name):
    fmt = request.args.get('format')

    role_maps = RoleMap.get_by_role_name(db.session.query, role_name)
    host_names = [role_map.host_name for role_map in role_maps]
    hosts = Host.get_in_host_names(db.session.query, host_names)
    result = [r.ip for r in hosts]
    return formatter(fmt, result)


# TODO: test
@app.route('/api/ip')
@crossdomain(origin='*')
def all_ip():
    result = []
    ips = IP.get_all(db.session.query)
    for ip in ips:
        result.append(dict(ip=ip.ip, is_used=ip.is_used))
    return jsonify(result=result)

@app.route('/api/ip/<string:ipaddr>')
@crossdomain(origin='*')
def search_by_ip(ipaddr):

    host = Host.get_one_by_ip(db.session.query, ipaddr)
    if not host:
        abort(404)

    role_maps = RoleMap.get_by_host_name(db.session.query, host.host_name)
    role_names = [r.role_name for r in role_maps]

    result = [dict(host_name=host.host_name, ip=host.ip, role=role_names)]
    return jsonify(result=result)


@app.route('/api/ip', methods=['POST'])
@crossdomain(origin='*')
def add_ip():
    if not is_json_request(request) or not is_valid_keys(request.json, ['ip']):
        abort(400)
    ipaddr = request.json['ip']

    if not is_valid_ip(ipaddr):
        abort(400)
    try:
        check_registerable_ip(ipaddr)
        ip = IP(ip=ipaddr)
        db.session.add(ip)
        db.session.commit()
    except Exception as e:
        abort(500)
    return jsonify(result=[dict(message='OK', request='add ip', payload=str(request.json))])


@app.route('/api/ip/<string:old_ipaddr>', methods=['PUT'])
@crossdomain(origin='*')
def update_ip(old_ipaddr):
    if not is_json_request(request) or not is_valid_keys(request.json, ['ip']):
        abort(400)
    new_ipaddr = request.json['ip']

    if not is_valid_ip(new_ipaddr):
        abort(400)
    try:
        check_registerable_ip(new_ipaddr)
        ip = IP.get_one(db.session.query, old_ipaddr)
        if ip.is_used == 1:
            ip.is_used = 1
        ip.ip = new_ipaddr
        db.session.commit()
    except Exception as e:
        abort(500)
    return jsonify(result=[dict(message='OK', request='update ip', payload=str(request.json))])


@app.route('/api/ip/<string:ipaddr>', methods=['DELETE'])
@crossdomain(origin='*')
def delete_ip(ipaddr):

    if not is_valid_ip(ipaddr):
        abort(400)
    try:
        delete_unused_ip(ipaddr)
        db.session.commit()
    except Exception as e:
        print(ipaddr)
        print(e)
        abort(500)
    return jsonify(result=[dict(message='OK', request='delete ip', payload=str(request.json))])


def delete_unused_ip(ipaddr):
    ip = IP.get_one(db.session.query, ipaddr)
    if ip:
        if ip.is_used == 1:
            raise
        try:
            db.session.delete(ip)
        except Exception as e:
            raise

# Role
@app.route('/api/list/role')
@crossdomain(origin='*')
def list_role():
    fmt = request.args.get('format')

    roles = Role.get_all(db.session.query)
    result = [r.role_name for r in roles]
    return formatter(fmt, result)

@app.route('/api/role', methods=['GET'])
@crossdomain(origin='*')
def all_role():
    result = []
    roles = Role.get_all(db.session.query)
    for role in roles:
        result.append(dict(role=role.role_name))
    return jsonify(result=result)

@app.route('/api/role/<string:role_name>', methods=['GET'])
@crossdomain(origin='*')
def search_by_role(role_name):
    role_maps = RoleMap.get_by_role_name(db.session.query, role_name)
    host_names = [r.host_name for r in role_maps]

    hosts = Host.get_in_host_names(db.session.query, host_names)
    if len(hosts) == 0:
        abort(404)

    result = []
    for host in hosts:
        d = {}
        d['host_name'] = host.host_name
        d['ip'] = host.ip
        d['role'] = [r.role_name for r in host.role]
        result.append(d)
    return jsonify(result=result)


@app.route('/api/role', methods=['POST'])
@crossdomain(origin='*')
def add_role():
    if not is_json_request(request) and not is_valid_keys(request.json, ['role']):
        abort(400)

    role_name = request.json['role']
    try:
        role = Role(role_name=role_name)
        db.session.add(role)
        db.session.commit()
    except Exception as e:
        abort(500)
    return jsonify(result=dict(message='OK', request='add role', payload=str(request.json)))


@app.route('/api/role/<string:role_name>', methods=['DELETE'])
@crossdomain(origin='*')
def delete_role(role_name):
    try:
        role = Role.get_one(db.session.query, role_name)
        if role:
            db.session.delete(role)
            db.session.commit()
    except Exception as e:
        abort(500)
    return jsonify(result=dict(message='OK', request='delete role', payload=str(request.json)))


@app.route('/api/role/<string:old_role_name>', methods=['PUT'])
@crossdomain(origin='*')
def update_role(old_role_name):
    if not is_json_request(request) or not is_valid_keys(request.json, ['role']):
        abort(400)
    new_role_name = request.json['role']

    try:
        role = Role.get_one(db.session.query, old_role_name)
        role.role_name = new_role_name
        db.session.commit()
    except Exception as e:
        abort(500)
    return jsonify(result=[dict(message='OK', request='update role', payload=str(request.json))])

# Host
@app.route('/api/list/host')
@crossdomain(origin='*')
def list_host():
    fmt = request.args.get('format')

    hosts = Host.get_all(db.session.query)
    result = [r.host_name for r in hosts]
    return formatter(fmt, result)


@app.route('/api/host/<string:host_name>')
@crossdomain(origin='*')
def search_by_host(host_name):
    host = Host.get_one_by_host_name(db.session.query, host_name)
    if not host:
        abort(404)

    role_maps = RoleMap.get_by_host_name(db.session.query, host.host_name)
    role_names = [r.role_name for r in role_maps]

    result = [dict(host_name=host.host_name, ip=host.ip, role=role_names)]
    return jsonify(result=result)


# TODO: test
@app.route('/api/host')
@crossdomain(origin='*')
def all_host():
    hosts = Host.get_all(db.session.query)
    if len(hosts) == 0:
        abort(404)

    result = []
    for host in hosts:
        d = {}
        d['host_name'] = host.host_name
        d['ip'] = host.ip
        d['role'] = [r.role_name for r in host.role]
        result.append(d)
    return jsonify(result=result)


@app.route('/api/host', methods=['POST'])
@crossdomain(origin='*')
def add_host():
    if not is_json_request(request):
        return abort(400)

    req = request.json
    if not is_valid_keys(req, ['host_name', 'ip', 'role']):
        abort(400)
    try:
        register_new_host(req['host_name'], req['ip'], req['role'])
        db.session.commit()
    except Exception as e:
        abort(500)

    return jsonify(result=dict(message='OK', request='add host', payload=str(request.json)))


@app.route('/api/host/<string:old_host_name>', methods=['PUT'])
@crossdomain(origin='*')
def update_host(old_host_name):
    if not is_json_request(request):
        return abort(400)

    req = request.json
    if not is_valid_keys(req, ['host_name', 'ip', 'role']):
        abort(400)

    try:
        role_maps = RoleMap.get_by_host_name(db.session.query, old_host_name)
        for r in role_maps:
            rm = RoleMap.get_by_host_name_and_role_name(db.session.query, old_host_name, r.role_name)
            db.session.delete(rm)
            db.session.flush()

        host = Host.get_one_by_host_name(db.session.query, old_host_name)
        host.host_name = req['host_name']
        old_ip = host.ip
        host.ip = req['ip']
        host.role = [RoleMap(role_name=role_name) for role_name in req['role']]
        db.session.add(host)

        if req['ip'] != old_ip:
            ip = IP.get_one(db.session.query, req['ip'])
            ip.is_used = 1
            ip = IP.get_one(db.session.query, old_ip)
            ip.is_used = 0

        db.session.commit()
    except Exception as e:
        abort(500)
    return jsonify(result=[dict(message='OK', request='update host', payload=str(request.json))])


@app.route('/api/host/<string:host_name>', methods=['DELETE'])
@crossdomain(origin='*')
def delete_host(host_name):
    try:
        host = Host.get_one_by_host_name(db.session.query, host_name)
        if host:
            db.session.delete(host)
            ip = IP.get_one(db.session.query, host.ip)
            ip.is_used = 0
            db.session.commit()
    except Exception as e:
        abort(500)
    return jsonify(result=dict(message='OK', request='delete host', payload=str(request.json)))

# TODO: refactor
def register_new_host(host_name, ipaddr, role_names):
    try:
        # is exist unused ip
        ip = IP.get_one(db.session.query, ipaddr)
        if not ip or ip.is_used == 1:
            raise Exception("ip does not exist or used")
        ip.is_used = 1
        db.session.flush()

        # is exist role in db
        roles = Role.get_in_role_names(db.session.query, role_names)
        if len(roles) != len(role_names):
            raise Exception("role not found")
        
        # insert host
        host = Host(host_name=host_name, ip=ipaddr)
        host.role = [RoleMap(role_name=role_name) for role_name in role_names]
        db.session.add(host)
    
    except Exception as e:
        raise e

# hosts
@app.route('/api/hosts_output/<string:role_name>')
@crossdomain(origin='*')
def output_hosts(role_name):
    role_maps = RoleMap.get_by_role_name(db.session.query, role_name)
    host_names = [role_map.host_name for role_map in role_maps]

    hosts = Host.get_in_host_names(db.session.query, host_names)
    if len(hosts) == 0:
        abort(404)

    result = [dict(host_name=host.host_name, ip=host.ip) for host in hosts]
    return formatter('hosts', result)

# Common
@app.errorhandler(405)
@crossdomain(origin='*')
def method_not_allowed(e):
    return jsonify(message='Method not allowed'), 405

@app.errorhandler(404)
@crossdomain(origin='*')
def not_found(e):
    return jsonify(message='Not found'), 404

@app.errorhandler(400)
@crossdomain(origin='*')
def bad_request(e):
    return jsonify(message='Check the format you requested'), 400

@app.errorhandler(500)
@crossdomain(origin='*')
def internal_server_error(e):
    return jsonify(message='Could not complete your request. may be duprecated.'), 500

def formatter(fmt, rs):
    if fmt == 'csv':
        ret = ''
        for r in rs:
            ret = "%s%s," % (ret, r)
        ret = ret[:len(ret)-1]
        return ret
    elif fmt == 'space':
        ret = ''
        for r in rs:
            ret = "%s%s " % (ret, r)
        ret = ret[:len(ret)-1]
        return ret
    elif fmt == 'hosts':
        ret = ''
        for r in rs:
            ret = "%s%s\t%s\n" % (ret, r['ip'], r['host_name'])
        return ret
    else:
        return jsonify(result=rs)

def is_json_request(req):
    try:
        req.json
        return True
    except:
        return False

def check_registerable_ip(ipaddr):
    try:
        ip = IP.get_one(db.session.query, ipaddr)
    except Exception as e:
        raise

