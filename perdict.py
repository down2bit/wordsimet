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
from datetime import timedelta, date
import nltk
import config
log = config.log
wn = nltk.wordnet.wordnet

firstX_file="./Dictionary/first10k.txt"
userfile="./user.dat"
        
class Perdict():
    def __init__(self,dicfile):
        self.dictfile=dicfile
        self.db=sqlite3.connect(dicfile)
        self.cursor=self.db.cursor()
        self.known=[]
        # if dicfile is not a file, create the file
        # if the size is 0, create table
        self.createTable()
        self.populateFirst(level=80)
        self.getFirstX()
    def getFirstX(self):
        filein=open(firstX_file)
        words=filein.read().split("\n")
        self.known=words
    def populateFirst(self,level=30):
        self.cursor.execute("select count(*) from TableWordKnown")
        num=self.cursor.next()[0]
        if num>level*100: return
        global firstX_file
        filein=file(firstX_file)
        wordin=filein.read().split("\n")
        print len(wordin),"total first 3k"
        for w in wordin:
            if "###" in w:
                continue
            if self.isKnown(w.strip()):
                continue
            self.addKnown(w.strip())
            #print w.strip(),
        self.db.commit()
    def isKnown(self,word):
        if word in self.known:
            return True
        rows=self.lookupKnown(word)
        if len(rows)>0:
            return True
        else:
            return False
    def isMet(self,word):
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
    def addSent(self, sent):
        log.write("addSend:"+sent)
        self.cursor.execute("""insert into TableMnemonic(type,content,source,date) values (?,?,?,?)""", 
                            ("sent",sent,"", time.strftime("%Y-%m-%d")))
    def addRef(self,wordid,refid):
        self.cursor.execute("""insert into TableRef(wordid,refid) values(?,?)""", (wordid,refid))
    def word2sent(self,word):
        self.cursor.execute("select rowid from TableWordNew where spell=?",(word.lower(),))
        wordid = self.cursor.next()[0]
        self.cursor.execute("select refid from TableRef where wordid =?",(wordid,))
        reflist = self.cursor.fetchall()
        sents=[]
        for refid in reflist:
            self.cursor.execute("select * from TableMnemonic where rowid = ?",(refid[0],))
            sents.append(self.cursor.next())
        return sents
    def deleteNew(self,word):
        log.write("deleteNew:"+word)
        self.cursor.execute("delete from TableWordNew where spell=?",(word,))
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
        for word in wordlist:
            spell,meaning,metCount,familarity,weight,firstdate,lastdate,sent=word
            if self.isMet(spell):
                self.updateNew(spell,metCount,familarity,weight)
                self.cursor.execute("select rowid from TableWordNew where spell=?",(spell,))
                wordid=self.cursor.fetchall()
                if len(wordid)==0: continue
                wordid = wordid[0][0]
            else:
                self.addNew(spell,meaning,metCount,familarity,weight,firstdate,lastdate)
                wordid = self.getlastrowid()
            self.addSent(sent)
            sentid = self.getlastrowid()
            self.addRef(wordid, sentid)
        self.db.commit()
    def getlastrowid(self):
        self.cursor.execute("select last_insert_rowid()")
        return self.cursor.next()[0]
    def runSql(self,sql):
        self.cursor.execute(sql)
        ret = ''
        if "select" in sql.lower():
            ret = self.cursor.fetchall()
        return ret
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
        create table if not exists TableMnemonic
        (
   type text, 
   content text,
   source text,
   date text)
        """)
        self.cursor.execute("""
        create table if not exists TableRef (
    wordid integer, 
    refid integer)
        """)
    def lookupKnown(self,word):
        self.cursor.execute("select * from TableWordKnown where spell=?",(word,))
    
        return self.cursor.fetchmany()
    def lookupNew(self,word):
        self.cursor.execute("select * from TableWordNew where spell=?",(word,))
    
        return self.cursor.fetchmany()
    def getToday(self):
        self.cursor.execute("""select spell, definition,firstdate,lastdate from TableWordNew where firstdate=?""",(time.strftime("%Y-%m-%d"),))
        return self.cursor.fetchall()
    def lookupWordnet(self,word,onlyOne=True):
        syns=wn.synsets(word)
        if len(syns)>0:
            if onlyOne:
                return syns[0].definition
            else:
                return (' '.join((str(i+1),syn.definition)) for (i,syn) in enumerate(syns))
        else:
            return ""
    def profile(self):
        self.cursor.execute("""select count(*) from TableWordKnown""")
        knownTotal= self.cursor.fetchone()[0]
        self.cursor.execute("""select count(*) from TableWordNew""")
        newTotal= self.cursor.fetchone()[0]
        day_0=date.today().strftime("%Y-%m-%d")
        day_1=(date.today()-timedelta(1)).strftime("%Y-%m-%d")
        day_2=(date.today()-timedelta(2)).strftime("%Y-%m-%d")
        day_3=(date.today()-timedelta(3)).strftime("%Y-%m-%d")
        day_4=(date.today()-timedelta(4)).strftime("%Y-%m-%d")
        day_5=(date.today()-timedelta(5)).strftime("%Y-%m-%d")
        day_6=(date.today()-timedelta(6)).strftime("%Y-%m-%d")
        day_7=(date.today()-timedelta(7)).strftime("%Y-%m-%d")
        self.cursor.execute("""select count(*) from TableWordKnown where lastdate=?""",(day_0,))
        knownToday= self.cursor.fetchone()[0]
        self.cursor.execute("""select count(*) from TableWordNew where firstdate=?""",(day_0,))
        newToday= self.cursor.fetchone()[0]
        self.cursor.execute("""select count(*) from TableWordKnown where lastdate=?""",(day_1,))
        known1= self.cursor.fetchone()[0]
        self.cursor.execute("""select count(*) from TableWordNew where firstdate=?""",(day_1,))
        new1= self.cursor.fetchone()[0]
        self.cursor.execute("""select count(*) from TableWordKnown where lastdate=?""",(day_2,))
        known2= self.cursor.fetchone()[0]
        self.cursor.execute("""select count(*) from TableWordNew where firstdate=?""",(day_2,))
        new2= self.cursor.fetchone()[0]
        self.cursor.execute("""select count(*) from TableWordKnown where lastdate=?""",(day_3,))
        known3= self.cursor.fetchone()[0]
        self.cursor.execute("""select count(*) from TableWordNew where firstdate=?""",(day_3,))
        new3= self.cursor.fetchone()[0]
        self.cursor.execute("""select count(*) from TableWordKnown where lastdate=?""",(day_4,))
        known4= self.cursor.fetchone()[0]
        self.cursor.execute("""select count(*) from TableWordNew where firstdate=?""",(day_4,))
        new4= self.cursor.fetchone()[0]
        self.cursor.execute("""select count(*) from TableWordKnown where lastdate=?""",(day_5,))
        known5= self.cursor.fetchone()[0]
        self.cursor.execute("""select count(*) from TableWordNew where firstdate=?""",(day_5,))
        new5= self.cursor.fetchone()[0]
        self.cursor.execute("""select count(*) from TableWordKnown where lastdate=?""",(day_6,))
        known6= self.cursor.fetchone()[0]
        self.cursor.execute("""select count(*) from TableWordNew where firstdate=?""",(day_6,))
        new6= self.cursor.fetchone()[0]
        self.cursor.execute("""select count(*) from TableWordKnown where lastdate=?""",(day_7,))
        known7= self.cursor.fetchone()[0]
        self.cursor.execute("""select count(*) from TableWordNew where firstdate=?""",(day_7,))
        new7= self.cursor.fetchone()[0]
        return (knownTotal, newTotal,knownToday, newToday, known1,new1, known2,new2, known3,new3,
                known4,new4, known5,new5, known6,new6, known7,new7)
    def close(self):
        self.db.close()
class User():
    def __init__(self,username=""):
        self.username = username
def main():
    mypdict=Perdict("./Perdict/qiys.dic")
    rows=mypdict.lookupWordnet("example",onlyOne=False)
    print("example:")
    for r in rows:
        print( r )
    print( "number of words in perdict\n(known,new):%s" %(str(mypdict.profile())))
    rows=mypdict.getToday()
    for r in rows:
        print r
    mypdict.close()
def test():
    mypdict=Perdict("./Perdict/qiys.dic")
    mypdict.runSql("select * from TableWordNew where firstdate = '2013-10-14' ")
    for r in mypdict.cursor.fetchall():
        print r
if __name__=="__main__":
    test()
    print "Check your dict."
