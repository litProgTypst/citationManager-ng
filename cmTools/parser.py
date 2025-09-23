
import argparse
import yaml

# import pybtex

from cmTools.config import addConfigurationArgs, loadConfig
from cmTools.pybtex import loadBibLaTeXFile

def parseArgs() :
  parser = argparse.ArgumentParser(
    prog='cmParse',
    description="""
      Parse a (better) BibLaTeX file to extract the citations
      and authors for our use.

      The results will be written into separate files
      one per citation or author.

      Duplicate citations with different `-X` endings will be
      amalgamated into the same citation file.
    """,
    epilog='Text at the bottom of help'
  )

  addConfigurationArgs(parser)

  parser.add_argument('bibtex')

  return vars(parser.parse_args())

def cli() :
  print("Hello from the parser!")
  config = loadConfig(parseArgs())
  bibLaTeX = loadBibLaTeXFile(config['bibtex'])
  for anEntryKey in bibLaTeX.entries :
    anEntry = bibLaTeX.entries[anEntryKey]
    print(yaml.dump(anEntry))
