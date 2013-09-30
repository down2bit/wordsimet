#!/usr/bin/env python
#-*- coding: utf-8 -*-
# gui.py
import wx
import wx.richtext as rt
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
import unittest
import config
import os
import sys
log = config.log
LIGHT_GREY= config.LIGHT_GREY

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)
class PageHelp(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent)
        log.write("help:"+str(self.Size)+' '+str(parent.Size))
        self.SetBackgroundColour(LIGHT_GREY)
        self.helpText = open(config.HELPFILE).read()
        txtCtrl=wx.StaticText(self,-1, self.helpText)
        #txtCtrl.SetBackgroundColour(LIGHT_GREY)
class PageConsole(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.txtCtrl=rt.RichTextCtrl(self,-1,style=rt.RE_MULTILINE|rt.RE_READONLY)
        self.txtCtrl.SetBackgroundColour(LIGHT_GREY)
        vbox = wx.BoxSizer()
        vbox.Add(self.txtCtrl,1,wx.EXPAND)
        self.SetSizer(vbox)
        self.txtCtrl.SetValue("output of command goes here.")
class PageStat(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.txtCtrl=rt.RichTextCtrl(self,-1,style=rt.RE_MULTILINE|rt.RE_READONLY)
        self.txtCtrl.SetBackgroundColour(LIGHT_GREY)
        vbox = wx.BoxSizer()
        vbox.Add(self.txtCtrl,1,wx.EXPAND)
        self.SetSizer(vbox)
        self.txtCtrl.SetValue("statistics and profile.")
class PageConfig(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.txtCtrl=rt.RichTextCtrl(self,-1,style=rt.RE_MULTILINE|rt.RE_READONLY)
        self.txtCtrl.SetBackgroundColour(LIGHT_GREY)
        vbox = wx.BoxSizer()
        vbox.Add(self.txtCtrl,1,wx.EXPAND)
        self.SetSizer(vbox)
        self.txtCtrl.SetValue("""
        Configuration:
        
        background colour: light grey
        text colour: black
        text size: 12
        new word: bold/underline
        
        times to learn every new word: 7
        maximum of new words per page: 10
        maximum of new words per day: 50
        
        """)
        print "cfg size:", self.txtCtrl.Size
class PageNewwords(wx.Panel):
    def __init__(self,parent,mainframe):
        wx.Panel.__init__(self,parent)
        self.mainframe=mainframe
        bigbox=wx.BoxSizer()
        bigpanel=wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        panelList = wx.Panel(bigpanel)
        panelBtn = wx.Panel(bigpanel,-1,size=(-1,10))
         
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        btnSelect=wx.Button(panelBtn,-1,"SelectAll")
        btnKnown=wx.Button(panelBtn,-1,"Known")
        btnWeight=wx.Button(panelBtn,-1,"DontCare")
        btnSave=wx.Button(panelBtn,-1,"Save")
        hbox.Add((20,-1))
        hbox.Add(btnSelect,0,wx.TOP,3)
        hbox.Add(btnKnown,0,wx.TOP,3)
        hbox.Add(btnWeight,0,wx.TOP,3)
        hbox.Add(btnSave,0,wx.TOP,3)
        panelBtn.SetSizer(hbox)
        self.Bind(wx.EVT_BUTTON, self.OnSelectAll, btnSelect)
        self.Bind(wx.EVT_BUTTON, self.OnApplyKnown, btnKnown)
        self.Bind(wx.EVT_BUTTON, self.OnApplyIgnore, btnWeight)
        self.Bind(wx.EVT_BUTTON, self.OnApplyNew, btnSave)
        
        
        lbox=wx.BoxSizer(wx.VERTICAL)
        self.list = CheckListCtrl(panelList)
        self.list.SetBackgroundColour(LIGHT_GREY)
        self.list.InsertColumn(0, 'word', width=100)
        self.list.InsertColumn(1, 'meaning',width=200)
        self.list.InsertColumn(2, 'M', width=20)
        self.list.InsertColumn(3, 'F',width=20)
        self.list.InsertColumn(4, 'W',width=20)
        
        self.list.DeleteAllItems()

        for i in mainframe.newwords:
            index = self.list.InsertStringItem(sys.maxint, i[3])
            self.list.SetStringItem(index, 4, str(i[4]))
            self.list.SetStringItem(index, 3, str(i[3]))
            self.list.SetStringItem(index, 2, str(i[2]))
            self.list.SetStringItem(index, 1, str(i[1]))
            self.list.SetStringItem(index, 0, str(i[0]))
        lbox.Add(self.list,1,wx.EXPAND)
        panelList.SetSizer(lbox)    

        #vbox.Add(self.list, 1, wx.EXPAND | wx.TOP, 3)
        #vbox.Add((-1,20))
        vbox.Add(panelList, 1, wx.EXPAND, 3)
        vbox.Add(panelBtn, proportion=0,  flag=0, border=30)
        #vbox.Add((-1, 10))
        bigpanel.SetSizer(vbox)
        bigbox.Add(bigpanel,1, wx.EXPAND)
        self.SetSizer(bigbox)
    def OnSelectAll(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            self.list.CheckItem(i)

    def OnDeselectAll(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            self.list.CheckItem(i, False)

    def OnApplyNew(self, event):
        num = self.list.GetItemCount()
        goodwords=[]
        for idx in range(num):
            
            if self.list.IsChecked(idx):
                
                goodwords.append(self.mainframe.newwords[idx])
        article1Page=self.mainframe.booktext.GetValue() 
        self.mainframe.pdict.saveNew(goodwords,article1Page)
    def OnApplyKnown(self, event):
        """1. save the words in tablewordknown;
        2. delete the words from tablewordnew
        3. delete the words from the new word list """
        num = self.list.GetItemCount()
        newwords=[]
        for idx in range(num):
            spell=self.list.GetItem(idx,0).GetText()
            meaning=self.list.GetItem(idx,1).GetText()
            metCount=int(self.list.GetItem(idx,2).GetText())
            familarity=int(self.list.GetItem(idx,3).GetText())
            weight=int(self.list.GetItem(idx,4).GetText())
            firstdate=self.mainframe.newwords[idx][5]
            lastdate=self.mainframe.newwords[idx][6]
            if self.list.IsChecked(idx):
                if self.mainframe.pdict.isMet(spell):
                    self.mainframe.pdict.deleteNew(spell)
                    #"todo: what about the firstdate?"
                self.mainframe.pdict.addKnown(spell,meaning,metCount,familarity,weight,firstdate,lastdate)
            else: #the word is really new
                newwords.append(self.mainframe.newwords[idx])
        self.mainframe.pdict.db.commit()
        self.newwords=newwords
        
        #self.refreshList()
        self.list.DeleteAllItems()
        for i in self.newwords:
            index = self.list.InsertStringItem(sys.maxint, i[0])
            self.list.SetStringItem(index, 4, str(i[4]))
            self.list.SetStringItem(index, 3, str(i[3]))
            self.list.SetStringItem(index, 2, str(i[2]))
            self.list.SetStringItem(index, 1, str(i[1]))
            self.list.SetStringItem(index, 0, str(i[0]))
    def OnApplyIgnore(self, event):
        num = self.list.GetItemCount()
        self.goodwords=[]
        for idx in range(num):
            if self.list.IsChecked(idx):
                self.list.SetStringItem(idx,4,str(config.IGNORE))
                rec=self.newwords[idx]
                self.newwords[idx]=rec[:4]+(config.IGNORE,)+rec[5:]
        #todo: delete these checked words from the list

class PanelRight(wx.Panel):
    def __init__(self,parent,mainframe):
        wx.Panel.__init__(self,parent)
        self.mainframe = mainframe
        nb=wx.Notebook(self)
        self.pagenew=PageNewwords(nb,mainframe)
        self.pagehelp = PageHelp(nb)
        self.pageconsole=PageConsole(nb)
        self.pagestat = PageStat(nb)
        self.pagecfg = PageConfig(nb)
        nb.AddPage(self.pagenew,"NewWords")
        nb.AddPage(self.pagehelp,"Help")
        nb.AddPage(self.pageconsole,"Console")
        nb.AddPage(self.pagestat,"Statistics")
        nb.AddPage(self.pagecfg,"Config")
        print "pagesize:", self.pagecfg.Size
        
        sizer=wx.BoxSizer()
        sizer.Add(nb,1,wx.EXPAND)
        self.SetSizer(sizer)
        print "pagesize2:", self.pagecfg.Size
        print "cfg size2:", self.pagecfg.txtCtrl.Size

class MyPanels(wx.Frame):
    def __init__(self, parent=None, id=-1, title=''):
        wx.Frame.__init__(self, parent, id, title, size=(1200,800))
        self.CreateStatusBar() # a status bar in the bottom 
        self.CreateMenu()
        self.splitter = wx.SplitterWindow(self,-1)
        #self.CreateRightPanel()
        self.newwords=[]        
        self.panelRight = PanelRight(self.splitter, self)
        self.CreateLeftPanel()
        self.CreateMyToolbar()
        self.splitter.SplitVertically(self.panelLeft,self.panelRight,sashPosition=900)
    def CreateMyToolbar(self):
        path=config.get_main_dir()
        exitfile=os.path.join(path,'img','exit.png')
        configfile=os.path.join(path,'img','config.png')
        aboutfile=os.path.join(path,'img','about.png')
        toolbar = self.CreateToolBar()
        self.toolExit=wx.NewId()
        self.toolConfig=wx.NewId()
        self.toolAbout=wx.NewId()
        toolbar.AddLabelTool(self.toolExit, 'Exit', wx.Bitmap(os.path.join(path,'img','exit.png')))
        toolbar.AddLabelTool(self.toolConfig, 'Config', wx.Bitmap(os.path.join(path,'img','config.png')))
        toolbar.AddLabelTool(self.toolAbout, 'About', wx.Bitmap(os.path.join(path,'img','about.png')))
        toolbar.Realize()
        
        
    def CreateLeftPanel(self):
        vboxMsg = wx.BoxSizer(wx.VERTICAL)
        self.panelLeft = wx.Panel(self.splitter, -1)
        splitterLeft = wx.SplitterWindow(self.panelLeft,-1)
        self.booktext = rt.RichTextCtrl(splitterLeft,style=wx.TE_MULTILINE)
        self.booktext.SetBackgroundColour(LIGHT_GREY)
        self.page = 0
        self.pagenum = 0
        self.pages = ['']
        self.content = ''
        self.fontsize=config.fontsize
        self.booktext.BeginFontSize(self.fontsize)
        panelCmd = wx.Panel(splitterLeft, -1,size=(-1,10))
        splitterLeft.SplitHorizontally(self.booktext,panelCmd,sashPosition=-60)
        #panelMsgsend.SetSize((-1,10))
        vboxMsg.Add(self.booktext, 0, wx.EXPAND)
        vboxMsg.Add(splitterLeft, 1, wx.EXPAND)
        #vboxMsg.Add(panelCmd, 0, wx.EXPAND)  # without adding explicitly, panelCmd fill the gap
        self.panelLeft.SetSizer(vboxMsg)

        #msgTitle.SetForegroundColour('RED')
        
        hboxCmd = wx.BoxSizer(wx.HORIZONTAL)
        
        self.command = wx.TextCtrl(panelCmd,-1,style=wx.TE_MULTILINE)
        self.CmdBtn = wx.Button(panelCmd,-1,"Run",size=(40,-1))
        
        hboxCmd.Add(self.command,1,wx.EXPAND)
        hboxCmd.Add(self.CmdBtn,0,wx.EXPAND)
        panelCmd.SetSizer(hboxCmd)
        
    def CreateMenu(self):
        # Setting up the menu
        filemenu = wx.Menu()
        self.menuOpen = wx.NewId()
        filemenu.Append(self.menuOpen, "&Open","Open a file")
        
        self.menuSave = wx.NewId()
        filemenu.Append(self.menuSave, "&Save", "Save to a file")
        filemenu.AppendSeparator()
        #wx.ID_ABOUT and wx.ID_EXIT are standard IDs by wxWidgets.
        self.menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", "Terminate the program")

        helpmenu = wx.Menu()
        self.menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About", "Information about the program")
        helpmenu.AppendSeparator()
        
        cfgmenu = wx.Menu()
        self.menuCfg = cfgmenu.Append(wx.ID_ANY,"&Config","Setting IP,Port ...")
        #Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(cfgmenu, "Config")
        menuBar.Append(helpmenu, "&Help")
        #menuBar.Enable(menuOpen,False)
        #menuBar.Enable(menuSave,False)
        self.SetMenuBar(menuBar) # Adding the menuBar to the Frame content.

    def updateFontSize(self, updown):
        if updown=="up":
            self.fontsize+=1
            if self.fontsize>config.MAXFONT:
                self.fontsize = config.MAXFONT
        elif updown == "down":
            self.fontsize -=1
            if self.fontsize<config.MINFONT:
                self.fontsize = config.MINFONT
        strin=self.booktext.GetValue()
        self.booktext.SetValue("")
        #self.msglog.EndFontSize()
        self.booktext.BeginFontSize(self.fontsize)
        self.booktext.SetValue(strin)
        #self.msglog.EndFontSize()
def main():
    app=wx.App(False) # Create a new app, don't redirect stdout/stderr to a window.
    MyPanels()
    app.MainLoop()
class mytest(unittest.TestCase):
    def testXMLcompare(self):
        app=wx.App(False)
        win = MyPanels()
        win.Show(True)
        app.MainLoop()
if __name__=='__main__':
    unittest.main()
