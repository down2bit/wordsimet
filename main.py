# high level design
# 2013-09-10
# article split into pages
# page split into sentences
# sentence split into words, at this time, phrases are not considered.
# word is formalized: walks, walking and walked all become walk
import data
import config
import myview
import sys
import wx
def getinput():
    return "what a wonderful world."


def dealarticle(article):
    pages = split2page(article)
    for page in pages:
        dealpage(page)


def split2page(article):
    return []


def dealpage(page):
    sentences = split2sent(page)
    for sent in sentences:
        dealsent(sent)


def split2sent(page):
    return []


def dealsent(sent):
    global currSntnc
    currSntnc = sent
    words = split2word(sent)
    for w in words:
        dealword(w, currSntnc)


def split2word(sent):
    return []


def dealword(word, sntnc):
    """Save the word in database if it is somewhat new.
    Formalize it first, if it is not in public dictionary, it is likely a proper Name.
    If it is known alreay, do nothing;
    If it is the first time to be seen (not in WORDLIST),
        insert records into WORDLIST, SENTENCES, WORD_EXPE, WORD_STAT
    If it is seen before but not known quite well (in WORDLIST and WORD_STAT but familarity<9)
        insert records into SENTENCES, WORD_EXPE, update WORD_STAT
    """
    if len(word) <= config.IGNORE_LEN:
        return
    formw=formalize(word)
    if isKnown(formw):
        return
    if not inDict(formw):  # extra words are processed manually, not automatically
        return
    if isMet(formw):
        addSentence(sntnc)
        addExperience(formw,sntnc)
        updateStat(formw)
    if isNew(formw):
        if isProperName(formw):
            addProperName(formw)
        else: # formw is in public dictionary
            addWord(formw)
            addSentence(sntnc)
            addExperience(formw, sntnc)


def isProperName(word):
    return False


def addProperName(word, note = ''):
    return

def addExperience(word, sentence):
    """ wordID, sentID, metDate"""

def addWord(word):
    """ Stat set to 1"""
    return


def addSentence(sntnc):
    """ Every sentence has an ID """
    return


def updateStat(word):
    """ Stat increase 1
    if Stat> config.MET_NUM_TO_KNOWN (10), """
    return


def formalize(word):
    return ''

def isKnown(word):
    return False


def isNew(word):
    return False


def isMet(word):
    return False


def inDict(word):
    return False


def main(argv):
    print(argv[0])
    app = wx.App(False)
    win = myview.MyPanels()
    win.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    main(sys.argv)
