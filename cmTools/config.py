
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

class Config(object) :
  def __new__(cls) :
    if not hasattr(cls, 'instance') :
      cls.instance = super(Config, cls).__new__(cls)
    return cls.instance

  def __getattr__(self, name) :
    if name not in self.config :
      print(f"Could not find {name} in the configuration!")
      self.print()
      print("Have you called `loadConfig` yet?")
      sys.exit(1)

    return self.config[name]

  def print(self) :
    print("-------------------------------------------------")
    print(yaml.dump(self.config))
    print("-------------------------------------------------")

  def loadConfig(self, args, verbose=False) :
    if 'config' not in args :
      die("No configuration file specified... can not continue")

    self.config = {}
    with open(args['config']) as confFile :
      self.config = yaml.safe_load(confFile.read())

    for aKey, aValue in args.items() :
      if aValue : self.config[aKey] = aValue

    if 'verbose' not in self.config :
      self.config['verbose'] = verbose

    if 'refsDir' not in self.config :
      die("ERROR: no references directory has been configured!")

    self.refsDir = Path(self.config['refsDir']).expanduser()
    if not any(self.refsDir.glob("**/*_*Biblatex.yaml")) :
      print("No files found....")
      print(f"  at {self.config['refsDir']}")
      print(f"  at {self.refsDir}")
      print("  have you mounted the remote references?")
      sys.exit(1)

    if 'newRefsDir' not in self.config :
      die("ERROR: no NEW references directory has been configured!")

    self.newRefsDir = Path(self.config['newRefsDir']).expanduser()
    self.newRefsDir.mkdir(parents=True, exist_ok=True)

    if 'entryTypeMapping' not in self.config :
      self.config['entryTypeMapping'] = {}

    if 'biblatexFieldMapping' not in self.config :
      self.config['biblatexFieldMapping'] = {}

    if 'width'  not in self.config : self.config['width'] = 600
    if 'height' not in self.config : self.config['height'] = 600

    if self.config['verbose'] : self.print()

