#!/usr/bin/env python

from pathlib import Path
import yaml

remoteDir = Path('remoteWiki')

for aYamlFile in remoteDir.glob("**/*_bibLatex.yaml") :
  print(f"Working on {aYamlFile}")
  theYaml = yaml.safe_load(aYamlFile.read_text())
  if 'biblatex' not in theYaml :
    print("  fixing")
    theYaml = { 'biblatex' : theYaml }
    aYamlFile.write_text(yaml.dump(theYaml))

