
import argparse
import sys
import yaml

import wx

from cmTools.config import addConfigurationArgs, loadConfig
# from cmTools.pybtex import loadBibLaTeXFile


#######################################################
# Define the structure of editing Author BibLaTeX
class AuthorTab(wx.Panel):
  def __init__(self, parent, authorKey):
    self.authorKey = authorKey
    wx.Panel.__init__(self, parent)
    wx.StaticText(self, -1, f"Content for the {authorKey}", (20,20))

#######################################################
# Define the structure of editing Citation BibLaTeX
class CitationTab(wx.Panel):
  def __init__(self, parent, citationKey):
    self.citationKey = citationKey
    wx.Panel.__init__(self, parent)
    wx.StaticText(self, -1, f"Content for the {citationKey}", (20,20))

#######################################################
# Structure the App's MainFrame
class MainFrame(wx.Frame):
  def __init__(self, config):
    self.config = config
    print(yaml.dump(config))
    wx.Frame.__init__(
      self, None, title="Citation Manager BibLaTeX Editor"
    )

    # Panel creation and tab holder setup:
    p = wx.Panel(self)
    nb = wx.Notebook(p)

    # Initiation of the tab windows:
    citTab = CitationTab(nb, 'doeringIsham2008thingTheoryFoundationsPhysics')
    authorTab1 = AuthorTab(nb, 'Doering, Andreas')
    authorTab2 = AuthorTab(nb, 'Isham, Chris J')

    # Assigning names to tabs and adding them:
    nb.AddPage(citTab, citTab.citationKey)
    nb.AddPage(authorTab1, authorTab1.authorKey)
    nb.AddPage(authorTab2, authorTab2.authorKey)

    # Organizing notebook layout using a sizer:
    self.SetSize((1200,1000))
    # self.Centre()
    # self.Maximize()
    sizer = wx.BoxSizer()
    sizer.Add(nb, 1, wx.EXPAND)
    p.SetSizer(sizer)

#######################################################
# Provide the command line interface

def parseArgs() :
  parser = argparse.ArgumentParser(
    prog='cmEdit',
    description="""
      Edit a BibLaTeX YAML file to update a citation
      or authors.
    """,
    epilog='Text at the bottom of help'
  )

  addConfigurationArgs(parser)

  parser.add_argument('biblatexYaml')

  return vars(parser.parse_args())

def cli() :
  print(yaml.dump(sys.argv))
  config = loadConfig(parseArgs())
  app = wx.App()
  MainFrame(config).Show()
  app.MainLoop()

#######################################################
# Run the app if called as a main
if __name__ == "__main__":
  cli()
