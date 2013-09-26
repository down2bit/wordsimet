#!/usr/bin/env python
#-*- coding: utf-8 -*-
# panels.py
import wx
import wx.richtext as rt
import os
import ConfigParser as configparser
import time
import config
import unittest
from myview import MyPanels
import shell
import perdict
class ViewCtrl(MyPanels):
    """Panels with splitter and sizer"""
    def __init__(self,parent=None,id=-1, title=''):
        MyPanels.__init__(self,parent,id,title)
        self.isStop = False
        self.HisContent=''
        self.RegularContent=''
        self.specialwords=[]
        self.ShowHis=False
        self.notes = ""
        
        self.logger = config.log
        user=config.user
        datafile=config.datafile
        self.pdict=perdict.Perdict(datafile)
        self.SetTitle("reader for "+user)

        self.mapEvent()

        self.Show(True)
    def mapEvent(self):
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        
        self.Bind(wx.EVT_TOOL, self.OnExit, id=self.toolExit)
        self.Bind(wx.EVT_TOOL, self.OnAbout, id=self.toolAbout)
        self.Bind(wx.EVT_TOOL, self.OnCfg, id=self.toolConfig)
        self.Bind(wx.EVT_MENU, self.OnOpen, id=self.menuOpen)
        self.Bind(wx.EVT_MENU, self.OnExit, self.menuExit)
        self.Bind(wx.EVT_MENU, self.OnAbout, self.menuAbout)
        self.Bind(wx.EVT_MENU, self.OnCfg, self.menuCfg)
        self.Bind(wx.EVT_MENU, self.OnSave, id=self.menuSave)
        self.Bind(wx.EVT_BUTTON, self.OnShell, self.CmdBtn)
        self.command.Bind(wx.EVT_KEY_DOWN,self.OnReturnKey)

    def OnShell(self,event):
        strin=self.command.GetValue()
        if len(strin.strip())==0: strin=config.defaultcmd
        if config.DEBUG: print(strin)
        shell.shellcmd(strin,self)
    def onNext(self,event=None):
        if self.page+1 < self.pagenum:
            self.page +=1
            self.booktext.SetValue(self.pages[self.page])
    def onPrev(self,event=None):
        if self.page > 0:
            self.page -= 1
            self.booktext.SetValue(self.pages[self.page])
        
    def OnCfg(self,event):
        pass

    def OnAbout(self,event):
        # A message dialog box with an OK button.
        aboutmsg="""Ver: 0.5  2013-09-19
          Features: 
            1. Load text from a txt file
            2. Send text command manually
            3. Find new words in article
            4. 
            5. 
            6. 
            
          Any suggestion? 
          Email to qi_yue_sheng@hotmail.com"""
        dlg = wx.MessageDialog(self, aboutmsg, "Welcome",wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        

        
    def OnExit(self,event):
        self.logger.close()
        #self.writeNotes()
        self.Destroy()
    def OnReturnKey(self,event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_RETURN:
            self.OnShell(event)
        else:
            event.Skip()
    def OnOpen(self,event):
        """Open a file"""
        self.dirname=""
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "","*.txt", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname,self.filename),"r")
            self.content = f.read()
            f.close()
            self.page = 0
            self.pages = shell.split2page(self.content)
            self.pagenum = len(self.pages)
            self.booktext.SetValue(self.pages[self.page])
        dlg.Destroy()

    def OnSave(self,event):
        """Save to a file"""
        pass

def main():
    app=wx.App(False) # Create a new app, don't redirect stdout/stderr to a window.
    MyPanels()
    app.MainLoop()
class mytest(unittest.TestCase):
    def testXMLcompare(self):
        app=wx.App(False)
        win = ViewCtrl()
        win.booktext.SetValue("""OpenText
What We Do

Unleashing the power of information, technologies and business solutions. Learn more about Enterprise Information Management.!""")
        win.command.SetValue("findNew")
        win.Show(True)
        win.logger.write("start main loop.")
        app.MainLoop()
if __name__=='__main__':
    unittest.main()
