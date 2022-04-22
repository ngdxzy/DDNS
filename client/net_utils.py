import re
from netifaces import interfaces, ifaddresses, AF_INET

def get_netmask(ip):
    netmask = []
    temp = ip[4]
    for i in range(4):
        if temp >= 8:
            netmask.append(255)
        elif temp > 0:
            netmask.append(256 - 2 ** (8 - temp))
        else:
            netmask.append(0)
        temp = temp - 8
    netmask.append(2 ** (-temp) - 1)
    return netmask

def do_netmask(ip,netmask):
    o_ip = ip.copy()
    for i in range(4):
        o_ip[i] = ip[i] & netmask[i]
    o_ip.append(ip[3] & netmask[4])
    return o_ip


def ifInSubnet(subnet,ip):
    ip_num = [int(n) for n in re.split('\.|/',ip)]
    subnet_num = [int(n) for n in re.split('\.|/',subnet)]
    netmask = get_netmask(subnet_num)
    ip_subnet = do_netmask(ip_num,netmask)
    ip_cmp = do_netmask(subnet_num[0:4],netmask)
    return ip_subnet[0:4] == ip_cmp[0:4]

def get_valid_ip(eth_name):
    addresses = {}
    for ifaceName in interfaces():
        addresses[ifaceName] = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'-1.-1.-1.-1'}] )]
    #print(addresses)
    for itf_name, ip in addresses.items():
        if itf_name == eth_name:
            return ip
    return '255.255.255.255'