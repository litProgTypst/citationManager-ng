
import argparse
import copy
import sys
import yaml

import wx
import wx.propgrid as wxpg

from cmTools.config import addConfigurationArgs, Config
from cmTools.bibLaTeXYaml import loadBibLatex
from cmTools.bibLaTeXAuthors import createPersonRoleList, getPersonRole, \
  getPossiblePeopleFromName, guessAuthorBiblatex, loadAuthorBiblatex
# from cmTools.pybtex import loadBibLaTeXFile

#######################################################
# TODO

# PROVIDE wx.Property types in biblatex fields to be used by property
# editor to choose editor type for a given property.

# Add "AddFieldDialog" to add an extra field to an existing
# propertyEditor.

# Ensure entryType and docType are both choice of known types

# RATIONALIZE biblatex uses (citationBiblatex / ... )

# TEST pass **Biblatex keys through to allow for multiple variants to be
# amalgamated

# TEST Move notebook into the use of the PropertyGrid to allow editing of
# multiple variants.

# Correct getPeople in CitationEditor to collect CURRENT people rather
# than the initial list of people

# Add an updateCitationKey button which takes the given people and year
# and title and creates a trial citeKey, which can then be edited by the
# user in a dialog.

# Work on SAVING biblatex

# Add a getUrl button to download and archive a paper from its url.

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

    vBox = wx.BoxSizer(wx.VERTICAL)
    vBox.Add(hBoxLabel, proportion=2, flag=wx.EXPAND)
    vBox.Add(hBoxProps, proportion=2, flag=wx.EXPAND)
    self.SetSizer(vBox)

  def createAPropertyGrid(self, properties) :
    config = Config()
    pg = wxpg.PropertyGrid(
      self, size=wx.Size(
        int(int(config['width'])  * 0.95),
        int(int(config['height']) * 0.9)
      )
    )
    pg.Bind(wxpg.EVT_PG_CHANGED, self.OnPropGridChange)

    for aKey, aValue in properties.items() :
      self.addField(aKey, aValue, None, propertyGrid=pg)

    return pg

  def collectPropertyGrids(self) :
    self.mainPropertyGrid = self.createAPropertyGrid(
      self.properties
    )
    return self.mainPropertyGrid

  def OnPropGridChange(self, event) :
    p = event.GetProperty()
    if p :
      aKey = p.GetName()
      aValue = p.GetValueAsString()
      print(f"CHANGED {aKey} = {aValue}")
      print(yaml.dump(self.properties))
      if str(self.properties[aKey]) != aValue :
        self.changedProperties[aKey] = aValue

  def getUpdatedProperties(self) :
    properties = copy.deepcopy(self.properties)
    for aKey, aValue in self.changedProperties.items() :
      properties[aKey] = aValue
    return properties

  def saveChanges(self) :
    return {}

  def addField(self, fieldLabel, fieldValue, fieldType, propertyGrid=None) :
    if not propertyGrid :
      propertyGrid = self.mainPropertyGrid
    if isinstance(fieldValue, list) :
      asp = wxpg.ArrayStringProperty(fieldLabel, value=fieldValue)
      asp.SetAttribute(wxpg.PG_ARRAY_DELIMITER, ';')
      propertyGrid.Append(asp)
    else :
      propertyGrid.Append(
        wxpg.StringProperty(fieldLabel, value=str(fieldValue))
      )
    self.Show()

#######################################################
# Define the structure of editing Author BibLaTeX
class PersonEditor(PropertyEditor):
  def __init__(
    self, parent, personName, bibLatex
  ):
    self.personName = personName
    self.personBiblatex = bibLatex
    super().__init__(
      parent, bibLatex['authorBiblatex'],
      f"Content for the {personName}"
    )

  def collectPropertyGrids(self) :
    bibLatex = self.personBiblatex
    self.mainPropertyGrid = self.createAPropertyGrid(
      bibLatex['authorBiblatex']
    )
    if 'altAuthorBiblatex' not in bibLatex :
      return self.mainPropertyGrid

    nb = wx.Notebook(self)
    nb.AddPage(self.mainPropertyGrid, self.personName)

    for aPersonKey, aPerson in bibLatex['altAuthorBiblatex'].items() :
      aPersonPropGrid = self.createAPropertyGrid(aPerson)
      nb.AddPage(aPersonPropGrid, aPersonKey)
    return nb

  def saveChanges(self) :
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
    self.mainPropertyGrid = self.createAPropertyGrid(
      bibLatex['citationBiblatex']
    )
    if 'altCitationBiblatex' not in bibLatex :
      return self.mainPropertyGrid

    nb = wx.Notebook(self)
    nb.AddPage(self.mainPropertyGrid, self.citationKey)

    for aCiteKey, aCitation in bibLatex['altCitationBiblatex'].items() :
      aCitePropGrid = self.createAPropertyGrid(aCitation)
      nb.AddPage(aCitePropGrid, aCiteKey)
    return nb

  def saveChanges(self) :
    newCitationBiblatex = self.getUpdatedProperties()
    print("SAVING CHANGES:")
    print(yaml.dump(newCitationBiblatex))

  def getPeopleToCheck(self) :
    peopleToCheck = {}
    biblatex = self.citationBiblatex['citationBiblatex']
    peopleToCheck['author'] = copy.deepcopy(biblatex['author'])
    print(yaml.dump(peopleToCheck))
    return peopleToCheck

#######################################################
# Dialogs
#######################################################

#######################################################
# Add field dialog
class ChooseFieldDialog(wx.Dialog) :
  def __init__(self, parent, fields, taskType, gridType) :
    self.fields = fields
    self.taskType = taskType
    self.gridType = gridType
    self.selectedField = None

    wx.Dialog.__init__(
      self, parent, -1, f"{taskType} fields for {self.gridType}"
    )

    vBox = wx.BoxSizer(wx.VERTICAL)
    hBoxThings = wx.BoxSizer(wx.HORIZONTAL)

    choices = sorted(fields.keys())
    self.theChoice = wx.ListBox(
      self, choices=choices, name="Fields", style=wx.LB_SINGLE
    )
    self.theChoice.Bind(wx.EVT_LISTBOX, self.updateChoice)
    hBoxThings.Add(self.theChoice)

    self.commentPanel = wx.Panel(self)
    vBoxComment = wx.BoxSizer(wx.VERTICAL)
    self.theComment = wx.StaticText(self.commentPanel, label="")
    vBoxComment.Add(
      self.theComment, flag=wx.EXPAND | wx.ALL | wx.ALIGN_TOP, border=5
    )
    self.commentPanel.SetSizer(vBoxComment)
    hBoxThings.Add(self.commentPanel, 2, flag=wx.EXPAND)
    # hBoxThings.AddSpacer(10)
    vBox.Add(hBoxThings, 2, flag=wx.EXPAND)

    hBoxButtons = wx.BoxSizer(wx.HORIZONTAL)
    hBoxButtons.Add(wx.Button(self, wx.ID_OK, label = "Add this field"))
    hBoxButtons.Add(wx.Button(self, wx.ID_CANCEL, label = "Cancel"))
    vBox.Add(hBoxButtons)

    self.SetSizer(vBox)

  def updateChoice(self, cmdEvt) :
    self.selectedField = self.theChoice.GetString(
      self.theChoice.GetSelection()
    )
    theField = self.fields[self.selectedField]
    # see: https://rgbcolorpicker.com/
    theType = "UNUSED"
    theColor = wx.Colour(255, 149, 0, alpha=128)  # light orange
    if self.gridType in theField['optionalFor'] :
      theType = "OPTIONAL"
      theColor = wx.Colour(238, 255, 0, alpha=128)  # yellow
    elif self.gridType in theField['requiredBy'] :
      theType = "REQUIRED"
      theColor = wx.Colour(255, 15, 0, alpha=128)  # light red
    elif self.gridType in theField['usefulFor'] :
      theType = "USEFUL"
      theColor = wx.Colour(0, 178, 255, alpha=128)  # light blue
    theComment = ' '.join(theField['comment'].splitlines())
    self.theComment.SetLabel(
      f"{theType}: {theComment}"
    )
    self.theComment.SetBackgroundColour(theColor)
    self.theComment.Wrap(self.commentPanel.GetSize().GetWidth() - 10)

#######################################################
# PersonEditor dialogs
class PersonEditorDialog(wx.Dialog) :
  def __init__(
    self, parent, personName, bibLatex
  ) :
    wx.Dialog.__init__(
      self, parent, -1, personName
    )

    vBox = wx.BoxSizer(wx.VERTICAL)

    self.personEditor = PersonEditor(self, personName, bibLatex)
    hBoxEditor = wx.BoxSizer(wx.HORIZONTAL)
    hBoxEditor.Add(self.personEditor)
    vBox.Add(hBoxEditor, proportion=2, flag=wx.EXPAND)

    hBoxButtons = wx.BoxSizer(wx.HORIZONTAL)
    hBoxButtons.Add(wx.Button(self, wx.ID_OK, label = "DONE"))
    # addFieldButton = wx.Button(self, label="Add Field")
    # addFieldButton.Bind(wx.EVT_BUTTON, self.addField)
    # hBoxButtons.Add(addFieldButton)
    saveButton = wx.Button(self, label="Save changes")
    saveButton.Bind(wx.EVT_BUTTON, self.SaveChanges)
    hBoxButtons.Add(saveButton)
    vBox.Add(hBoxButtons)

    self.SetSizer(vBox)

    config = Config()
    self.SetSize(wx.Size(
      int(config['width']), int(config['height'])
    ))

  def SaveChanges(self, cmdEvt) :
    self.personEditor.saveChanges()

  # def addField(self, cmdEvt) :
  #   print("Add person field")

#######################################################
# Check a person dialog
class ChooseAPersonDialog(wx.Dialog) :
  def __init__(self, parent, personType, personName, peopleList) :
    self.personType = personType
    self.personName = personName
    self.peopleList = peopleList

    wx.Dialog.__init__(
      self, parent, -1, f"Choose a person to use as {personType}"
    )

    self.choices = []
    for aPerson in peopleList :
      self.choices.append(aPerson)

    vBox = wx.BoxSizer(wx.VERTICAL)
    hBoxList = wx.BoxSizer(wx.HORIZONTAL)
    self.listBox = wx.ListBox(
      self, choices=self.choices, style=wx.LB_SINGLE
    )
    hBoxList.Add(self.listBox)
    vBox.Add(hBoxList, 2, flag=wx.EXPAND)
    hBoxButtons = wx.BoxSizer(wx.HORIZONTAL)
    hBoxButtons.Add(wx.Button(self, wx.ID_OK, label = "DONE"))
    checkButton = wx.Button(self, -1, label="Update person")
    checkButton.Bind(wx.EVT_BUTTON, self.updatePerson)
    hBoxButtons.Add(checkButton)
    vBox.AddSpacer(10)
    vBox.Add(hBoxButtons)
    self.SetSizer(vBox)

  def updatePerson(self, cmdEvt) :
    selectionIndx = self.listBox.GetSelection()
    if -1 < selectionIndx :
      aPerson = self.choices[selectionIndx]
      personName = aPerson
      personBiblatex = {}
      if aPerson == 'new' :
        personName = self.personName
        personBiblatex = guessAuthorBiblatex(self.personName)
      else :
        personBiblatex = loadAuthorBiblatex(aPerson)
      print(f"Updating person: {aPerson}")
      with PersonEditorDialog(self, personName, personBiblatex) as dlg :
        dlg.ShowModal()

#######################################################
# Choose a person to check dialog
class ChooseAPersonToCheckDialog(wx.Dialog) :
  def __init__(self, parent, peopleDict) :
    self.peopleDict = peopleDict

    wx.Dialog.__init__(
      self, parent, -1, "Choose a person to check"
    )

    self.choices = createPersonRoleList(peopleDict)

    vBox = wx.BoxSizer(wx.VERTICAL)
    hBoxList = wx.BoxSizer(wx.HORIZONTAL)
    self.listBox = wx.ListBox(self, choices=self.choices, style=wx.LB_SINGLE)
    hBoxList.Add(self.listBox)
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
    selectionIndx = self.listBox.GetSelection()
    if -1 < selectionIndx :
      aPerson, aRole = getPersonRole(self.choices[selectionIndx])
      print(f"Checking a person: {aPerson} as {aRole}")
      peopleList = getPossiblePeopleFromName(aPerson)
      with ChooseAPersonDialog(self, aRole, aPerson, peopleList) as dlg :
        dlg.ShowModal()

#######################################################
# CitatoinEditorDialog
class CitationEditorDialog(wx.Dialog) :
  def __init__(
    self, parent, citationKey, bibLatex
  ) :
    wx.Dialog.__init__(
      self, parent, -1, citationKey
    )
    self.bibLatex = bibLatex['citationBiblatex']

    vBox = wx.BoxSizer(wx.VERTICAL)

    self.citationEditor = CitationEditor(self, citationKey, bibLatex)
    hBoxEditor = wx.BoxSizer(wx.HORIZONTAL)
    hBoxEditor.Add(self.citationEditor)
    vBox.Add(hBoxEditor, proportion=2, flag=wx.EXPAND)

    hBoxButtons = wx.BoxSizer(wx.HORIZONTAL)
    hBoxButtons.Add(wx.Button(self, wx.ID_OK, label = "DONE"))
    addFieldButton = wx.Button(self, label="Add Field")
    addFieldButton.Bind(wx.EVT_BUTTON, self.addField)
    hBoxButtons.Add(addFieldButton)
    checkPeopleButton = wx.Button(self, label="Check people")
    checkPeopleButton.Bind(wx.EVT_BUTTON, self.CheckPeople)
    hBoxButtons.Add(checkPeopleButton)
    vBox.Add(hBoxButtons)

    self.SetSizer(vBox)

    config = Config()
    self.SetSize(wx.Size(
      int(config['width']), int(config['height'])
    ))

  def CheckPeople(self, cmdEvt) :
    print("Checking people!")
    peopleToCheck = self.citationEditor.getPeopleToCheck()
    with ChooseAPersonToCheckDialog(self, peopleToCheck) as dlg :
      dlg.ShowModal()

  def addField(self, cmdEvt) :
    print("Add citation field")
    print(yaml.dump(self.bibLatex))
    with ChooseFieldDialog(
      self, Config().biblatexFields, 'Add', self.bibLatex['entrytype']
    ) as dlg :
      result = dlg.ShowModal()
      if result == wx.ID_OK :
        print(f"Adding field {dlg.selectedField}")
        selectedField = Config().biblatexFields[dlg.selectedField]
        print(yaml.dump(selectedField))

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
    vBox = wx.BoxSizer(wx.VERTICAL)
    hBoxLabel = wx.BoxSizer(wx.HORIZONTAL)
    hBoxLabel.Add(wx.StaticText(self, -1, 'Citation Editor', (20,20)))
    vBox.Add(hBoxLabel, proportion=2, flag=wx.EXPAND)
    self.SetSizer(vBox)
    self.Show()

    # Initiation of the citation or author editor dialog
    if 'citationBiblatex' in bibLatex :
      with CitationEditorDialog(
        self, bibLatex['citationBiblatex']['citekey'],
        bibLatex
      ) as dlg :
        dlg.ShowModal()
    elif 'authorBiblatex' in bibLatex :
      with PersonEditorDialog(
        self, bibLatex['authorBiblatex']['cleanname'],
        bibLatex
      ) as dlg :
        dlg.ShowModal()

    self.Close(force=True)

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

  bibLatex = loadBibLatex(config['biblatexYaml'])
  if bibLatex : print(yaml.dump(bibLatex))

  # sys.exit(1)

  app = wx.App()
  MainFrame(bibLatex).Show()
  app.MainLoop()

#######################################################
# Run the app if called as a main
if __name__ == "__main__":
  cli()
