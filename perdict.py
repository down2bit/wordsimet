"""
  table 
"""
todo={
    "writing":("diary,blog,", "code"),
    "reading":("time","national geography"),
    "listening":("cbc",),
    "surfing":(),
    "collecting":(),
    "physical exercise":("juggling"),
    "research":("mathematics","language","philosophy","religion"),
    "works":("software")
   }
#Not to do list
nottodo=[
    "pes",
    "bridge",
    "chess"
   ]
import sqlite3
import time
import nltk
import config
log = config.log
wn = nltk.wordnet.wordnet

first3k_file="./Dictionary/first3k.txt"
userfile="./user.dat"
        
class Perdict():
    def __init__(self,dicfile):
        self.dictfile=dicfile
        self.db=sqlite3.connect(dicfile)
        self.cursor=self.db.cursor()
        # if dicfile is not a file, create the file
        # if the size is 0, create table
        self.createTable()
        self.populateFirst(level=15)
    def populateFirst(self,level=15):
        self.cursor.execute("select count(*) from TableWordKnown")
        num=self.cursor.next()[0]
        if num>level*100: return
        global first3k_file
        filein=file(first3k_file)
        wordin=filein.read().split("\n")
        print len(wordin),"total first 3k"
        for w in wordin:
            if "###" in w:
                continue
            if self.isKnown(w.strip()):
                continue
            self.addKnown(w.strip())
            print w.strip(),
        self.db.commit()
    def isKnown(self,word):
        rows=self.lookupKnown(word)
        if len(rows)>0:
            return True
        else:
            return False
    def isMet(self,word):
        log.write("is Met "+word)
        rows=self.lookupNew(word)
        for r in rows: log.write(r)
        if len(rows)>0:
            return True
        else:
            return False
    def addKnown(self,word,meaning='',metCount=0,familarity=5,weight=5,firstdate=time.strftime("%Y-%m-%d"),lastdate= time.strftime("%Y-%m-%d")):
        
        if self.isKnown(word): 
            print word," is in your database already. Don't added again."
            return
        self.cursor.execute("""insert into TableWordKnown values (?,?,?,?,?,?,?)""", 
                            (word,meaning,metCount, familarity,weight, firstdate, lastdate))
        self.db.commit()
    def becomeKnown(self,word):
        self.cursor.execute("select * from TableWordNew where spell=?",(word,))
        (word,meaning,metCount, familarity,weight, firstdate, lastdate)=self.cursor.fetchone()
        self.addKnown(word,meaning,metCount,familarity,weight,firstdate,lastdate)
        self.cursor.execute("delete from TableWordNew where spell=?",(word,))
    def addNew(self,word,meaning='',metTimes=1, familarity=1,importance=5,firstdate=time.strftime("%Y-%m-%d"), lastdate=time.strftime("%Y-%m-%d")):
        log.write("addNew:"+word)
        self.cursor.execute("""insert into TableWordNew values (?,?,?,?,?,?,?)""", 
                            (word,meaning,metTimes, familarity,importance, firstdate, lastdate))
        self.db.commit()
    def updateNew(self,word,metCount,familarity,weight):
        log.write("updateNew:"+word)
        today=time.strftime("%Y-%m-%d")
        self.cursor.execute("select lastdate from TableWordNew where spell=?",(word,))
        lday=self.cursor.next()[0]
        if config.changeInOneDay or lday != today:
            metCount += 1
            familarity +=1
        if familarity > config.knownLimit:
            self.becomeKnown(word)
        else:
            self.cursor.execute("""update TableWordNew set metTimes=?,familarity=?,lastdate=? where spell=?""", 
                            (metCount,familarity,today,word) )
        self.db.commit()
    def saveNew(self,wordlist,article=""):
        if False: #article !="":
            for word in wordlist:
                #todo: sentence = self.findsentence(word, article)
                if self.isMet(word):
                    self.updateNew(word)
                else:
                    meaning = self.lookupWordnet(word)
                    self.addNew(word, meaning)
        else:
            for word in wordlist:
                spell,meaning,metCount,familarity,weight,firstdate,lastdate=word
                if self.isMet(spell):
                    self.updateNew(spell,metCount,familarity,weight)
                else:
                    self.addNew(spell,meaning,metCount,familarity,weight,firstdate,lastdate)
        self.db.commit()
    def createTable(self):
        self.cursor.execute("""create table if not exists pdict (word text, meaning text, sentence text, date text)""")
        self.cursor.execute("""
        create table if not exists TableWordKnown 
        (
   spell text,
   definition text, 
   metTimes integer,
   familarity integer,
   importance integer,
   firstdate text,
   lastdate text)
        """)
        self.cursor.execute("""
        create table if not exists TableWordNew 
        (
   spell text,
   definition text, 
   metTimes integer,
   familarity integer,
   importance integer,
   firstdate text,
   lastdate text)
        """)
        self.cursor.execute("""
        create table if not exists TableMnemoric
        (
   id text,
   type text, 
   content text,
   source text,
   date text)
        """)
        self.cursor.execute("""
        create table if not exists TableRef (
    word text, 
    reflist text)
        """)
    def lookupKnown(self,word):
        self.cursor.execute("select * from TableWordKnown where spell=?",(word,))
    
        return self.cursor.fetchmany()
    def lookupNew(self,word):
        self.cursor.execute("select * from TableWordNew where spell=?",(word,))
    
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
class User():
    def __init__(self,username=""):
        self.username = username
def main():
    mypdict=perdict("./Perdict/qiys.dic")
    rows=mypdict.lookup("example")
    for r in rows:
        print r
    print "number of words in perdict:",mypdict.profile()
    rows=mypdict.getToday()
    for r in rows:
        print r
    mypdict.close()
if __name__=="__main__":
    main()
    print "Check your dict."
