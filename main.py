# high level design
# 2013-09-10
# article split into pages
# page split into sentences
# sentence split into words, at this time, phrases are not considered.
# word is formalized: walks, walking and walked all become walk
import data
def getinput():
    return "what a wonderful world."
def dealarticle(article):
    pages = split2page(article)
    for page in pages:
        dealpage(page)
    
def dealpage(page):
    sentences = split2sent(page)
    for sent in sentences:
        dealsent(sent)

def dealsent(sent):
    global currSntnc
    currSntnc = sent
    words = split2word(sent)
    for w in words:
        dealword(w, currSntnc)

def dealword(word, sntnc):
    """Save the word in database if it is somewhat new.
    Formalize it first, if it is not in public dictionary, it is likely a proper Name.
    If it is known alreay, do nothing;
    If it is the first time to be seen (not in WORDLIST),
        insert records into WORDLIST, SENTENCES, WORD_EXPE, WORD_STAT
    If it is seen before but not known quite well (in WORDLIST and WORD_STAT but familarity<9)
        insert records into SENTENCES, WORD_EXPE, update WORD_STAT
    """
    formw=formalize(word)
    if isKnown(formw):
        return
    if not isPublic(formw):  # extra words are processed manually, not automatically
        return
    if isMet(formw):
        addSntnc(sntnc)
        addExperience(formw,sntnc)
        updateStat(formw)
    if isNew(formw):
        if isName(formw):
            addName(formw)
        else: # formw is not public dictionar
            addWord(formw)
            addSntnc(sntnc)
            addExperience(formw, sntnc)
            addStat(formw)
article = getinput()
dealarticle(article)
x
