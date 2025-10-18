

import wx

from cmTools.config import Config
from cmTools.wxEditors import PersonEditor, Colour

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
    theColor = Colour.orange
    if self.gridType in theField['optionalFor'] :
      theType = "OPTIONAL"
      theColor = Colour.yellow
    elif self.gridType in theField['requiredBy'] :
      theType = "REQUIRED"
      theColor = Colour.red
    elif self.gridType in theField['usefulFor'] :
      theType = "USEFUL"
      theColor = Colour.lightBlue
    theComment = ' '.join(theField['comment'].splitlines())
    theFieldType = f"{theType}--{theField['structure']}--{theField['type']}--{theField['baseType']}"  # noqa
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
    saveButton.SetBackgroundColour(Colour.green)
    hBoxButtons.Add(saveButton)

    doneButton = wx.Button(self, wx.ID_OK, label = "Done")
    doneButton.SetBackgroundColour(Colour.red)
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


