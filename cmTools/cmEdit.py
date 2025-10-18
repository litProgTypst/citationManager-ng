
import argparse
import sys
import yaml

import wx

from cmTools.config import addConfigurationArgs, Config
from cmTools.bibLaTeXYaml import loadBibLatex
from cmTools.wxDialogs import PersonEditorDialog, CitationEditorDialog

#######################################################
# TODO

# Add "AddFieldDialog" to add an extra field to an existing
# propertyEditor.

# Ensure entryType and docType are both choice of known types

# TEST wx.Property types in biblatex fields to be used by property
# editor to choose editor type for a given property.

# RATIONALIZE biblatex uses (citationBiblatex / ... )

# TEST pass **Biblatex keys through to allow for multiple variants to be
# amalgamated

# TEST Move notebook into the use of the PropertyGrid to allow editing of
# multiple variants.

# COMPLETE/TEST Correct getPeople in CitationEditor to collect CURRENT
# people rather than the initial list of people

# COMPLETE/TEST Add an updateCitationKey button which takes the given
# people and year and title and creates a trial citeKey, which can then be
# edited by the user in a dialog.

# COMPLETE/TEST Add a getUrl button to download and archive a paper from
# its url.

# Work on SAVING biblatex

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
