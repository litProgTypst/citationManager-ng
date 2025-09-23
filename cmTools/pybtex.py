# This Python module isolates our use of the pybtex package.

# see: https://docs.pybtex.org/index.html


# import datetime
# import json
# import os
# from pathlib import Path
# import sys
# import traceback
# import yaml
#

from pybtex.database import parse_file  # type: ignore

def loadBibLaTeXFile(aPath) :
  bibLaTeX = {}
  try :
    bibLaTeX = parse_file(aPath)
  except Exception as err :
    print("Opps!")
    print(repr(err))
  return bibLaTeX

# import pybtex.style.labels.alpha
# ######################################################################
# # Alas we do the monkey-patch (yet again)
# #
# # We wrap the pybtex.style.labels.alpha.LabelStyle::format_label to report
# # which entry(citekey) is being formatted...
# old_format_label = pybtex.style.labels.alpha.LabelStyle.format_label
# def monkeyPatchedFormatLabel(self, entry) :
#   if 'citekey' in entry.fields :
#     print(f"Formatting entry: {entry.fields['citekey']}")
#   return old_format_label(self, entry)
# pybtex.style.labels.alpha.LabelStyle.format_label = monkeyPatchedFormatLabel
#
# from pybtex.style.template import FieldIsMissing
# from pybtex.database import \
#   BibliographyData, Entry, Person
# from pybtex.plugin import find_plugin
#
# from cmTools.biblatexTools import \
#   citationPathExists, loadCitation, \
#   citation2urlBase, citation2refUrl
#
# peopleBiblatexFields = [
#   'author', 'editor'
# ]
#
# privateBiblatexFields = [
#   'docType', 'creationid', 'citePath', 'docPath', 'ignoreUrl'
# ]
#
# def normalizeBiblatex(biblatex) :
#   if 'year' in biblatex :
#     biblatex['year'] = str(biblatex['year'])
#   biblatexKeys = list(biblatex.keys())
#   for aKey in biblatexKeys :
#     if biblatex[aKey] is None :
#       biblatex.pop(aKey, None)
#       continue
#     if isinstance(biblatex[aKey], datetime.date) :
#       #print("OOPS!", aCiteId, aKey, biblatex[aKey], str(biblatex[aKey]))
#       biblatex[aKey] = biblatex[aKey].strftime("%Y-%m-%d")
#
#   fields2delete = set()
#   for aPrivateField in privateBiblatexFields :
#     if aPrivateField in biblatex :
#       fields2delete.add(aPrivateField)
#   for aField, aValue in biblatex.items() :
#     if isinstance(aValue, list) :
#       if aField in peopleBiblatexFields : continue
#       fields2delete.add(aField)
#     elif isinstance(aValue, int) :
#       biblatex[aField] = str(aValue)
#   for aField in fields2delete :
#     del biblatex[aField]
#
#   return biblatex
#
# typeOfPeople = ['author', 'editor']
#
# def writeBrokenBBLFile() :
#   try:
#     with open(config['bblFile'],'w') as bblFile :
#       bblFile.write("""
#
#   % something went wrong trying to format the bibliography
#   \\par\\noindent\\fbox{cmScan failed to create the bibliography}
#   """)
#   except Exception as err :
#     print("Could not write document's bbl file.")
#     sys.exit(2)
#
# def cli() :
#   config = loadConfig()
#
#   knownCitations = {}
#   missingCitations = set()
#   if config['recheck'] :
#     print(f"Rechecking all citations (ignoring the {config['citeFile']} file)")  # noqa
#   else :
#     try :
#       with open(config['citeFile']) as citeFile :
#         citationData = json.loads(citeFile.read())
#         if 'knownCitations' in citationData :
#           knownCitations = citationData['knownCitations']
#         if 'missingCitations' in citationData :
#           missingCitations = set(citationData['missingCitations'])
#     except FileNotFoundError as err :
#       print(f"Initializing {config['citeFile']} for the first time")
#     except Exception as err :
#       print(f"ERROR: Oops something went wrong...")
#       print(repr(err))
#       print(f"(re)Initializing {config['citeFile']} for the first time")
#
#   print("")
#   newCitations = set()
#   anAuxFilePath = config['auxFile']
#   print(f"scanning: {anAuxFilePath}")
#   try:
#     with open(anAuxFilePath) as auxFile :
#       for aLine in auxFile.readlines() :
#         if aLine.find('\\citation') < 0 : continue
#         aCiteId = aLine.replace('\\citation{','').strip().strip('}')
#         if aCiteId in knownCitations : continue
#         if aCiteId in missingCitations : continue
#         newCitations.add(aCiteId)
#   except Exception as err :
#     print(f"Could not open the document's aux file")
#     print(f"  {anAuxFilePath}")
#     print( "There is nothing more we can do...")
#     writeBrokenBBLFile()
#     return
#
#   citations2load = set()
#   citations2load = citations2load.union(missingCitations, newCitations)
#
#   print("")
#   for aCiteId in sorted(list(citations2load)) :
#     print(f"looking for citation: {aCiteId}")
#
#     if not citationPathExists(aCiteId, refsDir=config['refsDir']) :
#       print(f"ERROR: the citation {aCiteId} could not be found!")
#       missingCitations.add(aCiteId)
#       continue
#
#     citeDict, citeBody = loadCitation(aCiteId, refsDir=config['refsDir'])
#     rawBiblatex  = citeDict['biblatex']
#     biblatex     = {}
#     fieldMapping = config['biblatexFieldMapping']
#     for aField, aValue in rawBiblatex.items() :
#       if aField in fieldMapping :
#         aField = fieldMapping[aField]
#       biblatex[aField] = aValue
#     knownCitations[aCiteId] = biblatex
#     newCitations.add(aCiteId)
#     if aCiteId in missingCitations :
#       missingCitations.remove(aCiteId)
#
#   print("")
#   if not newCitations or (len(knownCitations) < 1) :
#     print("no new citations... nothing more to do!")
#     return
#   else :
#     print("new citations found...")
#
#   bibData    = BibliographyData()
#   theCiteIds = sorted(list(knownCitations.keys()))
#   for aCiteId in theCiteIds :
#     biblatex  = normalizeBiblatex(knownCitations[aCiteId])
#     entryType = biblatex['entrytype']
#     if entryType in config['entryTypeMapping'] :
#       entryType = config['entryTypeMapping'][entryType]
#     theEntry  = Entry(entryType, fields=biblatex)
#     for aPersonType in typeOfPeople :
#       if aPersonType in biblatex :
#         for aPerson in biblatex[aPersonType] :
#           theEntry.add_person(Person(aPerson), aPersonType)
#     bibData.add_entry(aCiteId, theEntry)
#
#   print("")
#
#   ####################################################################
#   # USING pybtex to write a bbl file...
#   #
#   # see pybtex documentation:
#   # https://docs.pybtex.org/api/styles.html#pybtex.style.formatting.BaseStyle
#   # and the code in:
#   #   pybtex.__init__.py class PybtexEngine::format_from_files
#   #
#
#   # get the style class...
#   styleCls = find_plugin('pybtex.style.formatting', 'alpha')
#
#   # initialize a style instance...
#   style    = styleCls(
#     label_style='alpha',
#     name_style='lastfirst',
#     sorting_style='author_year_title',
#     #abbreviated_names=abbreviatedNames,
#     min_crossrefs=2
#   )
#
#   # format the bibliography...
#   try :
#     formattedBibliography = \
#       style.format_bibliography(bibData, theCiteIds)
#   except FieldIsMissing as err :
#     citeKey = err.args[0].split().pop()
#     print("------------------------------------------")
#     print( "While trying to format the citation")
#     print(f"    {citeKey}")
#     print(f"  the '{err.field_name}' field was missing.")
#     print( "  Check the")
#     print(f"    get_{bibData.entries._dict[citeKey.lower()].type}_template")
#     print( "  method in the")
#     print( "    .venv/lib/python3.11/site-packages/pybtex/style/formatting/unsrt.py")  # noqa
#     print( "  file for more details of which fields are expected.")
#     print("------------------------------------------")
#     writeBrokenBBLFile()
#     return
#   except Exception as err :
#     print("While trying to format the Bibliography...")
#     print(f"ERROR: {repr(err)}")
#     print("------------------------------------------")
#     print(yaml.dump(theCiteIds))
#     print("------------------------------------------")
#     print(yaml.dump(bibData))
#     print("------------------------------------------")
#     print(traceback.format_exc())
#     writeBrokenBBLFile()
#     return
#
#   # get the 'latex' pybtex backend...
#   outputBackend = find_plugin('pybtex.backends', 'latex')
#
#   # write out the bbl file...
#   print("\nWriting out the BBL file")
#   outputBackend('UTF-8').write_to_file(
#     formattedBibliography,
#     config['bblFile']
#   )
#
#   # write out the citation data for the next run...
#   print("Writing out the CIT file")
#   with open(config['citeFile'], 'w') as citeFile :
#     citeFile.write(json.dumps({
#       'knownCitations'   : knownCitations,
#       'missingCitations' : sorted(list(missingCitations))
#     }))
#
#   # write out a "synthetized" .bib file
#   print("Writing out the BIB file")
#   with open(config['bibFile'], 'w') as bibFile :
#     for aKey, aCiteData in bibData.entries.items() :
#       print(f"  writing out: {aKey}")
#       for aPersonRole in peopleBiblatexFields :
#         if aPersonRole in aCiteData.fields :
#           del aCiteData.fields[aPersonRole]
#       #print(yaml.dump(aCiteData))
#       bibFile.write(aCiteData.to_string("bibtex"))
#       bibFile.write("\n")
#
