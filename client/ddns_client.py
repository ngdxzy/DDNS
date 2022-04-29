import threading as th
import socket as ss
import time
import re
from netifaces import interfaces, ifaddresses, AF_INET

def get_valid_ip(eth_name):
    addresses = {}
    for ifaceName in interfaces():
        addresses[ifaceName] = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'-1.-1.-1.-1'}] )]
    #print(addresses)
    for itf_name, ip in addresses.items():
        if itf_name == eth_name:
            return ip[0]
    return '255.255.255.255'

def tcp_server(port, name):
    HOST = ''
    PORT = port
    ADDR = (HOST, PORT)
    tcpServer = ss.socket(ss.AF_INET, ss.SOCK_STREAM)
    try:
        tcpServer.bind(ADDR)
    except:
        # in case the address is taken by old threads, if so , reuse the address
        tcpServer.setsockopt(ss.SOL_SOCKET, ss.SO_REUSEADDR, 1)
        # connect again
        tcpServer.bind(ADDR)
    tcpServer.listen(1)
    while True:
        try:
            tcpConnection, addr = tcpServer.accept()
            data = tcpConnection.recv(1024)
            tcpConnection.send(name.encode('utf-8'))
            tcpConnection.close()
        except:
            pass

def udp_clinet(name, eth_name, udpClient):
    valid_ip = get_valid_ip(eth_name)
    msg = name + ' ' + valid_ip
    try:
        udpClient.sendto(msg.encode('utf-8'), ADDR)
    except:
        pass

if __name__ == "__main__":
    cfg = open('client.cfg')
    local_name = cfg.readline().strip()
    eth_name = cfg.readline().strip()
    server_ip = cfg.readline().strip()
    cfg.close()

    ddns_client_service = th.Thread(target=tcp_server, args=(60001, local_name,))
    ddns_client_service.start()
    HOST = server_ip
    PORT = 60000
    ADDR = (HOST, PORT)
    udpClient = ss.socket(ss.AF_INET, ss.SOCK_DGRAM, 0)
    udpClient.settimeout(1)
    while True:
        udp_clinet(local_name, eth_name, udpClient)
        time.sleep(60)

