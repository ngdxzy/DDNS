import os
import shutil as sh
import socket as ss
import threading as th
import ddns_utils
import user_manager
import net_utils
import pandas as pd

class cmd:
    def __init__(self, server_port = 60000, client_port = 60001):
        self.server_port = server_port
        self.client_port = client_port
    
    def run(self):
        msg = input('> ')
        msg = msg.split()
        if msg[0] == "exit":
            return False
        elif msg[0] == "useradd":
            self.useradd(msg)
        elif msg[0] == "userdel":
            self.userdel(msg)
        elif msg[0] == "ls":
            self.check_status()
        
        return True
    
    def useradd(self, msg):
        name = msg[1]
        zone = msg[2]
        subnet = msg[3]
        user_manager.register_user(name, zone, subnet)
    
    def userdel(self, msg):
        name = msg[1]
        user_manager.remove_user(name)
    
    def check_status(self):
        table = pd.read_csv('registered_users.csv')
        print(table)