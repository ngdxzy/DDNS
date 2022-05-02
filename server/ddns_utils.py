from xml import dom
from numpy import BUFSIZE
import pandas as pd
from datetime import datetime
import bind9_utils
import os
import shutil as sh
import socket as ss
import threading as th
import ddns_utils
import user_manager
import net_utils
import pandas as pd
import time

def check_alive(IP, port, name):
    HOST = IP
    PORT = port
    ADDR = (HOST, PORT)
    BUFSIZE = 1024
    tcpClient = ss.socket(ss.AF_INET, ss.SOCK_STREAM)
    tcpClient.settimeout(10)
    try:
        tcpClient.connect(ADDR)
        msg = "Alive?"
        tcpClient.send(msg.encode('utf-8'))
        ack = tcpClient.recv(BUFSIZE)
        if name in ack.decode('utf-8'):
            tcpClient.close()
            return True
        else:
            tcpClient.close()
            return False
    except:
        tcpClient.close()
        return False


def udp_server(port, msg_q):
    HOST = ''
    PORT = port
    ADDR = (HOST, PORT)
    BUFSIZ = 1024
    udpServer = ss.socket(ss.AF_INET, ss.SOCK_DGRAM)
    try:
        udpServer.bind(ADDR)
    except:
        # in case the address is taken by old threads, if so , reuse the address
        udpServer.setsockopt(ss.SOL_SOCKET, ss.SO_REUSEADDR, 1)
        # connect again
        udpServer.bind(ADDR)
    udpServer.settimeout(1)
    RUN_FLAG = True
    while RUN_FLAG:
        try:
            msg, addr = udpServer.recvfrom(BUFSIZ)
            msg = msg.decode('utf-8')
            msg = msg.split()
            table = pd.read_csv('registered_users.csv')
            Valid = False
            idx = -1
            for row in table.iterrows():
                if row[1]['username'] == msg[0] and row[1]['zone'] == msg[1]:
                    Valid = True
                    idx = row[0]
                    print("correct!")
                    break
            if Valid: # registered user?
                if table['ip'][idx] != msg[2] or table['active'][idx] == False: # ip changed or was inactive?
                    if net_utils.ifInSubnet(subnet=table['subnet'][idx], ip=msg[2]): # if the ip is valid
                        bind9_utils.bind(zone=table['zone'][idx], domain_name=table['username'][idx], IP=msg[2])
                        print(msg[0] + 'is now alive! ' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
                        table.loc[idx,'ip'] = msg[2]
                        table.loc[idx,'date'] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                        table.loc[idx,'active'] = True
                    else:
                        bind9_utils.unbind(zone=table['zone'][idx], domain_name=table['username'][idx])
                        table.loc[idx,'ip'] = msg[2]
                        table.loc[idx,'active'] = False
                table.to_csv('registered_users.csv', index=False)

        except:
            if not msg_q.empty():
                cmd = msg_q.get()
                if cmd == "exit":
                    RUN_FLAG = False
    udpServer.close()
    print("UDP server closed!")

def tcpClient(port, msg_q):
    RUN_FLAG = True
    while RUN_FLAG:
        table = pd.read_csv('registered_users.csv')
        for index, row in table.iterrows():
            if check_alive(row['ip'],port, row['username']):
                if not table.loc[index, 'active']:
                    print(row['username'] + " just alive!")
                    bind9_utils.bind(zone=row['zone'], domain_name=row['username'], IP=row['ip'])
                    table.loc[index, 'active'] = True
            else:
                if table.loc[index, 'active']:
                    table.loc[index, 'active'] = False
                    bind9_utils.unbind(zone=row['zone'], domain_name=row['username'])
                    print(row['username'] + " just dead! " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

        table.to_csv('registered_users.csv', index=False)
        for _ in range(60):
            time.sleep(1)
            if not msg_q.empty():
                cmd = msg_q.get()
                if cmd == "exit":
                    RUN_FLAG = False
                    break


class cmd:
    def __init__(self):
        pass

    def run(self):
        msg = input('> ')

        if msg == "":
            return True

        smsg = msg.split()
        if smsg[0] == "exit":
            return False
        elif smsg[0] == "ddns_useradd":
            if len(smsg) == 4:
                self.useradd(smsg)
            else:
                print('Syntax Wrong!')
        elif smsg[0] == "ddns_userdel":
            if len(smsg) == 2:
                self.userdel(smsg)
            else:
                print('Syntax Wrong!')
        elif smsg[0] == "ddns_ls":
            self.check_status()
        else:
            os.system(msg)

        return True

    def useradd(self, msg):
        name = msg[1]
        zone = msg[2]
        subnet = msg[3]
        user_manager.register_user(name, zone, subnet)
        bind9_utils.create_zone(msg[2])

    def userdel(self, msg):
        name = msg[1]
        user_manager.remove_user(name)

    def zonedel(self, msg):
        name = msg[1]
        user_manager.remove_user(name)

    def check_status(self):
        table = pd.read_csv('registered_users.csv')
        print(table)



# def start_service(user_name, zone, IP):
#     active_table = pd.read_csv('active_bindings.csv')
#     if user_name not in active_table['username'].to_list():
#         if bind9_utils.bind(zone=zone, domain_name=user_name, IP=IP):
#             new_record = {}
#             new_record['username'] = [user_name]
#             new_record['zone'] = [zone]
#             new_record['ip'] = [IP]
#             new_record = pd.DataFrame(new_record)
#             table = pd.concat([table, new_record],ignore_index=True)
#             table.to_csv('active_bindings.csv', index=False)
#             return True
#         else:
#             print("Failed to bind!")
#             return False
#     else:
#         print("It is already on!")
#         return True

# def stop_service(user_name, zone):
#     active_table = pd.read_csv('active_bindings.csv')
#     if user_name in active_table['username'].to_list():
#         if bind9_utils.unbind(zone=zone, domain_name=user_name):
#             active_table.drop(active_table['username'].to_list().index(user_name), inplace=True)
#             active_table.to_csv('active_bindings.csv',index=False)
#             return True
#         else:
#             print("Failed to unbind!")
#             return False
#     else:
#         print("It is already off!")
#         return True

