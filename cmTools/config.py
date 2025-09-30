
import os
from subprocess import run
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

  config.update(args)
  if 'verbose' not in config :
    config['verbose'] = verbose

  if 'refsDir' not in config :
    die("ERROR: no references directory has been configured!")

  # THIS IS A VERY CRUDE way to check the SSHFS FUSE mounted remote
  # directory for bibLatex YAML FILES
  #
  # IT MUST be run as a shell command since anything else does not "see"
  # the FUSE mounted files.
  #
  result = run(
    f"ls {config['refsDir']}",
    shell=True, capture_output=True
  )
  files = result.stdout.decode('utf-8')
  if not files :
    print("No files found....")
    print(f"  at {config['refsDir']}")
    print("  have you mounted the remote references?")
    sys.exit(1)

  if 'entryTypeMapping' not in config :
    config['entryTypeMapping'] = {}

  if 'biblatexFieldMapping' not in config :
    config['biblatexFieldMapping'] = {}

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

