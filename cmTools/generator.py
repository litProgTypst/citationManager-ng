
from glob import glob
import os
import sys
import yaml

sys.path.append(os.path.dirname(__file__))

from writeAuthorTiddlers import writeAuthorTable, \
  writeAuthorNote, writeAuthorToC
from writeCitationTiddlers import writeCitationTable, \
  writeCitationNote, writeCitationToC

os.system("reset")

oldRefsDir = os.path.expanduser(
  "~/ExpositionGit/websites/noteServer/refs"
)

# newRefsDir = os.path.expanduser(
#   "~/GitTools/tiddlywiki/wikis/references"
# )
newRefsDir = "wikis/tiddlers"

os.system(f"rm -rf {newRefsDir}")
os.system(f"mkdir -p {newRefsDir}")

authorLetters2   = set()
citationLetters2 = set()

def parseFile(aFile) :
  with open(aFile) as mdFile :
    theLines = mdFile.readlines()
    theLines.pop(0)
    yamlHeader = []
    while 0 < len(theLines) :
      aLine = theLines.pop(0)
      if aLine.startswith('---') : break
      yamlHeader.append(aLine)
  return (
    "".join(yamlHeader),
    "".join(theLines)
  )

def parseAuthor(aFile) :
  header, notes = parseFile(aFile)
  print("----------------------------")
  header = yaml.safe_load(header)

  writeAuthorTable(
    newRefsDir, header['title'], header['biblatex'], authorLetters2
  )

  writeAuthorNote(
    newRefsDir, header['title'], notes
  )

def parseCitation(aFile) :
  header, notes = parseFile(aFile)
  print("----------------------------")
  header = yaml.safe_load(header)

  writeCitationTable(
    newRefsDir,
    header['biblatex']['citekey'],
    header['biblatex'],
    citationLetters2
  )

  writeCitationNote(
    newRefsDir, header['biblatex']['citekey'], notes, header['biblatex']
  )

for aFile in glob(os.path.join(oldRefsDir, "**/*.md"), recursive=True) :
  if 'refs/author' in aFile : parseAuthor(aFile)
  elif 'refs/cite' in aFile : parseCitation(aFile)
  # else : print(f"IGNORE: {aFile}")

writeAuthorToC(newRefsDir, authorLetters2)
writeCitationToC(newRefsDir, citationLetters2)

def cli() :
  print("Hello from the generator!")
