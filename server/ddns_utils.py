from xml import dom
import pandas as pd
from datetime import datetime
import bind9_utils

def start_service(user_name, zone, IP):
    active_table = pd.read_csv('active_bindings.csv')
    if user_name not in active_table['username'].to_list():
        if bind9_utils.bind(zone=zone, domain_name=user_name, IP=IP):
            new_record = {}
            new_record['username'] = [user_name]
            new_record['zone'] = [zone]
            new_record['ip'] = [IP]
            new_record = pd.DataFrame(new_record)
            table = pd.concat([table, new_record],ignore_index=True)
            table.to_csv('active_bindings.csv', index=False)
            return True
        else:
            print("Failed to bind!")
            return False
    else:
        print("It is already on!")
        return True

def stop_service(user_name, zone):
    active_table = pd.read_csv('active_bindings.csv')
    if user_name in active_table['username'].to_list():
        if bind9_utils.unbind(zone=zone, domain_name=user_name):
            active_table.drop(active_table['username'].to_list().index(user_name), inplace=True)
            active_table.to_csv('active_bindings.csv',index=False)
            return True
        else:
            print("Failed to unbind!")
            return False
    else:
        print("It is already off!")
        return True

def check_availability(ss, user_name, IP):
    pass