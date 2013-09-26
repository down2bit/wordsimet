'''
Created on Nov 24, 2011

@author: Qiyuesheng
'''
import unittest
import sqlite3
import os
import time
import config
PATH = "C:/PerData"
USERFILE = "userfile.dat"
class Userdb:
    """TableUser
  username:
  dictfile:
  password: #to do, should be MD5
  
      TableUserProfile
  username:
  passphrase:
  email:
  dayofbirth:
  registerDate:
    """
    def __init__(self, dbpath=PATH, dbfile=USERFILE):
        
        userfile = os.path.join(dbpath,USERFILE)
        self.db = sqlite3.connect(userfile)
        self.cursor=self.db.cursor()
        dbcmd = "create table if not exists TableUser (username text, dictfile text, password text)"
        self.cursor.execute(dbcmd)
    def adduser(self,username="",password="", dictfile=""):
        if username=="":
            YYYYmmdd=time.strftime("%Y%m%d")
            self.username= "guest"+YYYYmmdd
            self.password = YYYYmmdd[2:]
            self.dictfile = "dict"+YYYYmmdd+".dat"
        if dictfile == "":
            self.dictfile = self.username+".dat"
        self.cursor.execute("select username from TableUser")
        rows=self.cursor.fetchall()
        if len(rows)>=config.MAXUSER:
            return 1 #too much user
        elif (username,) in rows:
            return 2 #user exists
        dbcmd = "insert into tableuser values(?,?,?)" 
        self.cursor.execute(dbcmd,(username, dictfile, password) )
        self.db.commit()
        return 0 # successful
    def deluser(self,username=""):
        cmd = "delete from TableUser where username =?"
        self.cursor.execute(cmd,(username,))
        self.db.commit()
        return 0
    def setPassword(self,username,password,):
        cmd = "update TableUser set password = ? where username =?"
        self.cursor.execute(cmd,(password, username,))
        self.db.commit()
        return 0
    def setDictfile(self,username,dictfile,):
        cmd = "update TableUser set dictfile = ? where username =?"
        self.cursor.execute(cmd,(dictfile, username,))
        self.db.commit()
        return 0
    def getDictfile(self,username,password=""):
        dbcmd="select dictfile from TableUser where username =? and password=? "
        self.cursor.execute(dbcmd, (username,password))
        row = self.cursor.fetchone()
        dictfile = row[0] if row is not None else ""
        return dictfile
    def getUsers(self):
        dbcmd="select username, dictfile from TableUser"
        self.cursor.execute(dbcmd)
        user_dictfile = self.cursor.fetchall()
        return user_dictfile
        
    def removeuser(self,username=""):
        if username =="":
            self.cursor.execute( "delete from tableuser")
        else:
            self.cursor.execute ("delete from tableuser where username = ?", (username,))
        self.db.commit()
    def close(self):
        self.db.close()
class User():
    def __init__(self,username="",password="",dictfile=""):
        self.username=username
        self.password=password
        self.dictfile=dictfile
class TestUserdb(unittest.TestCase):


    def setUp(self):
        self.userdb = Userdb()


    def tearDown(self):
        self.userdb.db.close()
        pass


    def testAddUser(self):
        self.userdb.adduser("ys", "ysdict.dat","1111")
        
        pfile = self.userdb.getDictfile("ys")
        self.assertEqual(pfile,"ysdict.dat", "!=".join((pfile,"ysdict.dat")))
        ret = self.userdb.adduser("ys","ysdict.dat","9999")
        self.assertEqual(ret,2, "same user added, ys")
        self.userdb.removeuser("ys")
    def testGetUser(self):
        self.userdb.adduser("x", "xdict.dat","1111")
        self.userdb.adduser("y", "ydict.dat","2222")
        self.userdb.adduser("z", "zdict.dat","3333")
        
        user_file = self.userdb.getUsers()
        self.assertIn(("x","xdict.dat"),user_file, str(user_file))
        self.assertIn(("z","zdict.dat"),user_file, str(user_file))
        self.assertIn(("y","ydict.dat"),user_file, str(user_file))
        self.userdb.removeuser("x")
        self.userdb.removeuser("y")
        self.userdb.removeuser("z")

class perdict():
    def __init__(self,dicfile):
        self.db=sqlite3.connect(dicfile)
        self.cursor=self.db.cursor()
        # if dicfile is not a file, create the file
        # if the size is 0, create table
        self.createTable()
        self.populateFirst(level=15)
    def populateFirst(self,level=15):
        self.cursor.execute("select count(*) from pdict")
        num=self.cursor.next()[0]
        if num>level*100: return
        global first3k_file
        filein=file(first3k_file)
        wordin=filein.read().split("\n")
        print len(wordin),"total first 3k"
        for w in wordin:
            if "###" in w:
                continue
            if self.isInPerdict(w.strip()):
                continue
            self.insert(w.strip())
            print w.strip(),
    def isInPerdict(self,word):
        rows=self.lookup(word)
        if len(rows)>0:
            return True
        else:
            return False
    def insert(self,word,meaning='',sentence=''):
        self.cursor.execute("""insert into pdict values (?,?,?,?)""", (word,meaning,sentence,time.strftime("%Y-%m-%d")))
        self.db.commit()
    def savenew(self,wordlist,article=""):
        if article !="":
            for word in wordlist:
                meaning = self.lookupWordnet(word)
                sentence = self.findsentence(word, article)
                self.insert(word, meaning, sentence)
        else:
            for word in wordlist:
                self.insert(word[0],word[1],word[2])
    def createTable(self):
        self.cursor.execute("""create table if not exists pdict (word text, meaning text, sentence text, date text)""")
    def lookup(self,word):
        self.cursor.execute("select * from pdict where word=?",(word,))
    
        return self.cursor.fetchmany()
    def getToday(self):
        self.cursor.execute("""select word, meaning,sentence from pdict where date=?""",(time.strftime("%Y-%m-%d"),))
        return self.cursor.fetchall()
    def lookupWordnet(self,word):
        syns=wn.synsets(word)
        if len(syns)>0:
            return syns[0].definition
        else:
            return ""
    def profile(self):
        self.cursor.execute("""select count(*) from pdict""")
        return self.cursor.fetchone()
    def close(self):
        self.db.close()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()