## APIs to create required bind9 files
from ast import expr_context
import shutil as sh
import os
import time

def apply_ddns():
    os.system('cp db.* /etc/bind/')
    os.system('cp zones.* /etc/bind/')
    os.system('cp named.conf.local /etc/bind/')
    time.sleep(.01)
    os.system("service bind9 restart")

def create_zone(name):
    if os.path.exists('./zones.' + name):
        return

    with open("./templates/zones.template","r") as template_file, open("./zones." + name, "w") as new_zone_file:
        for line in template_file:
            new_zone_file.write(line.replace('TOREPLACE',name))

    sh.copy("./templates/db.template", "db." + name, )

    with open("named.conf.local","r") as cfg_old, open("named.conf.local.new","w") as cfg_new:
        flag = False
        for line in cfg_old:
            if line != '':
                cfg_new.write(line)
            elif '.' + name + '\"' in line:
                flag = True
        if not flag:
            cfg_new.write('\ninclude \"/etc/bind/zones.%s\";' % name)

    sh.move("named.conf.local.new", "named.conf.local")
    apply_ddns()


def bind(zone, domain_name, IP):
    # add forward record
    try:
        with open('db.' + zone,"r") as db_file_old, open('db.' + zone + ".temp","w") as db_new_file:
            for line in db_file_old:
                if domain_name + '.' + zone + '.' not in line:
                    db_new_file.write(line)
                if "NS records" in line:
                    db_new_file.write("\tIN NS %s.\n" % (domain_name + '.' + zone))
                if "NS mapping" in line:
                    db_new_file.write("%s.\tIN A %s\n" % ((domain_name + '.' + zone), IP))

        sh.move('db.' + zone + ".temp", 'db.' + zone)
        apply_ddns()
        return True
    except:
        return False


def unbind(zone, domain_name):
    try:
        with open('db.' + zone,"r") as db_file_old, open('db.' + zone + ".temp","w") as db_new_file:
            for line in db_file_old:
                if domain_name not in line:
                    db_new_file.write(line)

        sh.move('db.' + zone + ".temp", 'db.' + zone)
        apply_ddns()
        return True
    except:
        return False

def remove_zone(name):
    try:
        os.remove('db.' + name)
    except:
        pass
    try:
        os.remove('zones.' + name)
    except:
        pass
    os.remove('/etc/bind/db.' + name)
    os.remove('/etc/bind/zones.' + name)
    with open("named.conf.local","r") as cfg_old, open("named.conf.local.new","w") as cfg_new:
        for line in cfg_old:
            if '.' + name + '\"' not in line:
                cfg_new.write(line)

    sh.move("named.conf.local.new", "named.conf.local")
    os.system('cp named.conf.local /etc/bind/')
    os.system("service bind9 restart")
    # sh.move("named.conf.local", "/etc/bind/named.conf.local")
