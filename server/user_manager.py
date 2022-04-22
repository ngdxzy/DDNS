import pandas as pd
from datetime import datetime
import bind9_utils
def get_time():
    return datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

def register_user(user_name, zone, subnet):
    table = pd.read_csv('registered_users.csv')
    if user_name not in table['username'].to_list():
        if zone not in table['zone'].to_list():
            print("New Zone!")
            bind9_utils.create_zone(zone)
        print("Add new user %s!" % user_name)
        new_record = {}
        new_record['username'] = [user_name]
        new_record['zone'] = [zone]
        new_record['subnet'] = [subnet]
        new_record['ip'] = ['x']
        new_record['date'] = [get_time()]
        new_record['active'] = [False]
        new_record = pd.DataFrame(new_record)
        table = pd.concat([table, new_record],ignore_index=True)
        print(table)
        table.to_csv('registered_users.csv',index=False)
    else:
        print("The user already exists!")

def remove_user(user_name):
    table = pd.read_csv('registered_users.csv')
    if user_name in table['username'].to_list():
        this_zone = table['zone'][table['username'].to_list().index(user_name)]
        table.drop(table['username'].to_list().index(user_name), inplace=True)
        bind9_utils.unbind(this_zone, user_name)
        if this_zone not in table['zone'].to_list(): # This zone nolonger exists
            bind9_utils.remove_zone(this_zone)
        table.to_csv('registered_users.csv',index=False)

def update_info(user_name, new_ip):
    table = pd.read_csv('registered_users.csv')
    if user_name in table['username'].to_list():
        idx = table['username'].to_list().index(user_name)
        table['ip'][idx] = new_ip
        table['date'][idx] = get_time()
        table.to_csv('registered_users.csv',index=False)


