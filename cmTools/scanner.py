
import sys

def usage() :
  print("""
  usage: cmScan <projBase>

  arguments:
    projBase   The base LaTeX file for which to create Bibliographic entries

  options:
    -r --recheck Recheck all references (ignore known citations file)
    -v --verbose Be verbose
    -h, --help   This help text
""")
  sys.exit(1)

def cli() :
  print("Hello from the scanner!")
  cmdLineArgs = sys.argv.copy()
  cmdLineArgs.pop(0) # remove the program's path
  projBase = None
  recheck  = False
  for anArg in cmdLineArgs :
    if anArg == '-r' or anArg == '--recheck' :
      recheck = True
      continue
    if anArg == '-v' or anArg == '--verbose' :
      verbose = True
      continue
    if anArg == '-h' or anArg == '--help' :
      usage()
    projBase = anArg

  if not projBase : usage()

