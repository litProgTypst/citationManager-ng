#!.venv/bin/python

from pathlib import Path
import yaml

remoteDir = Path('remoteWiki')

for aYamlFile in remoteDir.glob("**/*_bibLatex.yaml") :
  print(f"Working on {aYamlFile}")
  theYaml = yaml.safe_load(aYamlFile.read_text())
  if 'biblatex' in theYaml :
    theBibLatex = theYaml['biblatex']
    print("  fixing")
    theYaml = { 'citationBiblatex' : theBibLatex }
    if 'cleanname' in theBibLatex :
      theYaml = { 'authorBiblatex' : theBibLatex }
    aYamlFile.write_text(yaml.dump(theYaml))

