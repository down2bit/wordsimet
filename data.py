"""database manipulate"""
import sqlite3
class MyDatabase():
    def __init__(self, filename):
        self.filename = filename
        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()
    def createSENTENCES(self):
        self.cursor.execute("""create table if not exists
                SENTENCES
                (sid integer primary key,
                sentence text,
                source text)
                """)
    def createNEWLIST(self):
        self.cursor.execute("""create table if not exists
                NEWLIST
                (wid integer primary key,
                spell text,
                mydef text)
                """)
    def createKNOWNLIST(self):
        self.cursor.execute("""create table if not exists
                KNOWNLIST
                (wid integer primary key,
                spell text,
                mydef text,
                lastdate date)
                """)
    def createEXTRALIST(self):
        """This table to store words not found in public library,
        like names of people, places and organization etc,
        technical term
        """
        self.cursor.execute("""create table if not exists
                EXTRALIST
                (wid integer primary key,
                spell text,
                mydef text)
                """)
    def createWORDMEET(self):
        """This table to record when a new word appears to user in which sentence."""
        self.cursor.execute("""create table if not exists
                WORDMEET
                (wid integer,
                sid integer,
                dt date)
                """)
    def createWORDSTAT(self):
        """This table to mark statistics of a new word.
        metcount  -- how many time I meet this word, initialized to 1
        familarity  -- from 1 to 9, 1 means quite new, 9 means it will be known, 
        importance -- from 1 to 9, 1 is basic word, 9 rarely used, default to 5
        """
        self.cursor.execute("""create table if not exists
                WORDSTAT
                (wid integer,
                metcount number,
                familarity number,
                importance number,
                lastmet  date)
                """)
    def createTables(self):
        self.createSENTENCES()
        self.createNEWLIST()
        self.createKNOWNLIST()
        self.createEXTRALIST()
        self.createWORDMEET()
        self.createWORDSTAT()
    def dropTables(self):
        self.cursor.execute("drop table if exists SENTENCES")
        self.cursor.execute("drop table if exists NEWLIST")
        self.cursor.execute("drop table if exists KNOWNLIST")
        self.cursor.execute("drop table if exists EXTRALIST")
        self.cursor.execute("drop table if exists WORDMEET")
        self.cursor.execute("drop table if exists WORDSTAT")

class User():
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor
    def addNew(self, spell, sntnc="", src=""):
        #self.cursor.execute("begin transaction")
        sid = wid = 0
        if sntnc:
            self.cursor.execute("insert into SENTENCES values (NULL,?,?)",(sntnc,src))
            self.cursor.execute("select last_insert_rowid()")
            sid = self.cursor.fetchone()[0]
        self.cursor.execute("insert into NEWLIST values(NULL,?,'')", (spell,))
        self.cursor.execute("select last_insert_rowid()")
        wid = self.cursor.fetchone()[0]
        self.cursor.execute("select date('now')")
        today = self.cursor.fetchone()[0]
        self.cursor.execute("insert into WORDMEET values(?,?,?)",(wid, sid,today))
        self.cursor.execute("insert into WORDSTAT values(?,1,1,5,?)",(wid,today))
    def updateNew(self, spell, sntnc="", src=""):
        sid = wid = 0
        if sntnc:
            self.cursor.execute("insert into SENTENCES values (NULL,?,?)",(sntnc,src))
            self.cursor.execute("select last_insert_rowid()")
            sid = self.cursor.fetchone()[0]
        self.cursor.execute("select wid from NEWLIST where spell = ?", (spell,))
        wid = self.cursor.fetchone()[0]
        self.cursor.execute("select date('now')")
        today = self.cursor.fetchone()[0]
        self.cursor.execute("insert into WORDMEET values(?,?,?)",(wid, sid,today))
        self.cursor.execute("update WORDSTAT set \
                            metcount=metcount+1, familarity=familarity+1,lastmet=?\
                            where wid =?",  (today,wid))
    def becomeKnown(self,aword,comment=''):
        wid = 0
        cmd = "select wid from newlist where spell = ?"
        self.cursor.execute(cmd,(aword,))
        wid = self.cursor.fetchone()[0]
        cmd = "delete from newlist where wid = ?"
        self.cursor.execute(cmd,(wid,))
        cmd = "delete from wordmeet where wid = ?"
        self.cursor.execute(cmd,(wid,))
        cmd = "delete from wordstat where wid = ?"
        self.cursor.execute(cmd,(wid,))
        cmd = "insert into knownlist values (?,?,?,date('now')) "
        self.cursor.execute(cmd, (wid,aword,comment))
    def isNew(self, aword):
        cmd = "select oid from NEWLIST where spell=?"
        self.cursor.execute(cmd,(aword,))
        if len(self.cursor.fetchall())>0:
            return True
        else:
            return False
    def isKnown(self, aword):
        cmd = "select oid from KNOWNLIST where spell=?"
        self.cursor.execute(cmd,(aword,))
        if len(self.cursor.fetchall())>0:
            return True
        else:
            return False
    def getNew(self):
        cur = self.cursor
        cmd = "select * from NEWLIST"
        cur.execute(cmd)
        return cur.fetchall()
    def getSentence(self):
        cur = self.cursor
        cmd = "select * from SENTENCES"
        cur.execute(cmd)
        return cur.fetchall()
    def getStat(self):
        cur = self.cursor
        cmd = "select * from WORDSTAT"
        cur.execute(cmd)
        return cur.fetchall()
    def getMeet(self):
        cur = self.cursor
        cmd = "select * from WORDMEET"
        cur.execute(cmd)
        return cur.fetchall()
if __name__ == "__main__":
    mydb = MyDatabase("example.db")
    #mydb.dropTables()
    #mydb.createTables()
    user = User(mydb)
    print(user.getNew())
    print(user.getSentence())
    print(user.getStat())
    print(user.getMeet())
    user.addNew("hello", "hello,world.")
    print(user.getNew())
    print(user.getSentence())
    print(user.getStat())
    print(user.getMeet())
    assert user.getNew() == [(1,'hello',''),]
    assert user.getSentence() == [(1,'hello,world.',''),]
    assert user.getStat() == [(1,2,3,5,'2013-09-12'),]
    assert user.getMeet() == [(1,1,'2013-09-12'),]
    """
    user.addKnown("time")
    user.getKnown()
    user.getNew()
    user.getExtra()
    user.getSentence()
    user.getStat()
    """
    user.db.conn.commit()
    mydb.cursor.close()
"""
tables

SOURCES  -- store books, magazine/articles, internet websites/url, movies
id
source
sourcetype
comment

SENTENCES
id
sentence
source
"""
"""
KNOWNLIST
spell
lastdate

NEWLIST
id
spell
mydef

NAMELIST  -- proper names like people, place, organization etc
id
spell
mydef

WORDMEET  -- word experience, history, story
wordid
sentid
when

WORD_STAT  -- word statistics
wordid
metcount  -- how many time I meet this word, initialized to 1
familarity  -- from 1 to 9, 9 means it is known well, not a new word any more
importance -- from 1 to 9, 1 means basic word, 10 means rarely used word, default to 5

PUBD  -- public dictionary, wordnet, for example

MYWORDNET
wordid
synanym
antagnym
simspell
simsound
"""
