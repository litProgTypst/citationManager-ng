
from pathlib import Path
import re
import yaml

import wx
import wx.grid as wxgrid

from cmTools.config import Config

from cmTools.bibLaTeXAuthors import createPersonRoleList, getPersonRole, \
  getPossiblePeopleFromName, guessAuthorBiblatex, loadAuthorBiblatex, \
  guessSurname

from cmTools.wxEditors import Colour, CitationEditor
from cmTools.wxPeopleDialogs import ChooseFieldDialog, PersonEditorDialog

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
    addFieldButton.SetBackgroundColour(Colour.yellow)
    hBoxButtons.Add(addFieldButton)

    removeFieldButton = wx.Button(self, label="Remove Field")
    removeFieldButton.Bind(wx.EVT_BUTTON, self.removeField)
    removeFieldButton.SetBackgroundColour(Colour.yellow)
    hBoxButtons.Add(removeFieldButton)

    checkPeopleButton = wx.Button(self, label="Check people")
    checkPeopleButton.Bind(wx.EVT_BUTTON, self.CheckPeople)
    checkPeopleButton.SetBackgroundColour(Colour.aqua)
    hBoxButtons.Add(checkPeopleButton)

    updateCiteKeyButton = wx.Button(self, label="Update CiteKey")
    updateCiteKeyButton.Bind(wx.EVT_BUTTON, self.updateCiteKey)
    updateCiteKeyButton.SetBackgroundColour(Colour.purple)
    hBoxButtons.Add(updateCiteKeyButton)

    downloadPdfButton = wx.Button(self, label="Download PDF")
    downloadPdfButton.Bind(wx.EVT_BUTTON, self.downloadPdf)
    downloadPdfButton.SetBackgroundColour(Colour.purple)
    hBoxButtons.Add(downloadPdfButton)

    saveButton = wx.Button(self, wx.ID_OK, label = "Save Changes")
    saveButton.SetBackgroundColour(Colour.green)
    hBoxButtons.Add(saveButton)

    cancelButton = wx.Button(self, wx.ID_CANCEL, label = "Cancel")
    cancelButton.SetBackgroundColour(Colour.red)
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

        self.citationEditor.addField(
          selectedField['biblatex'][0],
          None,
          selectedField['structure'],
          selectedField['baseType']
        )

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

        self.citationEditor.removeField(
          selectedField['biblatex'][0],
        )

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

