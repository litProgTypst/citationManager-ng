
import re
from cmTools.config import Config
from cmTools.bibLaTeXYaml import loadBibLatexYamlFile, saveBiblatexYaml

# We collect all of the methods which load/save Authors using our BibLaTeX
# formated YAML

removeStrangeChars      = re.compile(r"[\'\",\.\{\} \t\n\r]+")
removeMultipleDashes    = re.compile(r"\-+")
removeLeadingDashes     = re.compile(r"^\-+")
removeTrailingDashes    = re.compile(r"\-+$")
removeMultipleSpaces    = re.compile(r"\s+")
removeSpacesBeforeComma = re.compile(r"\s+\,")

def author2tiddlerPath(authorName) :
  authorFileName = authorName[:]  # (makes a *copy*)
  authorFileName = removeStrangeChars.sub('-', authorFileName)
  authorFileName = removeMultipleDashes.sub('-', authorFileName)
  authorFileName = removeLeadingDashes.sub('', authorFileName)
  authorFileName = removeTrailingDashes.sub('', authorFileName)
  refsDir = Config().refsDir
  return refsDir / f"{authorFileName}_authorBiblatex.yaml"

def createPersonRoleList(aPeopleRoleDict) :
    choices = []
    for aPersonType, typedPeople in aPeopleRoleDict.items() :
      for aPerson in typedPeople :
        choices.append(f"{aPersonType} | {aPerson}")
    return choices

def getPersonRole(aPersonRole) :
  aRole = 'unknown'
  aPerson = aPersonRole
  if -1 < aPersonRole.find('|') :
    theParts = aPersonRole.split('|')
    aRole = theParts[0].strip()
    aPerson = theParts[1].strip()
  return (aPerson, aRole)

def guessSurname(aPerson) :
  surname = None
  if ',' in aPerson :
    surname = aPerson.split(',')[0]
  else :
    surname = aPerson.split()[-1]
  return surname

def expandSurname(surname) :
  surnameParts = surname.split()
  vonPart = ""
  jrPart  = ""
  if surnameParts and 1 < len(surnameParts) :
    if 0 < len(surnameParts) : vonPart = surnameParts.pop(0)
    if 0 < len(surnameParts) : surname = surnameParts.pop(0)
    if 0 < len(surnameParts) : jrPart  = surnameParts.pop(0)
  return (surname, vonPart, jrPart)

def getPossiblePeopleFromName(aName) :
  surname = guessSurname(aName)
  surname, vonPart, jrPart = expandSurname(surname)
  print(f"Searching for author: [{surname}] ({vonPart}) ({jrPart})")
  refsDir = Config().refsDir
  possibleAuthors = []
  for anAuthor in refsDir.glob(f'*{surname}*_authorBiblatex.yaml') :
    anAuthor = str(anAuthor.name).removesuffix('_authorBiblatex.yaml')
    possibleAuthors.append(anAuthor)
  possibleAuthors.append("new")
  possibleAuthors.sort()
  return possibleAuthors

def guessAuthorBiblatex(anAuthor) :
  # anAuthor, aRole = getPersonRole(anAuthorRole)
  authorDict = {
    'cleanname' : anAuthor,
    'surname'   : '',
    'firstname' : '',
    'von'       : '',
    'jr'        : '',
    'email'     : '',
    'institute' : '',
    'url'       : []
  }

  # Guess the parts of an author
  if ',' in anAuthor :
    nameParts = anAuthor.split(',')
    if nameParts :
      surname = nameParts[0].strip()
      surname, vonPart, jrPart = expandSurname(surname)
      firstname = ""
      if 1 < len(nameParts) :
        firstname = nameParts[1].replace('.', ' ').strip()
  else :
    surname = guessSurname(anAuthor)
    firstname = anAuthor.replace(surname, '').strip()
    vonPart = ''
    jrPart = ''

  cleanName = f" {vonPart} {surname} {jrPart}, {firstname}"
  cleanName = removeMultipleSpaces.sub(" ", cleanName)
  cleanName = removeSpacesBeforeComma.sub(",", cleanName)
  cleanName = cleanName.strip()
  authorDict['cleanname'] = cleanName
  authorDict['surname']   = surname
  authorDict['firstname'] = firstname
  authorDict['von']       = vonPart
  authorDict['jr']        = jrPart

  return { 'authorBiblatex': authorDict }

def loadAuthorBiblatex(anAuthor) :
  refsDir = Config().refsDir
  aPath = refsDir / f'{anAuthor}_authorBiblatex.yaml'
  return loadBibLatexYamlFile(aPath)

def saveAuthorBiblatex(authorBiblatex) :
  authorPath = author2tiddlerPath(authorBiblatex['cleanname'])
  saveBiblatexYaml(authorPath, authorBiblatex)

