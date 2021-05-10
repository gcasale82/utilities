#Monitor SMOS test
import paramiko
from apscheduler.schedulers.blocking import BlockingScheduler
from pysnmp.hlapi import *
import argparse
import getpass
import logging
import logging.handlers
import os
import daemon
import datetime


class test_ssh():
    def __init__(self,host,user,password,interval,unit):
        self.host=host
        self.user=user
        self.password = password
        self.interval=interval
        self.unit = unit
        self.scheduler = BlockingScheduler()
        self.connection_error = False


    def ssh_test(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self.host, 22 , self.user, self.password , timeout=5)
            ssh.close()
        except:
            self.connection_error = True

    def write_log(self):
        file_path = r'/var/log/monitor_ssh.log'
        logging.basicConfig(filename= file_path ,
                            #format='%(asctime)s %(message)s',
                            filemode='w')
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        if self.connection_error : logger.error(f"{datetime.datetime.now()} - SSH connection to {self.host} was lost , SNMP trap has been sent to Solarwinds ")
        else : logger.info(f"{datetime.datetime.now()} - SSH connection to {self.host} is alive ")
        handler = logging.handlers.RotatingFileHandler(file_path , maxBytes=200000,
                                      backupCount=5)
        logger.addHandler(handler)

    def test_job(self):
        self.ssh_test()
        if self.connection_error :
            self.send_trap()
            self.write_log()
        else:
            self.write_log()


    def send_trap(self):
        iterator = sendNotification(
            SnmpEngine(),
            CommunityData('community_test', mpModel=0),
            UdpTransportTarget(('74.1.1.1', 162)),
            ContextData(),
            'trap',
            NotificationType(
                ObjectIdentity('1.3.6.1.6.3.1.1.5.2')
            ).addVarBinds(
                ('1.3.6.1.6.3.1.1.4.3.0', '1.3.6.1.4.1.20408.4.1.1.2'),
                ('1.3.6.1.2.1.1.1.0', OctetString('Smos backup connection failed'))
            ).loadMibs(
                'SNMPv2-MIB'
            )
        )
        next(iterator)
    def run_job(self):
        if self.unit == "seconds" :
            self.scheduler.add_job(self.test_job, 'interval', seconds = self.interval)
        elif self.unit == "minutes" :
            self.scheduler.add_job(self.test_job, 'interval', minutes=self.interval)
        elif self.unit == "hours" :
            self.scheduler.add_job(self.test_job, 'interval', hours=self.interval)
        self.scheduler.start()


def main() :
    my_parser = argparse.ArgumentParser(prog='monitor_ssh',
                                        usage='%(prog)s host_ip_address user interval seconds/minutes/hours',
                                        description='Monitor ssh connection , log report , snmp trap generation ')

    my_parser.add_argument('--host', action='store', type=str, required=True, help="host ip address to be monitored")
    my_parser.add_argument('--user', action='store', type=str, required=True, help="user for the ssh connection")
    my_parser.add_argument('--interval', action='store', type=int, required=True, help="interval of job scheduler")
    my_parser.add_argument('--unit', action='store', choices=['seconds', 'minutes', 'hours'])
    args=my_parser.parse_args()
    password = getpass.getpass()
    with daemon.DaemonContext():
        run_ssh = test_ssh(args.host,args.user,password, args.interval,args.unit)
        run_ssh.run_job()




main()