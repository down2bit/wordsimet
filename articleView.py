import wx
from wx import html2

class Window(wx.Panel):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.panel = self
        print("hello")
        sizer = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.web = html2.WebView.New(self.panel)
        self.web.LoadURL("https://www.google.ca")
        hbox1.Add(self.web,  1, flag=wx.ALL|wx.EXPAND)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.command = wx.TextCtrl(self.panel)
        hbox2.Add(self.command, proportion=1, flag=wx.ALL)

        button = wx.Button(self.panel, label="panel 2")
        hbox2.Add(button, proportion=0, flag=wx.ALL)

        """input = wx.TextCtrl(panel2)
        hbox.Add(input, proportion=0)"""
        sizer.Add(hbox1, 1, flag=wx.ALL | wx.EXPAND)
        sizer.Add(hbox2, flag=wx.BOTTOM|wx.RIGHT|wx.EXPAND)
        self.panel.SetSizer(sizer)
        self.Show()


class WebFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        #box = wx.BoxSizer()
        #panel = wx.Panel(self)
        web = Window(parent=self)
        #box.Add(web)
        #panel.SetSizer(box)
        self.Show()

def main():
    app = wx.App()
    window = WebFrame(parent=None, title="No!")
    window.Show(True)
    app.MainLoop()
    print("bye")