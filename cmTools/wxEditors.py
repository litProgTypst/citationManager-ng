
import copy
from datetime import date
import yaml

import wx
import wx.propgrid as wxpg

from cmTools.config import Config

#######################################################
# Setup our colours
# see: https://rgbcolorpicker.com/
class Colour :

  red       = wx.Colour(255, 0,   0)
  green     = wx.Colour(0,   255, 0)
  blue      = wx.Colour(0,   0,   255)

  yellow    = wx.Colour(255, 255, 0)
  orange    = wx.Colour(255, 128, 0)

  purple    = wx.Colour(255, 0,   255)

  aqua      = wx.Colour(0,   255, 255)
  lightBlue = wx.Colour(0,   128, 255)

docTypes = [
  "allowed",
  "alumni",
  "owned",
  "public",
  "purchased",
  # "scanned20180621",
  # "uncatalogued",
  "unknown",
  "workingCopies"
]

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

    biblatexFields = Config().biblatexFields
    for aKey, aValue in properties.items() :
      if aKey in biblatexFields :
        selectedField = biblatexFields[aKey]
        # print(yaml.dump(selectedField))

        self.addField(
          aKey, aValue,
          selectedField['structure'],
          selectedField['baseType'],
          propertyGrid=pg
        )
      else :
        print(f"aKey = {aKey} is NOT a known biblatexField")
        print("  ignoring this key/value")

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
      self.properties[aKey] = aValue
      print(yaml.dump(self.properties))

  def getUpdatedProperties(self) :
    return self.properties

  def saveChanges(self) :
    return {}

  def addField(
    self, fieldLabel, fieldValue, fieldStructure, fieldType, propertyGrid=None
  ) :
    print(f"WORKING on: {fieldLabel} = {fieldValue} ({fieldStructure};{fieldType})")  # noqa

    # we have two types of fiedStructure :
    #  field (one time) and list (many items of the same type)
    #
    # we have five fieldType(s) :
    #  date, integer, string, docType, entrytype

    # Ensure entryType and docType are both choice of known types

    # if fieldLabel == 'entryType' :
    # elif fieldLabel == 'docType' :

    if not propertyGrid :
      propertyGrid = self.mainPropertyGrid

    if not fieldValue  :
      if fieldStructure == 'list' :
        fieldValue = []
      else :
        if fieldType == 'string' :
          fieldValue = ""
        elif fieldType == 'integer' :
          fieldValue = 0
        elif fieldType == 'date' :
          fieldValue = date.today()
        elif fieldType == 'docType' :
          fieldValue = 'unknown'
        elif fieldType == 'entrytype' :
          fieldValue = 'article'
        else :
          print(f"UNKNOWN fieldType : {fieldType}")

    if isinstance(fieldValue, list) :
      if fieldType == 'string' :
        pass
      elif fieldType == 'integer' :
        print("THERE IS NO ArrayIntegerProperty!")
      elif fieldType == 'date' :
        print("THERE IS NO ArrayDateProperty!")
      elif fieldType == 'docType' :
        print("THERE IS NO ArrayDocTypeProperty!")
      elif fieldType == 'entrytype' :
        print("THERE IS NO ArrayEntryTypeProperty!")
      else :
          print(f"UNKNOWN fieldType : {fieldType}")
      print("  using ArrayStringProperty instead")
      asp = wxpg.ArrayStringProperty(fieldLabel, value=fieldValue)
      asp.SetAttribute(wxpg.PG_ARRAY_DELIMITER, ';')
      propertyGrid.Append(asp)
    else :
      aProperty = wxpg.StringProperty(fieldLabel, value=str(fieldValue))
      if fieldType == 'string' :
        pass
      elif fieldType == 'integer' :
        aProperty = wxpg.IntProperty(fieldLabel, value=int(fieldValue))
      elif fieldType == 'date' :
        aProperty = wxpg.DateProperty(fieldLabel, value=fieldValue)
      elif fieldType == 'docType' :
        if fieldValue in docTypes :
          theChoices = wxpg.PGChoices(docTypes)
          theChoice  = theChoices.GetValuesForStrings([fieldValue])[0]
          aProperty  = wxpg.EnumProperty(
            fieldLabel, fieldType, theChoices, theChoice
          )
      elif fieldType == 'entrytype' :
        entryTypes = sorted(Config().biblatexTypes.keys())
        if fieldValue in entryTypes :
          theChoices = wxpg.PGChoices(entryTypes)
          theChoice  = theChoices.GetValuesForStrings([fieldValue])[0]
          aProperty  = wxpg.EnumProperty(
            fieldLabel, fieldType, theChoices, theChoice
          )
      else :
        print(f"UNKNOWN fieldType : {fieldType}")
      propertyGrid.Append(aProperty)
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
