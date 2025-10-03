
from pathlib import Path
import sys
import yaml

# We collect all of the methods which load/save our BibLaTeX formated YAML

def loadBibLatexYamlFile(aPath) :
  return yaml.safe_load(aPath.read_text())

def loadBibLatex(config) :
  refsDir = Path(config['refsDir']).expanduser()
  newRefsDir = Path(config['newRefsDir']).expanduser()

  bibLatexTag = Path(config['biblatexYaml']).name.split('_')[0]

  yamlFiles = []
  yamlFiles.extend(list(refsDir.rglob(f'*{bibLatexTag}_bibLatex.yaml')))
  yamlFiles.extend(list(newRefsDir.rglob(f'*{bibLatexTag}_bibLatex.yaml')))

  if not yamlFiles :
    print(f"ERROR: could not find: {bibLatexTag}")
    sys.exit(1)

  if 1 < len(yamlFiles) :
    print(f"ERROR: multiple yaml files for: {bibLatexTag}")
    sys.exit(1)

  bibLatexYaml = loadBibLatexYamlFile(yamlFiles[0])

  citation = None
  authors  = []

  if 'citationBiblatex' in bibLatexYaml :
    citation = bibLatexYaml['citationBiblatex']
  elif 'authorBiblatex' in bibLatexYaml :
    authors.append(bibLatexYaml['authorBiblatex'])

  return (citation, authors)

