import re

def is_valid_ip(ip):
    valid_ip = '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
    result = re.match(valid_ip, ip)
    if result:
        return True
    else:
        return False

def is_valid_keys(d, keys):
    for key in keys:
        if key not in d:
            return False
    return True
