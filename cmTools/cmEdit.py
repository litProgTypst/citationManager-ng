
import argparse
import copy
from pathlib import Path
import re
import sys
import yaml

import wx
import wx.grid as wxgrid
import wx.propgrid as wxpg

from cmTools.config import addConfigurationArgs, Config
from cmTools.bibLaTeXYaml import loadBibLatex
from cmTools.bibLaTeXAuthors import createPersonRoleList, getPersonRole, \
  getPossiblePeopleFromName, guessAuthorBiblatex, loadAuthorBiblatex, \
  guessSurname
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
# Setup our colours
# see: https://rgbcolorpicker.com/

redColour       = wx.Colour(255, 0,   0)
greenColour     = wx.Colour(0,   255, 0)
blueColour      = wx.Colour(0,   0,   255)

yellowColour    = wx.Colour(255, 255, 0)
orangeColour    = wx.Colour(255, 128, 0)

purpleColour    = wx.Colour(255, 0,   255)

aquaColour      = wx.Colour(0,   255, 255)
lightBlueColour = wx.Colour(0,   128, 255)

#######################################################
# Define the generic propery grid editor

class PropertyEditor(wx.Panel) :
  def __init__(
    self, parent, properties, title
  ) :
    self.properties = properties
    self.title = title
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
      self.properties[aKey] = aValue

  def getUpdatedProperties(self) :
    return self.properties

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

  def removeField(self, fieldLabel, propertyGrid=None) :
    if not propertyGrid :
      propertyGrid = self.mainPropertyGrid
    propertyGrid.RemoveProperty(fieldLabel)
    self.Show()

#######################################################
# Define the structure of editing Author BibLaTeX
class PersonEditor(PropertyEditor):
  def __init__(
    self, parent, personName, bibLatex
  ):
    self.personName = personName
    self.personBiblatex = bibLatex
    self.origPersonBiblatex = copy.deepcopy(bibLatex)

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
    self.origCitationBiblatex = copy.deepcopy(citationBiblatex)

    super().__init__(
      parent, citationBiblatex['citationBiblatex'],
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
# Choose URL Dialog

# ADD a textCtrl which will be used as THE url to download and add a
# choose selected button to transfer the selected url to this text ctrl.

# ADD File chooser dialog for archiving local PDF files

class ArchivePDFDialog(wx.Dialog) :
  def __init__(self, parent, urls, citeKey) :
    self.urls         = urls
    self.citeKey      = citeKey
    self.selectedPath = None
    self.selectedUrl  = None

    wx.Dialog.__init__(self, parent, -1, f"Download PDF for {citeKey}")

    vBox = wx.BoxSizer(wx.VERTICAL)

    self.theChoice = wx.ListBox(
      self, choices=urls, name="urls", style=wx.LB_SINGLE
    )
    vBox.Add(self.theChoice, 2, wx.EXPAND)

    hBoxButtons = wx.BoxSizer(wx.HORIZONTAL)
    selectUrlButton = wx.Button(
      self, wx.ID_OK, label = "Download selected PDF"
    )
    selectUrlButton.Bind(wx.EVT_BUTTON, self.selectUrl)
    hBoxButtons.Add(selectUrlButton)
    selectFileButton = wx.Button(self, -1, label="Archive local file")
    selectFileButton.Bind(wx.EVT_BUTTON, self.selectFile)
    hBoxButtons.Add(selectFileButton)
    hBoxButtons.Add(wx.Button(self, wx.ID_CANCEL, label = "Cancel"))
    vBox.Add(hBoxButtons)

    self.SetSizer(vBox)

  def selectUrl(self, cmdEvt) :
    print(f"Select URL ({wx.ID_OK})")
    self.selectedUrl = self.theChoice.GetString(
      self.theChoice.GetSelection()
    )
    self.EndModal(wx.ID_OK)

  def selectFile(self, cmdEvt) :
    print("Select File (2)")
    with wx.FileDialog(
      self, "Archive a local PDF file",
      defaultDir=str(Path(Config()['pdfDir']).expanduser()),
      wildcard="PDF files (*.pdf)|*.pdf",
      style=wx.FD_SAVE
    ) as dlg :
      if dlg.ShowModal() == wx.ID_OK :
        self.selectedPath = dlg.GetPath()
        print(f"Select file: {self.selectedPath}")
    self.EndModal(2)

#######################################################
# Choose cite key dialog
specialChars = re.compile(r'[^a-zA-Z0-9 ]')

def camelCase(thePhrase) :
  thePhrase = specialChars.sub('', thePhrase)
  thePhrase = thePhrase.title()
  return thePhrase[0].lower() + thePhrase.replace(' ', '')[1:]

class UpdateCiteKeyDialog(wx.Dialog) :
  def __init__(self, parent, authors, year, title) :
    print("UpdateCiteKeyDialog")
    self.authors = authors
    print(yaml.dump(authors))
    self.year    = year
    self.title   = title

    wx.Dialog.__init__(self, parent, -1, f"Update citeKey for {title}")

    vBox = wx.BoxSizer(wx.VERTICAL)

    self.grid = grid = wxgrid.Grid(self)
    grid.CreateGrid(3,1)
    grid.SetColLabelValue(0, "")
    grid.SetColLabelSize(5)

    authorSurnames = []
    for anAuthor in authors :
      authorSurnames.append(guessSurname(anAuthor))
    authorSurnames = ' '.join(authorSurnames)

    grid.SetRowLabelValue(0, "Authors")
    grid.SetCellValue(0,0, camelCase(authorSurnames))

    grid.SetRowLabelValue(1, "Year")
    grid.SetCellValue(1,0, year)

    grid.SetRowLabelValue(2, "Title")
    grid.SetCellValue(2,0, camelCase(title))

    grid.AutoSize()

    vBox.Add(grid, 1, wx.EXPAND)

    hBoxButtons = wx.BoxSizer(wx.HORIZONTAL)
    hBoxButtons.Add(wx.Button(
      self, wx.ID_OK, label = "Update citeKey")
    )
    hBoxButtons.Add(wx.Button(self, wx.ID_CANCEL, label = "Cancel"))
    vBox.Add(hBoxButtons)

    self.SetSizer(vBox)
    self.Fit()

  def getCiteKey(self) :
    citeKey = []
    citeKey.append(self.grid.GetCellValue(0,0))
    citeKey.append(self.grid.GetCellValue(1,0))
    citeKey.append(self.grid.GetCellValue(2,0))
    return ''.join(citeKey)

#######################################################
# Choose field dialog
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
    hBoxButtons.Add(wx.Button(
      self, wx.ID_OK, label = f"{taskType} this field")
    )
    hBoxButtons.Add(wx.Button(self, wx.ID_CANCEL, label = "Cancel"))
    vBox.Add(hBoxButtons)

    self.SetSizer(vBox)

  def updateChoice(self, cmdEvt) :
    self.selectedField = self.theChoice.GetString(
      self.theChoice.GetSelection()
    )
    theField = self.fields[self.selectedField]
    theType = "UNUSED"
    theColor = orangeColour
    if self.gridType in theField['optionalFor'] :
      theType = "OPTIONAL"
      theColor = yellowColour
    elif self.gridType in theField['requiredBy'] :
      theType = "REQUIRED"
      theColor = redColour
    elif self.gridType in theField['usefulFor'] :
      theType = "USEFUL"
      theColor = lightBlueColour
    theComment = ' '.join(theField['comment'].splitlines())
    theFieldType = f"{theType}--{theField['structure']}--{theField['type']}"
    self.theComment.SetLabel(
      f"{theComment}\t[{theFieldType}]"
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
    saveButton = wx.Button(self, label="Save changes")
    saveButton.Bind(wx.EVT_BUTTON, self.SaveChanges)
    saveButton.SetBackgroundColour(greenColour)
    hBoxButtons.Add(saveButton)

    doneButton = wx.Button(self, wx.ID_OK, label = "Done")
    doneButton.SetBackgroundColour(redColour)
    hBoxButtons.Add(doneButton)
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

    checkButton = wx.Button(self, -1, label="Update person")
    checkButton.Bind(wx.EVT_BUTTON, self.updatePerson)
    hBoxButtons.Add(checkButton)

    doneButton = wx.Button(self, wx.ID_OK, label = "DONE")
    hBoxButtons.Add(doneButton)

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

    addFieldButton = wx.Button(self, label="Add Field")
    addFieldButton.Bind(wx.EVT_BUTTON, self.addField)
    addFieldButton.SetBackgroundColour(yellowColour)
    hBoxButtons.Add(addFieldButton)

    removeFieldButton = wx.Button(self, label="Remove Field")
    removeFieldButton.Bind(wx.EVT_BUTTON, self.removeField)
    removeFieldButton.SetBackgroundColour(yellowColour)
    hBoxButtons.Add(removeFieldButton)

    checkPeopleButton = wx.Button(self, label="Check people")
    checkPeopleButton.Bind(wx.EVT_BUTTON, self.CheckPeople)
    checkPeopleButton.SetBackgroundColour(aquaColour)
    hBoxButtons.Add(checkPeopleButton)

    updateCiteKeyButton = wx.Button(self, label="Update CiteKey")
    updateCiteKeyButton.Bind(wx.EVT_BUTTON, self.updateCiteKey)
    updateCiteKeyButton.SetBackgroundColour(purpleColour)
    hBoxButtons.Add(updateCiteKeyButton)

    downloadPdfButton = wx.Button(self, label="Download PDF")
    downloadPdfButton.Bind(wx.EVT_BUTTON, self.downloadPdf)
    downloadPdfButton.SetBackgroundColour(purpleColour)
    hBoxButtons.Add(downloadPdfButton)

    saveButton = wx.Button(self, wx.ID_OK, label = "Save Changes")
    saveButton.SetBackgroundColour(greenColour)
    hBoxButtons.Add(saveButton)

    cancelButton = wx.Button(self, wx.ID_CANCEL, label = "Cancel")
    cancelButton.SetBackgroundColour(redColour)
    hBoxButtons.Add(cancelButton)
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
    with ChooseFieldDialog(
      self, Config().biblatexFields, 'Add', self.bibLatex['entrytype']
    ) as dlg :
      result = dlg.ShowModal()
      if result == wx.ID_OK :
        print(f"Adding field {dlg.selectedField}")
        selectedField = Config().biblatexFields[dlg.selectedField]
        print(yaml.dump(selectedField))

  def removeField(self, cmdEvt) :
    print("Remove citation field")
    with ChooseFieldDialog(
      self, Config().biblatexFields, 'Remove', self.bibLatex['entrytype']
    ) as dlg :
      result = dlg.ShowModal()
      if result == wx.ID_OK :
        print(f"Removing field {dlg.selectedField}")
        selectedField = Config().biblatexFields[dlg.selectedField]
        print(yaml.dump(selectedField))

  def updateCiteKey(self, cmdEvt) :
    print("Update citeKey")
    authors = self.bibLatex['author']
    year    = self.bibLatex['year']
    title   = self.bibLatex['title']
    with UpdateCiteKeyDialog(self, authors, year, title) as dlg :
      if dlg.ShowModal() == wx.ID_OK :
        print(dlg.getCiteKey())

  def downloadPdf(self, cmdEvt) :
    print("Download PDF")
    urls = []
    if 'url' in self.bibLatex :
      urls = self.bibLatex['url']
    if urls :
      citeKey = self.bibLatex['citekey']
      with ArchivePDFDialog(self, urls, citeKey) as dlg :
        result = dlg.ShowModal()
        print(f"download PDF: {result}")
        print(dlg.selectedUrl)
        print(dlg.selectedPath)
        if result == wx.ID_OK and dlg.selectedUrl :
          print(f"selected url: {dlg.selectedUrl}")
        elif result == 2 and dlg.selectedPath :
          print(f"selected path: {dlg.selectedPath}")

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
