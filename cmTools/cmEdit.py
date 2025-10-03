
import argparse
import copy
import sys
import yaml

import wx
import wx.propgrid as wxpg

from cmTools.config import addConfigurationArgs, loadConfig
from cmTools.bibLaTeXYaml import loadBibLatex
# from cmTools.pybtex import loadBibLaTeXFile

TODO Must use wx.___EXPAND ;-)

TODO Make AuthorTab and CitationTab subclasses of PropertyEditor AND
     override the saveChanges method.

#######################################################
# Define the generic propery grid editor
class PropertyEditor(wx.Panel) :
  def __init__(
    self, parent, properties, title,
    saveChangesObject, saveChangesCallback
  ) :
    self.properties = properties
    self.title = title
    self.saveChangesObject = saveChangesObject
    self.saveChangesCallback = saveChangesCallback
    self.changedProperties = {}
    wx.Panel.__init__(self, parent)

    self.properyGrid = pg = wxpg.PropertyGrid(self)
    pg.Bind(wxpg.EVT_PG_CHANGED, self.OnPropGridChange)

    for aKey, aValue in properties.items() :
      pg.Append(wxpg.StringProperty(aKey, value=str(aValue)))

    vBox = wx.BoxSizer(wx.VERTICAL)
    vBox.Add(wx.StaticText(self, -1, title, (20,20)))
    vBox.Add(pg)
    saveButton = wx.Button(self, label="Save changes")
    saveButton.Bind(wx.EVT_BUTTON, self.SaveChanges)
    vBox.Add(saveButton)
    self.SetSizer(vBox)

  def OnPropGridChange(self, event) :
    p = event.GetProperty()
    if p :
      aKey = p.GetName()
      aValue = p.GetValueAsString()
      if str(self.properties[aKey]) != aValue :
        self.changedProperties[aKey] = aValue

  def getUpdatedProperties(self) :
    properties = copy.deepcopy(self.properties)
    for aKey, aValue in self.changedProperties.items() :
      properties[aKey] = aValue
    return properties

  def SaveChanges(self, cmdEvt) :
    self.saveChangesCallback(
      self.saveChangesObject,
      self.getUpdatedProperties()
    )

#######################################################
# Define the structure of editing Author BibLaTeX
class AuthorTab(wx.Panel):
  def __init__(self, parent, authorKey, authorBiblatex):
    self.authorKey = authorKey
    self.authorBiblatex = authorBiblatex
    wx.Panel.__init__(self, parent)
    PropertyEditor(
      self, authorBiblatex, f"Content for the {authorKey}",
      self, self.saveChanges
    )

  def saveChanges(self, newAuthorBiblatex) :
    print("SAVING CHANGES:")
    print(yaml.dump(newAuthorBiblatex))

#######################################################
# Define the structure of editing Citation BibLaTeX
class CitationTab(wx.Panel):
  def __init__(self, parent, citationKey, citationBiblatex):
    self.citationKey = citationKey
    self.citationBiblatex = citationBiblatex
    wx.Panel.__init__(self, parent)
    PropertyEditor(
      self, citationBiblatex, f"Content for the {citationKey}",
      self, self.saveChanges
    )

  def saveChanges(self, newCitationBiblatex) :
    print("SAVING CHANGES:")
    print(yaml.dump(newCitationBiblatex))

#######################################################
# Structure the App's MainFrame
class MainFrame(wx.Frame):
  def __init__(self, config, citation, authors):
    self.config = config
    print(yaml.dump(config))
    wx.Frame.__init__(
      self, None, title="Citation Manager BibLaTeX Editor"
    )

    # Panel creation and tab holder setup:
    p = wx.Panel(self)
    nb = wx.Notebook(p)

    # Initiation of the tab windows:
    if citation :
      citTab = CitationTab(
        nb, citation['citekey'], citation
      )
      nb.AddPage(citTab, citTab.citationKey)
    for anAuthor in authors :
      authorTab = AuthorTab(
        nb, anAuthor['cleanname'], anAuthor
      )
      nb.AddPage(authorTab, authorTab.authorKey)

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
  citation, authors = loadBibLatex(config)
  if citation : print(yaml.dump(citation))
  if authors  : print(yaml.dump(authors))

  # sys.exit(1)

  app = wx.App()
  MainFrame(config, citation, authors).Show()
  app.MainLoop()

#######################################################
# Run the app if called as a main
if __name__ == "__main__":
  cli()
