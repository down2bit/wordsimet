#!/usr/bin/python

from telnetlib import Telnet
from time import sleep
import struct 
import config

PROMPT="$ "
USER="root"
PASSWORD="morega2009"
VIDEO_FOLDER="/mnt/USB0disk1/qew_tx/"
SYS_FOLDER="/system/"

class Dongle:
    
    def __init__(self,sIP):
        self.IP = sIP
        self.tn = openTelnet(sIP)
        if self.tn == None:
            print 'telnet failed.'
    def reboot(self):
        self.tn.write("pwd\n")
        ret = self.tn.read_until(config.dongle.prompt,5)
        print "\ngoing to reboot\n",ret
        self.tn.write("reboot\n")
        print "wait 3 secs."
        sleep(3)
        self.tn.close()
        return "reboot"
    def deleteBlacklist(self):
        self.tn.write("cd /system\n")
        ret = self.tn.read_until(config.dongle.prompt,5)
        print ret
        self.tn.write("rm blacklist.txt\n")
        ret = self.tn.read_until(config.dongle.prompt,5)
        print ret
        self.tn.close()
        return ret
    def deleteFilter(self):
        self.tn.write("cd /system\n")
        ret = self.tn.read_until(config.dongle.prompt,5)
        print ret
        self.tn.write("rm tx_filter.txt\n")
        ret = self.tn.read_until(config.dongle.prompt,5)
        print ret
        self.tn.close()
        return ret
    def deleteAllVideo(self,fileID=''):
        self.tn.write("cd %s; ls\n"%(VIDEO_FOLDER))
        ret = self.tn.read_until(config.dongle.prompt,5)
##        if '0' != ret[0]:
##            return ret
        if fileID=='':
            self.tn.write("rm -f *.ts\n")
            ret=ret+self.tn.read_until(config.dongle.prompt,5)
            self.tn.write("rm -f *.mp4\n")
            ret=ret+self.tn.read_until(config.dongle.prompt,5)
            self.tn.write("rm -f *.xml\n")
            ret=ret+self.tn.read_until(config.dongle.prompt,5)
            self.tn.write("ls\n")
            ret=ret+self.tn.read_until(config.dongle.prompt,5)
            self.tn.close()
            return ret
        # to do : support one specific file
##            self.tn.write("ls  | wc \n")
##            ret=self.tn.read_until(PROMPT,5)
##            threeNum=ret.split()
##            if int(threeNum[0])==int(threeNum[1])==int(threeNum[2])==0:
##                return 0
##            else:
##                return 1
##        else:
##            self.tn.write("rm -f %s*\n"%(fileID))
##            ret=self.tn.read_until(PROMPT)
##            return 0
    def trace(self,startTrace=True):
        if startTrace:
            self.traceTelnet=openTelnet(self.IP)
            if self.traceTelnet:
                self.traceTelnet.write('tail -f /system/.debugLog/morega.log | grep "servlet: Command"  \n')
        else: # stop the tail -f command
            self.tn.write("killall -9 tail \n")
            print self.tn.read_until(config.dongle.prompt,5),"tail killed already?"
            self.traceTelnet.close()
            self.traceTelnet=None
        return self.traceTelnet
    def traceAll(self,startTrace=True):
        if startTrace:
            self.traceTelnet=openTelnet(self.IP)
            if self.traceTelnet:
                self.traceTelnet.write('tail -f /system/.debugLog/morega.log  \n')
        return self.traceTelnet
    def getTrace(self,timeout=5):
        return self.traceTelnet.read_until('\n',timeout)
def openTelnet(sIP):
    try:
        tn = Telnet(host=sIP,port=23)
        sleep(2)
        ind,re,strout=tn.expect(['login: ','$ ','# '],2)
        print "ind:",ind, "strout:",strout
        print "user:",config.dongle.user
        print "password:", config.dongle.password
        if ind==1:
            config.dongle.prompt='$ '
        elif ind==2:
            config.dongle.prompt='# '
        elif ind==0:
            #tn.read_until("login:".encode("ascii"))
            tn.write(config.dongle.user+'\n')
            print "USER:%s" %(config.dongle.user)
            ret=tn.read_until("Password:",5)
            tn.write(config.dongle.password+"\n")
            print "P:%s" %(config.dongle.password)
            ret=tn.read_until(config.dongle.prompt,5)
    except Exception as e:
        print "Exception caught:", e
        tn = None    
    return tn



def telnetCommand(tn, cmd, timeout=180):
    tn.write(cmd+'\n')
    ret = tn.read_until(PROMPT, timeout)
    return ret


    
if __name__ == "__main__":
    IP="192.168.0.100"
    for x in range(5):
        tn = openTelnet(IP)
        tn.close()		