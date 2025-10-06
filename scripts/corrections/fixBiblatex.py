#!.venv/bin/python

from pathlib import Path
import yaml

remoteDir = Path('remoteWiki')

for aYamlFile in remoteDir.glob("**/*_bibLatex.yaml") :
  print(f"Working on {aYamlFile}")
  theYaml = yaml.safe_load(aYamlFile.read_text())
  if 'citationBiblatex' in theYaml :
    print("  moving to citationBiblatex")
    newPath = str(aYamlFile).replace('bibLatex', 'citationBiblatex')
    # print("", newPath)
    aYamlFile.rename(newPath)
  elif 'authorBiblatex' in theYaml :
    print("  moving to authorBiblatex")
    newPath = str(aYamlFile).replace('bibLatex', 'authorBiblatex')
    # print("", newPath)
    aYamlFile.rename(newPath)
