'''
Created on Nov 27, 2011

@author: Qiyuesheng
'''
import unittest
import perdictdb
import perdict
import config
import re
import sys
import nltk
import time
wn = nltk.wordnet.wordnet
from nltk.tokenize import sent_tokenize, word_tokenize
def shellcmd(cmd, whandler):
    cmdpara=cmd.split()
    if config.DEBUG: print cmdpara
    if "login" == cmdpara[0]:
        ret=login(cmd)
        if ret !="":
            whandler.user=cmdpara[1]
            whandler.pdict=perdict.Perdict(ret)
            whandler.updateTitle()
    elif "logout" == cmdpara[0]:
        ret=logout(cmd)
        whandler.user=""
        whandler.pdict=""
        whandler.updateTitle()
    elif "register" == cmdpara[0]:
        ret=register(cmd)
        if ret==0:
            whandler.user=cmdpara[1]
            whandler.pdict=cmdpara[3]
            whandler.updateTitle()
    elif "word2sent" == cmdpara[0]:
        records = whandler.pdict.word2sent(cmdpara[1])
        output = cmdpara[1]+":\n"
        for rec in records:
            typ,content,source,date=rec
            output += "type:%s, source:%s, date:%s\n %s \n"%(typ,source,date, content)
        whandler.panelRight.pageconsole.txtCtrl.SetValue(output)
    elif "allusers"  == cmdpara[0]:
        ret = allusers()
        strout="user: datafile"
        for user,dfile in ret:
            strout +="\n"+user+","+dfile
        whandler.panelRight.pageconsole.txtCtrl.SetValue(strout)
    elif "help" == cmdpara[0]:
        ret = CmdHelp()
        whandler.panelRight.pageconsole.txtCtrl.SetValue(ret)
    elif "updateFile" == cmdpara[0]:
        ret = updateFile(whandler.user,cmdpara[1])
        whandler.pdict=cmdpara[1]
    elif "findNew" == cmdpara[0]:
        findnew(whandler)
        ret = None
    elif "selectAll" == cmdpara[0]:
        whandler.panelRight.pagenew.OnSelectAll(None)
        ret = None
    elif "applyNew" == cmdpara[0]:
        whandler.panelRight.pagenew.OnApplyNew(None)
        ret = None
    elif "applyKnown" == cmdpara[0]:
        whandler.panelRight.pagenew.OnApplyKnown(None)
        ret = None
    elif "fontsize" == cmdpara[0]:
        whandler.updateFontSize(cmdpara[1])
        ret = None
    elif "sentence" ==cmdpara[0] or "sent" == cmdpara[0]:
        word = cmdpara[1]
        ret=getSentence(whandler,word)
    elif "def" ==cmdpara[0] or "definition" == cmdpara[0]:
        word = cmdpara[1]
        ret=getDefinition(whandler,word)
    elif "nextPage" == cmdpara[0]:
        ret = whandler.onNext(event=None)
    elif "prevPage" == cmdpara[0]:
        ret = whandler.onPrev(event=None)
    elif "stat" == cmdpara[0] or "statistics" == cmdpara[0]:
        ret = getStat(whandler)
    elif "clear" == cmdpara[0]:
        whandler.booktext.SetValue('')
    elif "paste" == cmdpara[0]:
        whandler.OnMyPaste(None)
    elif "open" == cmdpara[0]:
        whandler.OnOpen(None)
    elif "save" == cmdpara[0]:
        whandler.OnSave(None)
    elif "sql" == cmdpara[0]:
        ret = whandler.pdict.runSql(cmd[4:])
        whandler.panelRight.pageconsole.txtCtrl.SetValue(unicode(ret))
    else:
        whandler.panelRight.pageconsole.txtCtrl.SetValue(cmdpara[0]+" Not Known command.")    
def getStat(self):
    profile = self.pdict.profile()
    ret = "\n\
           Total  known: %6i;      new: %6i\n\n\
           today  known: %6i;      new: %6i\n\
           day-1  known: %6i;      new: %6i\n\
           day-2  known: %6i;      new: %6i\n\
           day-3  known: %6i;      new: %6i\n\
           day-4  known: %6i;      new: %6i\n\
           day-5  known: %6i;      new: %6i\n\
           day-6  known: %6i;      new: %6i\n\
           day-7  known: %6i;      new: %6i" %profile
    """(profile[0],profile[1],profile[2],profile[3],
                profile[4],profile[5],profile[6],profile[7],profile[8],profile[9],
                profile[10],profile[11],profile[12],profile[13],profile[14],profile[15],
                profile[16],profile[17])"""
    self.panelRight.pageconsole.txtCtrl.SetValue(ret)
    self.panelRight.pagestat.txtCtrl.SetValue(ret)
    
def getSentence(self,word): 
        passage=self.booktext.GetValue()
        sentences=split2sent(passage)
        word = word.lower()
        useful=[]
        for sent in sentences:
            if word in sent.lower():
                useful.append(sent)
        self.panelRight.pageconsole.txtCtrl.SetValue('\n'.join(useful))
                
def getDefinition(self, word):
        basicw=wn.morphy(word.lower())
        if basicw ==None:
            basicw=word.lower()
        definitions = self.pdict.lookupWordnet(basicw,onlyOne=False)
        self.panelRight.pageconsole.txtCtrl.SetValue(word+'\n'+'\n'.join(definitions))

def updateFile(username,newfile):
    userdb = perdictdb.Userdb()
    ret = userdb.setDictfile(username, newfile)
    return ret
def CmdHelp():
    return file(config.HELPFILE).read()
def allusers():
    userdb = perdictdb.Userdb()
    ret = userdb.getUsers()
    return ret
def register(cmd):
    cmdpara=cmd.split()
    userdb = perdictdb.Userdb()
    ret = userdb.adduser(cmdpara[1],cmdpara[2],cmdpara[3])
    return ret
def login(cmd):
    cmdpara = cmd.split()
    userdb = perdictdb.Userdb()
    ret = userdb.getDictfile(cmdpara[1],cmdpara[2])
    return ret
def logout(cmd):
    pass    
def split2page(article, limit=0):
    if limit == 0:
        limit = config.pagesize
    pages = []
    while True:
        if len(article)<limit:
            pages.append(article)
            return pages
        page =article[:limit]
        lastsent = split2sent(page)[-1]
        end = page.rfind(lastsent)
        page = article[:end]
        article = article[end:]
        pages.append(page)
        
    return pages
def split2sent(page):
    return sent_tokenize(page)
def split2word(sent):
    return word_tokenize(sent)
def findnew(self):
        strin=self.booktext.GetValue()
        nwlist=[]
        self.newwords=[]
        sents = sent_tokenize(strin)
        for sent in sents:
            wlist = word_tokenize(sent)
            for w in wlist:
                if len(w)< config.minLength:         # ignore short words
                    continue
                if re.search("\d",w):                # ignore words with digits,such as 5A, G8
                    continue
                basicw=wn.morphy(w.lower())
                if basicw ==None:
                    basicw=w.lower()
                if self.pdict.isKnown(basicw):       # ignore known words
                    continue
                if basicw in nwlist:
                    continue
                if self.pdict.isMet(basicw):
                    basicw,meaning,mettimes,familarity,weight,firstdate,lastdate=self.pdict.lookupNew(basicw)[0]
                    wordrecord=(basicw,meaning,mettimes,familarity,weight,firstdate,lastdate,sent)
                else:
                    meaning=self.pdict.lookupWordnet(basicw)
                    if meaning=='':
                        if basicw not in self.specialwords:
                            self.specialwords.append(basicw)
                        continue
                    mettimes=familarity=0
                    weight=config.NORMAL
                    firstdate=lastdate=time.strftime("%Y-%m-%d")
                    wordrecord=(basicw,meaning,mettimes,familarity,weight,firstdate,lastdate,sent)
                self.newwords.append(wordrecord)
                nwlist.append(basicw)
        mylist = self.panelRight.pagenew.list
        mylist.DeleteAllItems()
        for i in self.newwords:
            index = mylist.InsertStringItem(sys.maxint, i[0])
            mylist.SetStringItem(index, 1, i[1])
            mylist.SetStringItem(index, 2, str(i[2]))
            mylist.SetStringItem(index, 3, str(i[3]))
            mylist.SetStringItem(index, 4, str(i[4]))
class TestShell(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testName(self):
        ret=shellcmd("register xxx qysmima wyl.dat")
        print "register:", ret
        self.assertEqual(ret,1,"register failed")
        ret=shellcmd("login wyl qysmima")
        self.assertEqual(ret,"wyl.dat")
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
