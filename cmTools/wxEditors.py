
import copy
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
