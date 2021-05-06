#Monitor SMOS test
import paramiko
from apscheduler.schedulers.blocking import BlockingScheduler
from pysnmp.hlapi import *


def ssh_test() :
    #host = "test.rebex.net"
    host = "10.1.1.1"
    port = 22
    username = "demo"
    password = "password"
    ssh = paramiko.SSHClient()
    connection_error = False
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try :
        print("connection to fake host to generate snmp")
        ssh.connect(host, port, username, password)
        ssh.close()
    except :
        connection_error = True
    return connection_error

def test_job():
    if ssh_test() : send_trap()
    else : print("SSH connection is alive")


def send_trap():
    iterator = sendNotification(
        SnmpEngine(),
        CommunityData('community_test', mpModel=0),
        UdpTransportTarget(('solarwinds.com', 162)),
        ContextData(),
        'trap',
        NotificationType(
            ObjectIdentity('1.3.6.1.6.3.1.1.5.2')
        ).addVarBinds(
            ('1.3.6.1.6.3.1.1.4.3.0', '1.3.6.1.4.1.20408.4.1.1.2'),
            ('1.3.6.1.2.1.1.1.0', OctetString('my system'))
        ).loadMibs(
            'SNMPv2-MIB'
        )
    )
    next(iterator)


scheduler = BlockingScheduler()
#scheduler.add_job(some_job, 'interval', hours=1)
scheduler.add_job(test_job, 'interval', seconds=10)
scheduler.start()