
from pathlib import Path

# We collect all of the methods which load/save Authors using our BibLaTeX
# formated YAML

# def getPersonRole(anAuthorRole) :
#   aRole = 'unknown'
#   anAuthor = anAuthorRole
#   if -1 < anAuthorRole.find(':') :
#     theParts = anAuthorRole.split(':')
#     aRole = theParts[0].strip()
#     anAuthor = theParts[1].strip()
#   return (anAuthor, aRole)
#
# def normalizeAuthor(anAuthorRole) :
#   anAuthor, aRole = getPersonRole(anAuthorRole)
#   authorDict = {
#     'cleanname' : anAuthor,
#     'surname'   : '',
#     'firstname' : '',
#     'von'       : '',
#     'jr'        : '',
#     'email'     : '',
#     'institute' : '',
#     'url'       : []
#   }
#
#   # Guess the parts of an author
#   if ',' in anAuthor :
#     nameParts = anAuthor.split(',')
#     if nameParts :
#       surname = nameParts[0].strip()
#       surname, vonPart, jrPart = expandSurname(surname)
#       firstname = ""
#       if 1 < len(nameParts) :
#         firstname = nameParts[1].replace('.', ' ').strip()
#   else :
#     surname = guessSurname(anAuthor)
#     firstname = anAuthor.replace(surname, '').strip()
#     vonPart = ''
#     jrPart = ''
#
#   cleanName = f" {vonPart} {surname} {jrPart}, {firstname}"
#   cleanName = removeMultipleSpaces.sub(" ", cleanName)
#   cleanName = removeSpacesBeforeComma.sub(",", cleanName)
#   cleanName = cleanName.strip()
#   authorDict['cleanname'] = cleanName
#   authorDict['surname']   = surname
#   authorDict['firstname'] = firstname
#   authorDict['von']       = vonPart
#   authorDict['jr']        = jrPart
#
#   return authorDict

# def guessSurname(aPerson) :
#   surname = None
#   if ',' in aPerson :
#     surname = aPerson.split(',')[0]
#   else :
#     surname = aPerson.split()[-1]
#   return surname

def expandSurname(surname) :
  surnameParts = surname.split()
  vonPart = ""
  jrPart  = ""
  if surnameParts and 1 < len(surnameParts) :
    if 0 < len(surnameParts) : vonPart = surnameParts.pop(0)
    if 0 < len(surnameParts) : surname = surnameParts.pop(0)
    if 0 < len(surnameParts) : jrPart  = surnameParts.pop(0)
  return (surname, vonPart, jrPart)

def getPossiblePeopleFromSurname(surname) :
  surname, vonPart, jrPart = expandSurname(surname)
  print(f"Searching for author: [{surname}] ({vonPart}) ({jrPart})")
  authorDir = Path('author')
  possibleAuthors = []
  for anAuthor in authorDir.glob(f'*/*{surname}*') :
    anAuthor = str(anAuthor.name).removesuffix('.md')
    possibleAuthors.append(anAuthor)
  possibleAuthors.append("new")
  possibleAuthors.sort()
  return possibleAuthors

