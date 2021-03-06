#!/tools/miniconda3/bin/python3
import os
import shutil as sh
import socket as ss
import threading as th
from ddns_utils import cmd
from ddns_utils import udp_server
from ddns_utils import check_alive, tcpClient
from queue import Queue
import pandas as pd
import bind9_utils


if __name__ == "__main__":
    msg_q_udp = Queue()
    msg_q_tcp = Queue()
    table = pd.read_csv('registered_users.csv')
    print("Initialize! Check all registered users!")
    for index, row in table.iterrows():
        if check_alive(row['ip'],60001, row['username']):
            print(row['username'] + " alive!")
            bind9_utils.bind(zone=row['zone'], domain_name=row['username'], IP=row['ip'])
            table.loc[index, 'active'] = True
        else:
            if row['active']:
                table.loc[index, 'active'] = False
                bind9_utils.unbind(zone=row['zone'], domain_name=row['username'])
            print(row['username'] + " dead!")

    table.to_csv('registered_users.csv', index=False)
    print("Init. done!")
    ddns_server_service = th.Thread(target=udp_server, args=(60000, msg_q_udp, ))
    ddns_check_service = th.Thread(target=tcpClient, args=(60001, msg_q_tcp, ))
    ddns_server_service.start()
    ddns_check_service.start()
    cmd_tool = cmd()
    RUN_FLAG = True
    while RUN_FLAG:
        RUN_FLAG = cmd_tool.run()
    msg_q_tcp.put("exit")
    msg_q_udp.put("exit")
    ddns_server_service.join()
    ddns_check_service.join()
    table = pd.read_csv('registered_users.csv')
    for index, row in table.iterrows():
        if row['active']:
            table.loc[index, 'active'] = False
            bind9_utils.unbind(zone=row['zone'], domain_name=row['username'])
    table.to_csv('registered_users.csv', index=False)
