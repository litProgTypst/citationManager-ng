
import argparse
import copy
import sys
import yaml

import wx
import wx.propgrid as wxpg

from cmTools.config import addConfigurationArgs, Config
from cmTools.bibLaTeXYaml import loadBibLatex
# from cmTools.pybtex import loadBibLaTeXFile

#######################################################
# TODO

# TEST a PersonPropertyEditorDialog (modal)

# Check `ui/citationManager/updateReference` for details on how to
# find/extract citation structure.

# Extract `getPossiblePeopleFromSurname` from
# `tools/cmTools/biblatexTools.py` and adapt to new tiddlers.

# TEST pass **Biblatex keys through to allow for multiple variants to be
# amalgamated

# TEST Move notebook into the use of the PropertyGrid to allow editing of
# multiple variants.

# Add a checkPeople button which walks through a series of SingleChoice
# dialogs. 1) to list all people as in citation, 2) for each person allow
# the selection of a KNOWN person OR NEW person. 3) If a new person is
# selected, create a custom modal dialog with a PersonPropertyGrid to edit
# the new person's details.

# Add an updateCitationKey button which takes the given people and year
# and title and creates a trial citeKey, which can then be edited by the
# user in a dialog.

# Add a getUrl button to download and archive a paper from its url.

# Add exit button (or make SaveChanges exit)

#######################################################
# Check people dialogs
class ChooseAPersonDialog(wx.Dialog) :
  def __init__(self, parent, personType, peopleList) :
    self.peopleList = peopleList

    wx.Dialog.__init__(
      self, parent, -1, f"Choose a person to use as {personType}"
    )

    choices = []

    for aPerson in peopleList :
      choices.append(aPerson)

    hBox = wx.BoxSizer(wx.HORIZONTAL)
    hBox.Add(wx.Choice(self, choices=choices))
    self.SetSizer(hBox)

class ChooseAPersonToCheckDialog(wx.Dialog) :
  def __init__(self, parent, peopleDict) :
    self.peopleDict = peopleDict

    wx.Dialog.__init__(
      self, parent, -1, "Choose a person to check"
    )

    choices = []
    for aPersonType, typedPeople in peopleDict.items() :
      for aPerson in typedPeople :
        choices.append(f"{aPersonType} - {aPerson}")

    vBox = wx.BoxSizer(wx.VERTICAL)
    hBoxList = wx.BoxSizer(wx.HORIZONTAL)
    hBoxList.Add(wx.ListBox(self, choices=choices, style=wx.LB_SINGLE))
    vBox.Add(hBoxList, 2, flag=wx.EXPAND)
    hBoxButtons = wx.BoxSizer(wx.HORIZONTAL)
    hBoxButtons.Add(wx.Button(self, wx.ID_OK, label = "Done"))
    checkButton = wx.Button(self, -1, label="Check Person")
    checkButton.Bind(wx.EVT_BUTTON, self.checkPerson)
    hBoxButtons.Add(checkButton)
    vBox.AddSpacer(10)
    vBox.Add(hBoxButtons)
    self.SetSizer(vBox)

  def checkPerson(self, cmdEvt) :
    print("Checking a person")


#######################################################
# Define the generic propery grid editor

class PropertyEditor(wx.Panel) :
  def __init__(
    self, parent, properties, title
  ) :
    self.properties = properties
    self.title = title
    self.changedProperties = {}
    wx.Panel.__init__(self, parent)

    hBoxLabel = wx.BoxSizer(wx.HORIZONTAL)
    hBoxLabel.Add(wx.StaticText(self, -1, title, (20,20)))

    hBoxProps = wx.BoxSizer(wx.HORIZONTAL)
    pg = self.collectPropertyGrids()
    hBoxProps.Add(pg)

    self.hBoxButtons = hBoxButtons = wx.BoxSizer(wx.HORIZONTAL)
    saveButton = wx.Button(self, label="Save changes")
    saveButton.Bind(wx.EVT_BUTTON, self.SaveChanges)
    hBoxButtons.Add(saveButton)

    self.addAdditionalButtons()

    vBox = wx.BoxSizer(wx.VERTICAL)
    vBox.Add(hBoxLabel, proportion=2, flag=wx.EXPAND)
    vBox.Add(hBoxProps, proportion=2, flag=wx.EXPAND)
    vBox.Add(hBoxButtons)
    self.SetSizer(vBox)

  def createAPropertyGrid(self, properties) :
    config = Config()
    self.properyGrid = pg = wxpg.PropertyGrid(
      self, size=wx.Size(
        int(int(config.width)  * 0.95),
        int(int(config.height) * 0.9)
      )
    )
    pg.Bind(wxpg.EVT_PG_CHANGED, self.OnPropGridChange)

    for aKey, aValue in properties.items() :
      if isinstance(aValue, list) :
        asp = wxpg.ArrayStringProperty(aKey, value=aValue)
        asp.SetAttribute(wxpg.PG_ARRAY_DELIMITER, ';')
        pg.Append(asp)
      else :
        pg.Append(wxpg.StringProperty(aKey, value=str(aValue)))

    return pg

  def collectPropertyGrids(self) :
    return self.createAPropertyGrid(self.properties)

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

  def addAdditionalButtons(self) :
    pass

#######################################################
# Define the structure of editing Author BibLaTeX
class PersonEditor(PropertyEditor):
  def __init__(
    self, parent, personName, bibLatex
  ):
    self.personName = personName
    self.personBiblatex = bibLatex
    super().__init__(
      parent, bibLatex,
      f"Content for the {personName}"
    )

  def collectPropertyGrids(self) :
    bibLatex = self.personBiblatex
    personPropGrid = self.createAPropertyGrid(
      bibLatex['authorBiblatex']
    )
    if 'altAuthorBiblatex' not in bibLatex :
      return personPropGrid

    nb = wx.Notebook(self)
    nb.AddPage(personPropGrid, self.personName)

    for aPersonKey, aPerson in bibLatex['altAuthorBiblatex'].items() :
      aPersonPropGrid = self.createAPropertyGrid(aPerson)
      nb.AddPage(aPersonPropGrid, aPersonKey)
    return nb

  def SaveChanges(self, cmdEvt) :
    newAuthorBiblatex = self.getUpdatedProperties()
    print("SAVING CHANGES:")
    print(yaml.dump(newAuthorBiblatex))

#######################################################
# Define the structure of editing Citation BibLaTeX
class CitationEditor(PropertyEditor):
  def __init__(
    self, parent, citationKey, citationBiblatex
  ):
    self.citationKey = citationKey
    self.citationBiblatex = citationBiblatex
    super().__init__(
      parent, citationBiblatex,
      f"Content for the {citationKey}"
    )

  def collectPropertyGrids(self) :
    bibLatex = self.citationBiblatex
    citationPropGrid = self.createAPropertyGrid(bibLatex['citationBiblatex'])
    if 'altCitationBiblatex' not in bibLatex :
      return citationPropGrid

    nb = wx.Notebook(self)
    nb.AddPage(citationPropGrid, self.citationKey)

    for aCiteKey, aCitation in bibLatex['altCitationBiblatex'].items() :
      aCitePropGrid = self.createAPropertyGrid(aCitation)
      nb.AddPage(aCitePropGrid, aCiteKey)
    return nb

  def SaveChanges(self, cmdEvt) :
    newCitationBiblatex = self.getUpdatedProperties()
    print("SAVING CHANGES:")
    print(yaml.dump(newCitationBiblatex))

  def addAdditionalButtons(self) :
    hBoxButtons = self.hBoxButtons
    checkPeopleButton = wx.Button(self, label="Check people")
    checkPeopleButton.Bind(wx.EVT_BUTTON, self.CheckPeople)
    hBoxButtons.Add(checkPeopleButton)

  def CheckPeople(self, cmdEvt) :
    print("Checking people!")
    peopleToCheck = {}
    biblatex = self.citationBiblatex['citationBiblatex']
    peopleToCheck['author'] = copy.deepcopy(biblatex['author'])
    print(yaml.dump(peopleToCheck))
    captcd = ChooseAPersonToCheckDialog(self, peopleToCheck)
    if captcd.ShowModal() == wx.ID_OK :
      print("DONE OK")

#######################################################
# PersonEditorDialog
class PersonEditorDialog(wx.Dialog) :
  def __init__(
    self, parent, personName, bibLatex, config
  ) :
    wx.Dialog.__init__(
      self, parent, -1, personName
    )

    pe = PersonEditor(self, personName, bibLatex, config)
    hBox = wx.BoxSizer(wx.HORIZONTAL)
    hBox.Add(pe)
    self.SetSizer(hBox)

#######################################################
# PersonEditorDialog
class CitationEditorDialog(wx.Dialog) :
  def __init__(
    self, parent, citationKey, bibLatex, config
  ) :
    wx.Dialog.__init__(
      self, parent, -1, citationKey
    )

    ce = CitationEditor(self, citationKey, bibLatex, config)
    hBox = wx.BoxSizer(wx.HORIZONTAL)
    hBox.Add(ce)
    self.SetSizer(hBox)

#######################################################
# Structure the App's MainFrame
class MainFrame(wx.Frame):
  def __init__(self, bibLatex):
    config = Config()
    config.print()
    wx.Frame.__init__(
      self, None, title="Citation Manager BibLaTeX Editor"
    )

    # Panel creation and tab holder setup:
    p = wx.Panel(self)

    # Initiation of the tab windows:
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    if 'citationBiblatex' in bibLatex :
      citationEditor = CitationEditor(
        p, bibLatex['citationBiblatex']['citekey'],
        bibLatex
      )
      sizer.Add(citationEditor, proportion=2, flag=wx.EXPAND)
    elif 'authorBiblatex' in bibLatex :
      personEditor = PersonEditor(
        p, bibLatex['authorBiblatex']['cleanname'],
        bibLatex
      )
      sizer.Add(personEditor, proportion=2, flag=wx.EXPAND)

    # Organizing notebook layout using a sizer:
    self.SetSize(wx.Size(
      int(config.width), int(config.height)
    ))
    # self.Centre()
    # self.Maximize()
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

  parser.add_argument(
    '--width',
    help="The width of the editor"
  )

  parser.add_argument(
    '--height',
    help="The height of the editor"
  )

  parser.add_argument('biblatexYaml')

  return vars(parser.parse_args())

def cli() :
  print(yaml.dump(sys.argv))
  config = Config()
  config.loadConfig(parseArgs())
  config.print()
  bibLatex = loadBibLatex(config.biblatexYaml)
  if bibLatex : print(yaml.dump(bibLatex))

  # sys.exit(1)

  app = wx.App()
  MainFrame(bibLatex).Show()
  app.MainLoop()

#######################################################
# Run the app if called as a main
if __name__ == "__main__":
  cli()
