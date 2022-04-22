from multiprocessing.pool import RUN
import net_utils
import threading as th
from queue import Queue
import socket as ss
import time
def tcp_server(port, msg_q):
    pass

def udp_clinet(name, eth_name, port, IP, msg_q):
    HOST = IP
    PORT = port
    ADDR = (HOST, PORT)
    udpClient = ss.socket(ss.AF_INET, ss.SOCK_DGRAM, 0)
    udpClient.settimeout(1)
    RUN_FLAG = True
    while RUN_FLAG:
        try:
            valid_ip = net_utils.get_valid_ip(eth_name)
            msg = name + ' ' + valid_ip
            udpClient.sendto(msg.encode('utf-8'), ADDR)
        except:
            pass
        for i in range(60):
            if not msg_q.empty():
                cmd = msg_q.get()
                if cmd == "exit":
                    RUN_FLAG = False
            time.sleep(1)

if __name__ == "__main__":
    msg_q_tcp = Queue()
    msg_q_udp = Queue()
    cfg = open('client.cfg')
    local_name = cfg.read()
    server_ip = cfg.read()
    cfg.close()


