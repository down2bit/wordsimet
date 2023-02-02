#!/usr/bin/env python
#-*- coding: utf-8 -*-
# 
import unittest
import os
import  sys
#import imp
#import ConfigParser as configparser
import time
IGNORE_LEN = 3
DEBUG=True
CONFIGFILE="config.txt"
HELPFILE="help.txt"
LOGFILE = "wim.log"
TIMEFORMAT="%y/%m/%d %H:%M:%S"
LIGHT_GREY=(235,235,235)
MAXFONT =50
MINFONT =10
fontsize = 15
#---------
MAXUSER = 5
user="qiyuesheng"
datafile="./Perdict/qiys.dic"
KNOWN_VOCABULARY = 3000
minLength = 4
NORMAL = 5
defaultcmd = "nextPage"
knownLimit = 10 # if familarity is greater than the value, the word becomes known, no more new
changeInOneDay = True # words can be updated twice within one day
pagesize = 1000
newPerPage = 10
#---------
def timestamp():
    return time.strftime(TIMEFORMAT)
def get_main_dir():
    """if  (hasattr(sys,"frozen") or imp.is_frozen("__main__")):
        return os.path.dirname(sys.executable) #os.environ["_MEIPASS2"] #
    return os.path.dirname(sys.argv[0]) """
    return os.path.dirname(__file__)
def get_data_dir():
    """if  (hasattr(sys,"frozen") or imp.is_frozen("__main__")):
        return os.environ["_MEIPASS2"] #os.path.dirname(sys.executable) #
    return os.path.dirname(sys.argv[0]) """
    return os.path.dirname(__file__)
class logger():
    def __init__(self, logfile=LOGFILE):
        path = os.path.dirname(__file__)
        logfile = os.path.join(path, logfile)
        self.fileout=open(logfile, 'a')

    def write(self,mesg):
        if DEBUG: print(mesg)
        self.fileout.write(time.ctime().split()[-2] + ' '+mesg.encode('utf-8')+'\n')

    def close(self):
        self.fileout.close()

log=logger()
      
if __name__ == "__main__":
    unittest.main() 
