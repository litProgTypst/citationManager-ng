
import os
from pathlib import Path
import sys
import yaml

def die(msg) :
  print(msg)
  sys.exit(1)

def addConfigurationArgs(parser) :
  parser.add_argument(
    '-c', '--config',
    help="The path to the user configuration file",
    default=os.path.expanduser('~/.config/citationManager/config.yaml')
  )
  parser.add_argument(
    '-v', '--verbose',
    help="Be verbose",
    default=False,
    action='store_true'
  )

def loadConfig(args, verbose=False) :

  if 'config' not in args :
    die("No configuration file specified... can not continue")

  config = {}
  with open(args['config']) as confFile :
    config = yaml.safe_load(confFile.read())

  for aKey, aValue in args.items() :
    if aValue : config[aKey] = aValue

  if 'verbose' not in config :
    config['verbose'] = verbose

  if 'refsDir' not in config :
    die("ERROR: no references directory has been configured!")

  refsDirPath = Path(config['refsDir']).expanduser()
  if not any(refsDirPath.glob("**/*_bibLatex.yaml")) :
    print("No files found....")
    print(f"  at {config['refsDir']}")
    print("  have you mounted the remote references?")
    sys.exit(1)

  if 'newRefsDir' not in config :
    die("ERROR: no NEW references directory has been configured!")

  Path(config['newRefsDir']).expanduser().mkdir(
    parents=True, exist_ok=True
  )

  if 'entryTypeMapping' not in config :
    config['entryTypeMapping'] = {}

  if 'biblatexFieldMapping' not in config :
    config['biblatexFieldMapping'] = {}

  if 'width'  not in config : config['width'] = 600
  if 'height' not in config : config['height'] = 600

  if config['verbose'] :
    print("-------------------------------------------------")
    print(yaml.dump(config))
    print("-------------------------------------------------")

  return config

"""

  config['recheck'] = recheck
  config['verbose'] = verbose


  if 'buildDir' not in config :
    config['buildDir'] = os.path.join('build', 'latex')

  baseFileName = os.path.join(
    config['buildDir'],
    projBase.replace(r'\\..+$','')
  )
  config['auxFile']  = baseFileName+'.aux'
  config['bblFile']  = baseFileName+'.bbl'
  config['citeFile'] = baseFileName+'.cit'
  config['bibFile']  = baseFileName+'.bib'

"""

