import socket
import os
import re

from paramiko import PasswordRequiredException

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

dns_list = ['208.67.222.222' , '208.67.220.220' , '1.1.1.1' , '8.8.8.8' , '9.9.9.9' , '8.8.4.2']
configured_dns = []
url_list = ['google.it' , 'cisco.com' , 'apple.com' , 'microsoft.com']
test_list = {}
test_connection = {}
good_dns = []

def digcmd(url ,dns_ip):
    cmd = f"dig +noall +answer +time=2 +tries=1  @{dns_ip} {url}"
    output = os.popen(cmd).read()
    if len(output.splitlines()) == 0 : return False
    if re.match("^.*IN\tA.*$" , output.splitlines()[0]) : return True
    else : return False

def checkconnection(dns_ip):
    cmd = f"dig +noall +answer +time=2 +tries=1  @{dns_ip} www.google.com"
    output = os.popen(cmd).read()
    if len(output.splitlines()) == 0 : return True
    check = re.match("^.*connection.*timed.*out.*$" , output.splitlines()[0])
    #print("check" , check)
    if check : return False
    else : return True

def test_alldns():
    count=0
    for dns in dns_list :
        print("======"*count , f"{round(100/(len(dns_list)-1)*count,0)} %")
        count+=1
        connection = checkconnection(dns)
        if connection : 
            test_connection[dns] = True
        else : test_connection[dns] = False
        if test_connection[dns] : test_list[dns] = []
        for url in url_list :
            if test_connection[dns] :
                test_list[dns].append(digcmd(url ,dns))
            else : pass

def report():
    print(test_list)
    for k,v in test_connection.items() :
        if not v : print(f"{bcolors.FAIL}Failed to connect to DNS {k}{bcolors.WARNING} Skipped other tests. ")
    for k,v in test_list.items() :
        if all(v) : 
            print(f"{bcolors.OKGREEN} DNS {k} has resolved successfully all {bcolors.ENDC}")
            good_dns.append(k)
        else : print(f"{bcolors.FAIL}DNS {k} failed to resolve {bcolors.ENDC}")

def get_current_dns():
    with open("resolv.conf" , "r") as f :
        datalines = f.readlines()
    for line in datalines :
        if "nameserver" in line :
            line = line.strip()
            line=line.replace("nameserver" , "")
            line=line.replace(" " , "")
            line=line.replace("\t" , "")
            configured_dns.append(line)
    print(configured_dns)

test_alldns()
report()
get_current_dns()