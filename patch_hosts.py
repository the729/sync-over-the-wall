# patch and restore hosts for resilio sync config

import os
if os.name == 'nt': import ctypes

def get_host_filename():
    if os.name == 'nt':
        return "C:\\Windows\\System32\\drivers\\etc\\hosts"
    elif os.name == 'posix':
        return "/etc/hosts"
    else:
        raise RuntimeError, "Unsupported operating system for this module: %s" % (os.name,)

def add_hosts_entry(ipaddress, hostname):
    filename = get_host_filename()
    outputfile = open(filename, 'a')
    entry = "\n" + ipaddress + "\t" + hostname + "\n"
    outputfile.writelines(entry)
    outputfile.close()

def del_hosts_entry(hostname):
    filename = get_host_filename()
    lines = open(filename, 'r').readlines()
    outputfile = open(filename, 'w')
    for line in lines:
        stripped = line.split("#", 1)[0]
        if hostname in stripped: continue
        outputfile.write(line)
    outputfile.close()

def is_admin():
    if os.name == 'nt':
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            traceback.print_exc()
            print "Admin check failed, assuming not an admin."
            return False
    elif os.name == 'posix':
        # Check for root on Posix
        return os.getuid() == 0
    else:
        raise RuntimeError, "Unsupported operating system for this module: %s" % (os.name,)

def sync_patch_hosts():
    if not is_admin():
        print "Need admin previledge. Please run as admin."
        return False

    add_hosts_entry("127.0.0.1", "config.resilio.com")
    return True

def sync_unpatch_hosts():
    if not is_admin():
        print "Need admin previledge. Please run as admin."
        return False

    del_hosts_entry("config.resilio.com")
    return True
