
from pathlib import Path
import sys
import yaml

from cmTools.config import Config

# We collect all of the methods which load/save our BibLaTeX formated YAML

def loadBibLatexYamlFile(aPath) :
  return yaml.safe_load(aPath.read_text())

def loadBibLatex(biblatexToLoad) :
  config = Config()
  bibLatexTag = Path(biblatexToLoad).name.split('_')[0]

  yamlFiles = []
  yamlFiles.extend(
    list(config.refsDir.rglob(f'*{bibLatexTag}_*Biblatex.yaml'))
  )
  yamlFiles.extend(
    list(config.newRefsDir.rglob(f'*{bibLatexTag}_*Biblatex.yaml'))
  )

  if not yamlFiles :
    print(f"ERROR: could not find: {bibLatexTag}")
    sys.exit(1)

  if 1 < len(yamlFiles) :
    print(f"ERROR: multiple yaml files for: {bibLatexTag}")
    sys.exit(1)

  bibLatexYaml = loadBibLatexYamlFile(yamlFiles[0])

  return bibLatexYaml

